const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab sibling windows reuse counters without cross-free leakage" {
    slab.kmalloc_nr_allocated = 0;

    const left = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const right = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0 }, left);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0 }, right);

    @memset(left, 0x4c);
    @memset(right[1..5], 0x52);
    slab.kfree(left);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0x52, 0x52, 0x52, 0x52, 0 }, right);

    slab.kfree(right);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR caller subwindows terminate without touching surrounding sentinels" {
    var backing = [_]u8{
        0xaa, 0xaa, 0xaa, 0xaa,
        0xaa, 0xaa, 0xaa, 0xaa,
        0xaa, 0xaa, 0xaa, 0xaa,
    };

    const known = str_error_r.strErrorR(12, backing[2..9]);
    try std.testing.expectEqualStrings("Cannot", known);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[9]);

    backing[3] = 0xab;
    backing[11] = 0xab;
    const fallback = str_error_r.strErrorR(777, backing[4..11]);
    try std.testing.expectEqualStrings("INTERN", fallback);
    try std.testing.expectEqual(@as(u8, 0xab), backing[3]);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, 0xab), backing[11]);
}

test "vsprintf reuse windows clamp independently before zalloc owners reset" {
    var line = [_]u8{ 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc };

    const first = vsprintf.scnprintf(line[1..6], "{s}:{d}", .{ "abcd", 9 });
    try std.testing.expectEqual(@as(usize, 4), first);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 'a', 'b', 'c', 'd', 0, 0xcc, 0xcc, 0xcc, 0xcc }, &line);

    const second = vsprintf.scnprintfPad(line[3..9], 16, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 5), second);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 'a', 'b', 'x', 'y', ' ', ' ', ' ', 0, 0xcc }, &line);

    const allocator = std.testing.allocator;
    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const State = struct {
        seen: u16,
        active: bool,
        code: u8,
    };
    var state: ?*State = try zalloc.zallocValue(allocator, State);
    try std.testing.expectEqual(@as(u16, 0), state.?.seen);
    try std.testing.expectEqual(false, state.?.active);
    try std.testing.expectEqual(@as(u8, 0), state.?.code);
    zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expect(state == null);
}
