const std = @import("std");
const slab = @import("slab");
const zalloc = @import("zalloc");

test "slab array allocation keeps fail paths and zero flag boundaries separate" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocArray(3, 4, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const plain = slab.kmallocArray(2, 4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(plain, 0xa5);
    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocArray(2, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try std.testing.expect(slab.slabIsAvailable());
}

test "zalloc free helpers reset optionals and tolerate repeated empty frees" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    bytes.?[0] = 0xff;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const Payload = struct {
        count: u16,
        enabled: bool,
        label: [3]u8,
    };

    var payload: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expect(payload != null);
    try std.testing.expectEqual(@as(u16, 0), payload.?.count);
    try std.testing.expectEqual(false, payload.?.enabled);
    try std.testing.expectEqual([_]u8{ 0, 0, 0 }, payload.?.label);

    payload.?.count = 7;
    payload.?.enabled = true;
    zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(payload == null);
    zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(payload == null);
}
