const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab balances empty zeroed arrays across failed non-reclaim attempts" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR one-byte generated windows still terminate in place" {
    var storage = [_]u8{ 'L', 'M', 'N' };
    const rendered = str_error_r.strErrorR(4096, storage[1..2]);

    try std.testing.expectEqual(@as(usize, 0), rendered.len);
    try std.testing.expectEqual(@as(u8, 'L'), storage[0]);
    try std.testing.expectEqual(@as(u8, 0), storage[1]);
    try std.testing.expectEqual(@as(u8, 'N'), storage[2]);
}

test "vsprintf clamps oversized logical sizes and one-byte windows" {
    var storage = [_]u8{ '#', '#', '#', '#', '#', '#', '#', '#', '#' };
    const padded = vsprintf.scnprintfPad(storage[2..7], 99, "{s}", .{"xy"});

    try std.testing.expectEqual(@as(usize, 3), padded);
    try std.testing.expectEqualStrings("xy  ", storage[2..6]);
    try std.testing.expectEqual(@as(u8, 0), storage[6]);
    try std.testing.expectEqual(@as(u8, '#'), storage[1]);
    try std.testing.expectEqual(@as(u8, '#'), storage[7]);

    const narrowed = vsprintf.vscnprintf(storage[2..3], "{s}", .{"later"});
    try std.testing.expectEqual(@as(usize, 0), narrowed);
    try std.testing.expectEqual(@as(u8, 0), storage[2]);
    try std.testing.expectEqual(@as(u8, '#'), storage[1]);
    try std.testing.expectEqual(@as(u8, 'y'), storage[3]);
}

test "zalloc zero-length bytes and fresh values re-zero after dirty frees" {
    const allocator = std.testing.allocator;

    var empty_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(empty_bytes != null);
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.?.len);
    zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes == null);

    const Payload = extern struct {
        marker: u16,
        payload: extern union {
            words: [2]u32,
            byte: u8,
        },
        tail: bool,
    };

    var first: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expect(first != null);
    first.?.marker = 19;
    first.?.payload.words = .{ 7, 9 };
    first.?.tail = true;
    zalloc.zfreeValue(allocator, Payload, &first);
    try std.testing.expect(first == null);

    var second: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &second);
    try std.testing.expect(second != null);
    try std.testing.expectEqual(@as(u16, 0), second.?.marker);
    try std.testing.expectEqual(@as(u32, 0), second.?.payload.words[0]);
    try std.testing.expectEqual(@as(u32, 0), second.?.payload.words[1]);
    try std.testing.expectEqual(false, second.?.tail);
}
