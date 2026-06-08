const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "handoff mesh preserves slab windows through zalloc summaries" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_rows = slab.kmallocArray(3, 16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_rows) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const known_window = slab_rows[0..16];
    const fallback_window = slab_rows[16..32];
    const mesh_window = slab_rows[32..48];

    const known = str_error_r.strErrorR(12, known_window);
    const fallback = str_error_r.strErrorR(5151, fallback_window);

    try std.testing.expectEqualStrings("Cannot allocate", known);
    try std.testing.expectEqualStrings("INTERNAL ERROR:", fallback);
    try std.testing.expectEqual(@as(u8, 0), known_window[15]);
    try std.testing.expectEqual(@as(u8, 0), fallback_window[15]);

    const mesh_written = vsprintf.scnprintf(mesh_window, "{s}:{s}:{d}", .{
        known[0..3],
        fallback[0..3],
        slab.kmalloc_nr_allocated,
    });
    try std.testing.expectEqual(@as(usize, 9), mesh_written);
    try std.testing.expectEqualStrings("Can:INT:1", mesh_window[0..mesh_written]);
    try std.testing.expectEqual(@as(u8, 0), mesh_window[mesh_written]);

    var summary: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &summary);
    for (summary.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const padded_written = vsprintf.scnprintfPad(summary.?, summary.?.len - 1, "mesh={s}", .{mesh_window[0..mesh_written]});
    try std.testing.expect(padded_written == 16 or padded_written == 17);
    try std.testing.expectEqualSlices(u8, "mesh=Can:INT:1   ", summary.?[0 .. summary.?.len - 1]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[summary.?.len - 1]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const Owner = struct {
        count: usize,
        seen: bool,
    };
    var owner: ?*Owner = try zalloc.zallocValue(allocator, Owner);
    try std.testing.expectEqual(@as(usize, 0), owner.?.count);
    try std.testing.expectEqual(false, owner.?.seen);
    owner.?.count = mesh_written;
    owner.?.seen = true;
    zalloc.zfreeValue(allocator, Owner, &owner);
    try std.testing.expect(owner == null);

    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);

    slab.kfree(slab_rows);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
