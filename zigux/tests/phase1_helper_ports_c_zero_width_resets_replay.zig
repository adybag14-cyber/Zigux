const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps zero-byte allocations balanced across reclaimless failures" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    const single = slab.kmallocArray(1, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        slab.kfree(empty);
        return error.TestUnexpectedResult;
    };

    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, 0), single[0]);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(single);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps zero-width and offset caller views isolated" {
    var storage: [80]u8 = [_]u8{'!'} ** 80;

    const empty = str_error_r.strErrorR(13, storage[20..20]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, '!'), storage[19]);
    try std.testing.expectEqual(@as(u8, '!'), storage[20]);

    const offset = str_error_r.strErrorR(4096, storage[24..56]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096", offset);
    try std.testing.expectEqual(@as(u8, '!'), storage[23]);
    try std.testing.expectEqual(@as(u8, 0), storage[55]);
    try std.testing.expectEqual(@as(u8, '!'), storage[56]);

    const before_left = storage[29];
    const before_right = storage[38];
    const reuse = str_error_r.strErrorR(0, storage[30..38]);
    try std.testing.expectEqualStrings("Success", reuse);
    try std.testing.expectEqual(before_left, storage[29]);
    try std.testing.expectEqual(@as(u8, 0), storage[37]);
    try std.testing.expectEqual(before_right, storage[38]);
}

test "vsprintf resets zero-logical views before offset reuse" {
    var storage: [18]u8 = [_]u8{'~'} ** 18;

    const offset = storage[4..10];
    const zeroed = vsprintf.scnprintfPad(offset, 0, "{s}", .{"abc"});
    try std.testing.expectEqual(@as(usize, 0), zeroed);
    try std.testing.expectEqual(@as(u8, '~'), storage[3]);
    try std.testing.expectEqual(@as(u8, 0), offset[0]);
    try std.testing.expectEqual(@as(u8, '~'), offset[1]);
    try std.testing.expectEqual(@as(u8, '~'), storage[10]);

    const exact = vsprintf.scnprintf(offset, "{s}", .{"reset"});
    try std.testing.expectEqual(@as(usize, 5), exact);
    try std.testing.expectEqualStrings("reset", offset[0..exact]);
    try std.testing.expectEqual(@as(u8, 0), offset[exact]);
    try std.testing.expectEqual(@as(u8, '~'), storage[3]);
    try std.testing.expectEqual(@as(u8, '~'), storage[10]);

    const tiny = vsprintf.vscnprintf(storage[12..13], "{d}", .{42});
    try std.testing.expectEqual(@as(usize, 0), tiny);
    try std.testing.expectEqual(@as(u8, '~'), storage[11]);
    try std.testing.expectEqual(@as(u8, 0), storage[12]);
    try std.testing.expectEqual(@as(u8, '~'), storage[13]);
}

test "zalloc re-zeroes empty-byte and nested-value storage after explicit resets" {
    const allocator = std.testing.allocator;
    const Payload = extern struct {
        pair: [2]u16,
        flag: bool,
    };

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty != null);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);
    bytes.?[0] = 0xaa;
    bytes.?[1] = 0xbb;
    bytes.?[2] = 0xcc;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    bytes = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);

    var value: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &value);
    try std.testing.expectEqual(@as([2]u16, .{ 0, 0 }), value.?.pair);
    try std.testing.expectEqual(false, value.?.flag);
    value.?.pair = .{ 9, 7 };
    value.?.flag = true;
    zalloc.zfreeValue(allocator, Payload, &value);
    try std.testing.expect(value == null);
    value = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expectEqual(@as([2]u16, .{ 0, 0 }), value.?.pair);
    try std.testing.expectEqual(false, value.?.flag);
}
