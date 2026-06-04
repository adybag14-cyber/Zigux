const std = @import("std");
const slab = @import("slab");
const zalloc = @import("zalloc");

const AllocPayload = struct {
    count: u32,
    enabled: bool,
    tag: [4]u8,
};

test "slab no-reclaim and overflow failures leave allocation counter unchanged" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(16, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const bytes = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "zalloc bytes and values clear memory and reset optional handles" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 9);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    @memset(bytes.?, 0xa5);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var payload: ?*AllocPayload = try zalloc.zallocValue(allocator, AllocPayload);
    try std.testing.expect(payload != null);
    try std.testing.expectEqual(@as(u32, 0), payload.?.count);
    try std.testing.expectEqual(false, payload.?.enabled);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &payload.?.tag);

    payload.?.count = 7;
    payload.?.enabled = true;
    payload.?.tag = .{ 'z', 'i', 'g', 'x' };
    zalloc.zfreeValue(allocator, AllocPayload, &payload);
    try std.testing.expect(payload == null);
    zalloc.zfreeValue(allocator, AllocPayload, &payload);
    try std.testing.expect(payload == null);
}
