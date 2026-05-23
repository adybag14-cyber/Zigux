const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps adjacent allocations and null frees isolated" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const plain = slab.kmallocArray(2, 3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(plain, 0xa5);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR rewrites one caller view without spilling into the adjacent one" {
    var backing = [_]u8{0xaa} ** 32;

    const left = str_error_r.strErrorR(2, backing[0..8]);
    try std.testing.expectEqualStrings("No such", left);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'N', 'o', ' ', 's', 'u', 'c', 'h', 0 }, backing[0..8]);

    const right = str_error_r.strErrorR(4096, backing[8..24]);
    try std.testing.expect(std.mem.startsWith(u8, right, "INTERNAL ERROR"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'N', 'o', ' ', 's', 'u', 'c', 'h', 0 }, backing[0..8]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[24]);

    const rewritten = str_error_r.strErrorR(0, backing[0..8]);
    try std.testing.expectEqualStrings("Success", rewritten);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'S', 'u', 'c', 'c', 'e', 's', 's', 0 }, backing[0..8]);
}

test "vsprintf keeps adjacent caller views independent across padded and direct writes" {
    var backing = [_]u8{0xcc} ** 18;

    const left_written = vsprintf.scnprintfPad(backing[1..9], 6, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 5), left_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ' ', ' ', ' ', ' ', 0, 0xcc }, backing[1..9]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[9]);

    const right_written = vsprintf.vscnprintf(backing[9..15], "{d}", .{42});
    try std.testing.expectEqual(@as(usize, 2), right_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '4', '2', 0, 0xcc, 0xcc, 0xcc }, backing[9..15]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ' ', ' ', ' ', ' ', 0, 0xcc }, backing[1..9]);
}

test "zalloc frees bytes independently from value reuse and zeroing" {
    const allocator = std.testing.allocator;
    const Value = extern struct {
        word: u32,
        pair: [2]u8,
        maybe: ?*u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.word);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, &value.?.pair);
    try std.testing.expect(value.?.maybe == null);

    value.?.word = 0xdead_beef;
    value.?.pair = .{ 7, 9 };
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u32, 0xdead_beef), value.?.word);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 7, 9 }, &value.?.pair);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    var fresh: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &fresh);
    try std.testing.expectEqual(@as(u32, 0), fresh.?.word);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, &fresh.?.pair);
    try std.testing.expect(fresh.?.maybe == null);
}
