const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps staggered live allocations balanced across gated failures" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zeroed_array = slab.kmallocArray(2, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, zeroed_array);

    try std.testing.expect(slab.kmallocArray(4, 1, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocBytes(1, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(zeroed_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps staggered caller windows isolated" {
    var backing = [_]u8{0xaa} ** 12;

    const known = str_error_r.strErrorR(13, backing[1..5]);
    try std.testing.expectEqualStrings("Per", known);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xaa, 'P', 'e', 'r', 0, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa },
        &backing,
    );

    const generated = str_error_r.strErrorR(4096, backing[6..10]);
    try std.testing.expectEqualStrings("INT", generated);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xaa, 'P', 'e', 'r', 0, 0xaa, 'I', 'N', 'T', 0, 0xaa, 0xaa },
        &backing,
    );
}

test "vsprintf keeps staggered caller windows independent" {
    var backing = [_]u8{0xcc} ** 12;

    const first_written = vsprintf.vscnprintf(backing[1..6], "{s}", .{"abcde"});
    try std.testing.expectEqual(@as(usize, 4), first_written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xcc, 'a', 'b', 'c', 'd', 0, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc },
        &backing,
    );

    const second_written = vsprintf.scnprintfPad(backing[6..11], 3, "{d}", .{7});
    try std.testing.expectEqual(@as(usize, 2), second_written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xcc, 'a', 'b', 'c', 'd', 0, '7', ' ', ' ', 0, 0xcc, 0xcc },
        &backing,
    );
}

test "zalloc keeps byte and value lifetimes independent across staggered reuse" {
    const allocator = std.testing.allocator;
    const Record = struct {
        tag: [2]u8,
        enabled: bool,
        count: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);

    var value: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &value);
    try std.testing.expectEqualDeep(std.mem.zeroes(Record), value.?.*);

    @memset(bytes.?, 0x44);
    value.?.count = 99;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u16, 99), value.?.count);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    zalloc.zfreeValue(allocator, Record, &value);
    try std.testing.expect(value == null);

    var rebound: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &rebound);
    try std.testing.expect(rebound != null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, rebound.?);
}
