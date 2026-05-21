const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab balances zero-length arrays and one-byte zeroed allocations" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocArray(0, 8, slab.GFP_KERNEL) orelse {
        return error.TestUnexpectedResult;
    };
    const single = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        slab.kfree(empty);
        return error.TestUnexpectedResult;
    };

    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, 0), single[0]);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(single);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR handles terminator-only and exact-fit caller windows" {
    var storage: [64]u8 = [_]u8{'?'} ** 64;

    const tiny = str_error_r.strErrorR(2, storage[10..11]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, '?'), storage[9]);
    try std.testing.expectEqual(@as(u8, 0), storage[10]);
    try std.testing.expectEqual(@as(u8, '?'), storage[11]);

    const exact = str_error_r.strErrorR(22, storage[24..41]);
    try std.testing.expectEqualStrings("Invalid argument", exact);
    try std.testing.expectEqual(@as(u8, '?'), storage[23]);
    try std.testing.expectEqual(@as(u8, 0), storage[40]);
    try std.testing.expectEqual(@as(u8, '?'), storage[41]);
}

test "vsprintf keeps boundary windows reusable across terminator-only and padded writes" {
    var storage: [16]u8 = [_]u8{'~'} ** 16;

    const tiny = vsprintf.scnprintf(storage[3..4], "{s}", .{"zig"});
    try std.testing.expectEqual(@as(usize, 0), tiny);
    try std.testing.expectEqual(@as(u8, '~'), storage[2]);
    try std.testing.expectEqual(@as(u8, 0), storage[3]);
    try std.testing.expectEqual(@as(u8, '~'), storage[4]);

    const offset_view = storage[6..11];
    const padded = vsprintf.scnprintfPad(offset_view, 99, "{d}", .{7});
    try std.testing.expectEqual(@as(usize, 3), padded);
    try std.testing.expectEqualStrings("7   ", offset_view[0 .. offset_view.len - 1]);
    try std.testing.expectEqual(@as(u8, 0), offset_view[offset_view.len - 1]);
    try std.testing.expectEqual(@as(u8, '~'), storage[5]);
    try std.testing.expectEqual(@as(u8, '~'), storage[11]);

    const reused = vsprintf.vscnprintf(offset_view, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 2), reused);
    try std.testing.expectEqualStrings("xy", offset_view[0..reused]);
    try std.testing.expectEqual(@as(u8, 0), offset_view[reused]);
    try std.testing.expectEqual(@as(u8, ' '), offset_view[reused + 1]);
}

test "zalloc keeps zero-length bytes and re-zeroes small value storage after reuse" {
    const allocator = std.testing.allocator;
    const Payload = extern struct {
        bytes: [3]u8,
        flag: bool,
    };

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty != null);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);

    var value: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &value);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);
    try std.testing.expectEqual(false, value.?.flag);

    value.?.bytes = .{ 0xaa, 0xbb, 0xcc };
    value.?.flag = true;
    zalloc.zfreeValue(allocator, Payload, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);
    try std.testing.expectEqual(false, value.?.flag);
}
