const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectPadCount(actual: usize, current: usize, historical: usize) !void {
    try std.testing.expect(actual == current or actual == historical);
}

test "anchor ladder relays slab error windows through zalloc summaries" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;

    var slab_owner: ?[]u8 = slab.kmallocBytes(72, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer if (slab_owner) |bytes| slab.kfree(bytes);
    @memset(slab_owner.?, 0xaa);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const known_window = slab_owner.?[3..21];
    const known = str_error_r.strErrorR(13, known_window);
    try std.testing.expectEqualStrings("Permission denied", known);
    try std.testing.expectEqual(@as(u8, 0xaa), slab_owner.?[2]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner.?[20]);
    try std.testing.expectEqual(@as(u8, 0xaa), slab_owner.?[21]);

    const fallback_window = slab_owner.?[24..45];
    const fallback = str_error_r.strErrorR(5150, fallback_window);
    try std.testing.expectEqual(@as(usize, 20), fallback.len);
    try std.testing.expect(std.mem.startsWith(u8, fallback, "INTERNAL ERROR"));
    try std.testing.expectEqual(@as(u8, 0xaa), slab_owner.?[23]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner.?[44]);
    try std.testing.expectEqual(@as(u8, 0xaa), slab_owner.?[45]);

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    for (summary_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const summary_written = vsprintf.scnprintf(
        summary_owner.?,
        "anchor:{s}:{d}",
        .{ known[0..4], fallback.len },
    );
    try std.testing.expectEqualStrings("anchor:Perm:20", summary_owner.?[0..summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[summary_written]);

    const pad_window = slab_owner.?[50..62];
    const pad_written = vsprintf.scnprintfPad(pad_window, 10, "ladder={d}", .{7});
    try expectPadCount(pad_written, 10, 9);
    try std.testing.expectEqualStrings("ladder=7  ", pad_window[0..10]);
    try std.testing.expectEqual(@as(u8, 0), pad_window[10]);
    try std.testing.expectEqual(@as(u8, 0xaa), pad_window[11]);

    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);

    slab.kfree(slab_owner.?);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "anchor ladder preserves failed slab allocations and zalloc value reset" {
    const allocator = std.testing.allocator;

    const Snapshot = struct {
        tag: u16,
        flags: [3]bool,
        bytes: [5]u8,
    };

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(16, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var value_owner: ?*Snapshot = try zalloc.zallocValue(allocator, Snapshot);
    defer zalloc.zfreeValue(allocator, Snapshot, &value_owner);

    try std.testing.expectEqual(@as(u16, 0), value_owner.?.tag);
    for (value_owner.?.flags) |flag| {
        try std.testing.expectEqual(false, flag);
    }
    for (value_owner.?.bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    value_owner.?.tag = 0x10;
    value_owner.?.flags[1] = true;
    value_owner.?.bytes[4] = 0x7f;

    zalloc.zfreeValue(allocator, Snapshot, &value_owner);
    try std.testing.expect(value_owner == null);
    zalloc.zfreeValue(allocator, Snapshot, &value_owner);
    try std.testing.expect(value_owner == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
