const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectSentinel(slice: []const u8, value: u8) !void {
    for (slice) |byte| {
        try std.testing.expectEqual(value, byte);
    }
}

test "slab strided windows survive formatting and errno reuse" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectSentinel(bytes[0..], 0);

    @memset(bytes[0..], 0xa5);

    const first = bytes[2..10];
    const gap = bytes[10..14];
    const second = bytes[14..23];
    const tail = bytes[23..];

    const first_written = vsprintf.scnprintf(first, "s{d}:{s}", .{ 7, "abc" });
    try std.testing.expectEqual(@as(usize, 6), first_written);
    try std.testing.expectEqualStrings("s7:abc", first[0..first_written]);
    try std.testing.expectEqual(@as(u8, 0), first[first_written]);

    const errno = str_error_r.strErrorR(13, second[1..8]);
    try std.testing.expectEqualStrings("Permis", errno);
    try std.testing.expectEqual(@as(u8, 0xa5), second[0]);
    try std.testing.expectEqual(@as(u8, 0), second[7]);
    try std.testing.expectEqual(@as(u8, 0xa5), second[8]);

    const padded_written = vsprintf.scnprintfPad(second, second.len - 1, "x", .{});
    try std.testing.expectEqual(@as(usize, 7), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0 }, second);

    try expectSentinel(bytes[0..2], 0xa5);
    try expectSentinel(gap, 0xa5);
    try expectSentinel(tail, 0xa5);

    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "zalloc scratch can be freed and reacquired after helper reuse" {
    const allocator = std.testing.allocator;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 28);
    defer zalloc.zfreeBytes(allocator, &owner);

    try expectSentinel(owner.?, 0);
    @memset(owner.?, 0xcc);

    const left = owner.?[1..9];
    const mid = owner.?[11..20];
    const right = owner.?[21..27];

    const left_written = vsprintf.vscnprintf(left, "{s}-{d}", .{ "lane", 10 });
    try std.testing.expectEqual(@as(usize, 7), left_written);
    try std.testing.expectEqualStrings("lane-10", left[0..left_written]);
    try std.testing.expectEqual(@as(u8, 0), left[left_written]);

    const unknown = str_error_r.strErrorR(4096, mid);
    try std.testing.expectEqualStrings("INTERNAL", unknown);
    try std.testing.expectEqual(@as(u8, 0), mid[8]);

    const right_written = vsprintf.scnprintf(right, "{d}:{s}", .{ 4, "xy" });
    try std.testing.expectEqual(@as(usize, 4), right_written);
    try std.testing.expectEqualStrings("4:xy", right[0..right_written]);
    try std.testing.expectEqual(@as(u8, 0), right[right_written]);

    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc }, owner.?[9..11]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[20]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[27]);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);

    owner = try zalloc.zallocBytes(allocator, 6);
    try expectSentinel(owner.?, 0);
}
