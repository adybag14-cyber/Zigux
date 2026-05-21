const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C keeps slab rewrite cycles zeroed and balanced" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (first) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    @memset(first, 0xaa);
    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const second = slab.kmallocArray(3, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (second) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "phase1 helper ports C keeps strErrorR rewrite cycles inside one caller view" {
    var backing = [_]u8{'#'} ** 20;
    const view = backing[2..12];

    const generated = str_error_r.strErrorR(4096, view);
    try std.testing.expectEqualStrings("INTERNAL ", generated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#' }, backing[0..2]);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#', '#', '#', '#', '#', '#', '#' }, backing[12..20]);

    const known = str_error_r.strErrorR(0, view);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 'S'), backing[2]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#' }, backing[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#', '#', '#', '#', '#', '#', '#' }, backing[12..20]);
}

test "phase1 helper ports C keeps vsprintf rewrite cycles bounded and resettable" {
    var backing = [_]u8{'!'} ** 12;
    const view = backing[2..8];

    const first_written = vsprintf.scnprintfPad(view, 5, "{s}", .{"zig"});
    try std.testing.expectEqual(@as(usize, 4), first_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', ' ', ' ', 0 }, view);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!' }, backing[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', '!', '!' }, backing[8..12]);

    const second_written = vsprintf.scnprintfPad(view, 0, "{s}", .{"reset"});
    try std.testing.expectEqual(@as(usize, 0), second_written);
    try std.testing.expectEqual(@as(u8, 0), view[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!' }, backing[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', '!', '!' }, backing[8..12]);
}

test "phase1 helper ports C keeps zalloc rewrite cycles re-zeroed after free" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u16,
        flag: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);
    @memset(bytes.?, 0xff);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.flag);
    value.?.count = 9;
    value.?.flag = true;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.flag);
}
