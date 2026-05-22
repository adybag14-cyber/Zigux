const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-length allocations still balance allocation counters" {
    slab.kmalloc_nr_allocated = 0;

    const empty_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const empty_array = slab.kmallocArray(0, 4, slab.GFP_KERNEL) orelse {
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(usize, 0), empty_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(empty_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps tiny caller windows nul-terminated" {
    var single: [1]u8 = .{0xaa};
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(13, &single));
    try std.testing.expectEqual(@as(u8, 0), single[0]);

    var double: [2]u8 = .{ 0xaa, 0xbb };
    try std.testing.expectEqualStrings("P", str_error_r.strErrorR(13, &double));
    try std.testing.expectEqual(@as(u8, 'P'), double[0]);
    try std.testing.expectEqual(@as(u8, 0), double[1]);

    var window = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x' };
    try std.testing.expectEqualStrings("S", str_error_r.strErrorR(0, window[2..4]));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'x', 'S', 0, 'x', 'x' }, &window);
}

test "scnprintfPad zero logical size only writes the terminator slot" {
    var buffer = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x' };

    const zero_written = vsprintf.scnprintfPad(buffer[2..], 0, "{s}", .{"abcd"});
    try std.testing.expectEqual(@as(usize, 0), zero_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'x', 0, 'x', 'x', 'x', 'x', 'x' }, &buffer);

    const padded_written = vsprintf.scnprintfPad(buffer[2..], 4, "{s}", .{"Q"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqual(@as(u8, 'x'), buffer[0]);
    try std.testing.expectEqual(@as(u8, 'x'), buffer[1]);
    try std.testing.expectEqual(@as(u8, 'Q'), buffer[2]);
    try std.testing.expectEqual(@as(u8, ' '), buffer[3]);
    try std.testing.expectEqual(@as(u8, ' '), buffer[4]);
    try std.testing.expectEqual(@as(u8, ' '), buffer[5]);
    try std.testing.expectEqual(@as(u8, 0), buffer[6]);
    try std.testing.expectEqual(@as(u8, 'x'), buffer[7]);
}

test "zalloc zero-length bytes and repeated frees stay harmless" {
    const allocator = std.testing.allocator;
    const Value = struct {
        tag: u8,
        child: ?*u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u8, 0), value.?.tag);
    try std.testing.expect(value.?.child == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
