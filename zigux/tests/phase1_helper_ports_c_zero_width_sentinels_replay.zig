const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-width allocations keep counters and null frees stable" {
    slab.kmalloc_nr_allocated = 0;

    var empty = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    empty = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(empty);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR zero-width slices preserve sentinels and tiny buffers terminate" {
    var storage = [_]u8{ 'L', 'M', 'N', 'O' };
    const empty = str_error_r.strErrorR(2, storage[1..1]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'L', 'M', 'N', 'O' }, &storage);

    var tiny = [_]u8{'X'};
    const short = str_error_r.strErrorR(22, &tiny);
    try std.testing.expectEqual(@as(usize, 0), short.len);
    try std.testing.expectEqual(@as(u8, 0), tiny[0]);
}

test "vsprintf zero-width and zero-logical offset slices stay bounded" {
    var empty_backing = [_]u8{ 'a', 'b', 'c', 'd' };
    const empty_written = vsprintf.scnprintf(empty_backing[2..2], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 'd' }, &empty_backing);

    var offset = [_]u8{ 'q', 'r', 's', 't', 'u' };
    const padded_written = vsprintf.scnprintfPad(offset[1..4], 0, "{s}", .{"lane10"});
    try std.testing.expectEqual(@as(usize, 0), padded_written);
    try std.testing.expectEqual(@as(u8, 'q'), offset[0]);
    try std.testing.expectEqual(@as(u8, 0), offset[1]);
    try std.testing.expectEqual(@as(u8, 's'), offset[2]);
    try std.testing.expectEqual(@as(u8, 't'), offset[3]);
    try std.testing.expectEqual(@as(u8, 'u'), offset[4]);
}

test "zalloc zero-width bytes and values reset optional ownership" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const Value = struct {
        flag: bool,
        count: usize,
    };

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(false, value.?.flag);
    try std.testing.expectEqual(@as(usize, 0), value.?.count);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
