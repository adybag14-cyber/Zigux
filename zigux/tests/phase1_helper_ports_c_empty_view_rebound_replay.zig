const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 slab zero-length allocations and reclaimless failures keep counters balanced" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(2, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zero_array = slab.kmallocArray(3, 0, slab.GFP_KERNEL) orelse {
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 strErrorR empty views stay untouched and later wider views rebound cleanly" {
    var backing = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0xee };

    const empty = str_error_r.strErrorR(13, backing[2..2]);
    try std.testing.expectEqualStrings("", empty);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0xee }, &backing);

    const known = str_error_r.strErrorR(13, backing[1..3]);
    try std.testing.expectEqualStrings("P", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 'P', 0, 0xdd, 0xee }, &backing);

    const unknown = str_error_r.strErrorR(4096, backing[1..4]);
    try std.testing.expectEqualStrings("IN", unknown);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 'I', 'N', 0, 0xee }, &backing);
}

test "lane10 vsprintf zero-logical writes rebound into the same caller window" {
    var backing = [_]u8{ '#', '#', '#', '#', '#', '#', '#' };
    const inner = backing[1..6];

    const empty_written = vsprintf.scnprintfPad(inner, 0, "{s}", .{"host"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', 0, '#', '#', '#', '#', '#' }, &backing);

    const rebound_written = vsprintf.vscnprintf(inner, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 2), rebound_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', 'a', 'b', 0, '#', '#', '#' }, &backing);

    const padded_written = vsprintf.scnprintfPad(inner, 4, "{s}", .{"z"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', 'z', ' ', ' ', ' ', 0, '#' }, &backing);
}

test "lane10 zalloc zero-sized and rebound allocations come back fully zeroed" {
    const allocator = std.testing.allocator;
    const Value = struct {
        tag: [2]u8,
        flag: bool,
        maybe: ?*u8,
    };

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, bytes.?);
    bytes.?[0] = 0x7a;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, bytes.?);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    value.?.tag = .{ 9, 7 };
    value.?.flag = true;
    value.?.maybe = &bytes.?[0];
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as([2]u8, .{ 0, 0 }), value.?.tag);
    try std.testing.expectEqual(false, value.?.flag);
    try std.testing.expect(value.?.maybe == null);
}
