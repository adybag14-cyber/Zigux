const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab array allocations balance counters through nested slices" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocArray(3, 5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 15), bytes.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{0} ** 15, bytes);

    const middle = bytes[5..10];
    @memset(middle, 0x5a);
    try std.testing.expectEqualSlices(u8, &[_]u8{0} ** 5, bytes[0..5]);
    try std.testing.expectEqualSlices(u8, &[_]u8{0x5a} ** 5, bytes[5..10]);
    try std.testing.expectEqualSlices(u8, &[_]u8{0} ** 5, bytes[10..15]);

    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR stays inside caller subviews and terminates there" {
    var backing = [_]u8{0xcc} ** 16;
    const window = backing[3..11];

    const rendered = str_error_r.strErrorR(22, window);
    try std.testing.expectEqualStrings("Invalid", rendered);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[2]);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[11]);

    const empty = str_error_r.strErrorR(12, backing[5..5]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, 'v'), backing[5]);
}

test "vsprintf bounded views keep sentinels outside the render window" {
    var direct = [_]u8{0xdd} ** 12;
    var alias = [_]u8{0xee} ** 12;

    const direct_window = direct[2..8];
    const alias_window = alias[2..8];
    const direct_written = vsprintf.scnprintf(direct_window, "{s}:{d}", .{ "lane", 10 });
    const alias_written = vsprintf.vscnprintf(alias_window, "{s}:{d}", .{ "lane", 10 });

    try std.testing.expectEqual(direct_written, alias_written);
    try std.testing.expectEqual(@as(usize, 5), direct_written);
    try std.testing.expectEqualStrings("lane:", direct_window[0..direct_written]);
    try std.testing.expectEqualSlices(u8, direct_window, alias_window);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 0xdd }, direct[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xee, 0xee }, alias[0..2]);
    try std.testing.expectEqual(@as(u8, 0xdd), direct[8]);
    try std.testing.expectEqual(@as(u8, 0xee), alias[8]);

    const padded_written = vsprintf.scnprintfPad(direct[8..12], 3, "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0 }, direct[8..12]);
}

test "zalloc zeroes nested aggregates and clears optional owners" {
    const allocator = std.testing.allocator;
    const Payload = struct {
        len: usize,
        ready: bool,
        data: [4]u16,
        child: ?*u8,
    };

    var payload: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &payload);

    try std.testing.expect(payload != null);
    try std.testing.expectEqual(@as(usize, 0), payload.?.len);
    try std.testing.expectEqual(false, payload.?.ready);
    try std.testing.expectEqualSlices(u16, &[_]u16{0} ** 4, &payload.?.data);
    try std.testing.expect(payload.?.child == null);

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(empty != null);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);

    zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(payload == null);
}
