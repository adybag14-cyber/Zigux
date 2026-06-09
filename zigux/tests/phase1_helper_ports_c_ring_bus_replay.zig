const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "ring bus carries slab errors through zalloc formatting handoffs" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slab_ring_owner: ?[]u8 = slab.kmallocArray(3, 12, slab.GFP_KERNEL | slab.__GFP_ZERO);
    const slab_ring = slab_ring_owner orelse return error.TestUnexpectedResult;
    errdefer slab.kfree(slab_ring_owner);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 36), slab_ring.len);
    for (slab_ring) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(slab_ring, 0xa5);
    const known = str_error_r.strErrorR(22, slab_ring[1..18]);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_ring[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_ring[17]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_ring[18]);

    const fallback = str_error_r.strErrorR(31337, slab_ring[20..36]);
    try std.testing.expectEqualStrings("INTERNAL ERROR:", fallback);
    try std.testing.expectEqual(@as(u8, 0), slab_ring[35]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    for (summary_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const summary_written = vsprintf.scnprintf(
        summary_owner.?,
        "known={s}|fallback={s}",
        .{ known, fallback },
    );
    try std.testing.expectEqual(@as(usize, 47), summary_written);
    try std.testing.expectEqualStrings(
        "known=Invalid argument|fallback=INTERNAL ERROR:",
        summary_owner.?[0..summary_written],
    );
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[summary_written]);

    var padded_owner: ?[]u8 = slab.kmallocBytes(16, slab.GFP_KERNEL | slab.__GFP_ZERO);
    const padded = padded_owner orelse return error.TestUnexpectedResult;
    errdefer slab.kfree(padded_owner);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(padded, 0xcc);

    const padded_written = vsprintf.scnprintfPad(padded[2..14], 11, "bus:{d}", .{summary_written});
    try std.testing.expect(padded_written == 10 or padded_written == 11);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc }, padded[0..2]);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'b', 'u', 's', ':', '4', '7', ' ', ' ', ' ', ' ', ' ', 0 },
        padded[2..14],
    );
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc }, padded[14..16]);

    const Snapshot = struct {
        bytes: usize,
        saw_known: bool,
        tags: [3]u8,
    };
    var snapshot_owner: ?*Snapshot = try zalloc.zallocValue(allocator, Snapshot);
    try std.testing.expectEqual(@as(usize, 0), snapshot_owner.?.bytes);
    try std.testing.expectEqual(false, snapshot_owner.?.saw_known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &snapshot_owner.?.tags);

    snapshot_owner.?.* = .{
        .bytes = summary_written,
        .saw_known = known.len != 0,
        .tags = .{ 'r', 'i', 'g' },
    };
    try std.testing.expectEqual(@as(usize, 47), snapshot_owner.?.bytes);
    try std.testing.expect(snapshot_owner.?.saw_known);
    try std.testing.expectEqualSlices(u8, "rig", &snapshot_owner.?.tags);

    zalloc.zfreeValue(allocator, Snapshot, &snapshot_owner);
    try std.testing.expect(snapshot_owner == null);
    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);

    slab.kfree(padded_owner);
    padded_owner = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(slab_ring_owner);
    slab_ring_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
