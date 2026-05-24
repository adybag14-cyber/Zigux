const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-length allocation stays balanced beside a rejected sibling request" {
    slab.kmalloc_nr_allocated = 0;

    var empty: ?[]u8 = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(empty);

    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(2, 4, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    empty = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps sentinel neighbors intact across offset and tiny caller views" {
    var storage = [_]u8{0x6b} ** 10;

    const exact = str_error_r.strErrorR(0, storage[1..9]);
    try std.testing.expectEqualStrings("Success", exact);
    try std.testing.expectEqual(@as(u8, 0x6b), storage[0]);
    try std.testing.expectEqual(@as(u8, 0), storage[8]);
    try std.testing.expectEqual(@as(u8, 0x6b), storage[9]);

    const tiny = str_error_r.strErrorR(4096, storage[3..4]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, 'u'), storage[2]);
    try std.testing.expectEqual(@as(u8, 0), storage[3]);
    try std.testing.expectEqual(@as(u8, 'c'), storage[4]);
}

test "vsprintf reuses an interior caller window without disturbing sentinels" {
    var storage = [_]u8{0x5a} ** 9;

    const padded = vsprintf.scnprintfPad(storage[1..7], 32, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 4), padded);
    try std.testing.expectEqual(@as(u8, 0x5a), storage[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ' ', ' ', ' ', 0 }, storage[1..7]);
    try std.testing.expectEqual(@as(u8, 0x5a), storage[7]);

    const truncated = vsprintf.vscnprintf(storage[2..6], "{s}", .{"tooling"});
    try std.testing.expectEqual(@as(usize, 3), truncated);
    try std.testing.expectEqual(@as(u8, 'a'), storage[1]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 't', 'o', 'o', 0 }, storage[2..6]);
    try std.testing.expectEqual(@as(u8, 0), storage[6]);
    try std.testing.expectEqual(@as(u8, 0x5a), storage[7]);
}

test "zalloc zero-size bytes and nested values reset safely on repeated frees" {
    const allocator = std.testing.allocator;
    const Nested = struct {
        bytes: [3]u8,
        maybe: ?*u8,
        flags: [2]bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);

    var value: ?*Nested = try zalloc.zallocValue(allocator, Nested);
    defer zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);
    try std.testing.expect(value.?.maybe == null);
    try std.testing.expectEqual(@as(bool, false), value.?.flags[0]);
    try std.testing.expectEqual(@as(bool, false), value.?.flags[1]);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expect(value == null);
}
