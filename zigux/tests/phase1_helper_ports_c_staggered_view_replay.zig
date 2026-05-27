const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab staggered views keep live allocation counters and zeroed neighbors honest" {
    slab.kmalloc_nr_allocated = 0;

    const left = slab.kmallocBytes(3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    @memset(left, 0x7b);

    const zeroed = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(left);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "strErrorR staggered caller slices keep each terminator fenced to its own view" {
    var backing = [_]u8{0xaa} ** 18;

    const left = str_error_r.strErrorR(22, backing[0..4]);
    try std.testing.expectEqualStrings("Inv", left);
    try std.testing.expectEqual(@as(u8, 0), backing[3]);

    const middle = str_error_r.strErrorR(2, backing[4..10]);
    try std.testing.expectEqualStrings("No su", middle);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqualSlices(u8, "Inv", backing[0..3]);

    const right = str_error_r.strErrorR(4096, backing[10..18]);
    try std.testing.expectEqualStrings("INTERNA", right);
    try std.testing.expectEqual(@as(u8, 0), backing[17]);
    try std.testing.expectEqualSlices(u8, "No su", backing[4..9]);
}

test "vsprintf staggered caller windows preserve earlier prefixes across overlaps" {
    var backing = [_]u8{0xcc} ** 14;

    const padded = vsprintf.scnprintfPad(backing[1..8], 6, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 5), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', ' ', 0 }, backing[1..8]);

    const middle = vsprintf.vscnprintf(backing[4..10], "{d}", .{1234});
    try std.testing.expectEqual(@as(usize, 4), middle);
    try std.testing.expectEqualSlices(u8, "xy ", backing[1..4]);
    try std.testing.expectEqualSlices(u8, "1234", backing[4..8]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);

    const tail = vsprintf.scnprintf(backing[9..14], "{s}", .{"zz"});
    try std.testing.expectEqual(@as(usize, 2), tail);
    try std.testing.expectEqualSlices(u8, "zz", backing[9..11]);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);
}

test "zalloc staggered releases re-zero byte and value views after reuse" {
    const allocator = std.testing.allocator;
    const Pair = extern struct {
        a: u8,
        b: u8,
        c: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expect(bytes != null);
    bytes.?[0] = 9;
    bytes.?[1] = 8;
    bytes.?[2] = 7;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var bytes_again: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes_again);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes_again.?);

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expect(pair != null);
    pair.?.a = 0xff;
    pair.?.b = 0x44;
    pair.?.c = 0xfeed;
    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);

    var pair_again: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair_again);
    try std.testing.expectEqual(@as(u8, 0), pair_again.?.a);
    try std.testing.expectEqual(@as(u8, 0), pair_again.?.b);
    try std.testing.expectEqual(@as(u16, 0), pair_again.?.c);
}
