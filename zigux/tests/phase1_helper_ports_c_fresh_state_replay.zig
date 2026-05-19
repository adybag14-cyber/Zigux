const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "shared replay keeps slab counter stable around failed allocation" {
    slab.kmalloc_nr_allocated = 0;

    const live = slab.kmallocBytes(8, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(live);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "shared replay restores full strerror message after earlier truncation" {
    var small: [8]u8 = undefined;
    try std.testing.expectEqualStrings("No such", str_error_r.strErrorR(2, &small));

    var large: [64]u8 = undefined;
    try std.testing.expectEqualStrings("No such file or directory", str_error_r.strErrorR(2, &large));
}

test "shared replay keeps one-byte printf buffers terminated" {
    var tiny: [1]u8 = .{0xaa};
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(&tiny, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, 0), tiny[0]);

    tiny[0] = 0xaa;
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintfPad(&tiny, 4, "{s}", .{"id"}));
    try std.testing.expectEqual(@as(u8, 0), tiny[0]);
}

test "shared replay re-zeroes zalloc bytes and values after dirty frees" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u32,
        ready: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    @memset(bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    value.?.count = 99;
    value.?.ready = true;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.ready);
}
