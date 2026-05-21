const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C keeps slab limit-oriented allocation counters aligned" {
    slab.kmalloc_nr_allocated = 0;

    const zero = slab.kmallocArray(0, 32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zero);
    try std.testing.expectEqual(@as(usize, 0), zero.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const bytes = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "phase1 helper ports C keeps strErrorR writes inside clamped offset views" {
    var known_backing = [_]u8{'#'} ** 16;
    const known = str_error_r.strErrorR(0, known_backing[3..11]);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#', '#' }, known_backing[0..3]);
    try std.testing.expectEqual(@as(u8, 0), known_backing[10]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#', '#', '#', '#' }, known_backing[11..16]);

    var generated_backing = [_]u8{'@'} ** 16;
    const generated = str_error_r.strErrorR(4096, generated_backing[4..13]);
    try std.testing.expectEqualStrings("INTERNAL", generated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '@', '@', '@', '@' }, generated_backing[0..4]);
    try std.testing.expectEqual(@as(u8, 0), generated_backing[12]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '@', '@', '@' }, generated_backing[13..16]);
}

test "phase1 helper ports C keeps vsprintf padding inside clamped offset views" {
    var padded_backing = [_]u8{'!'} ** 18;
    const padded = padded_backing[2..9];
    const written = vsprintf.scnprintfPad(padded, 32, "{s}", .{"zig"});
    try std.testing.expectEqual(@as(usize, 5), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', ' ', ' ', ' ', 0 }, padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!' }, padded_backing[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', '!', '!', '!', '!', '!', '!', '!' }, padded_backing[9..18]);

    var single_backing = [_]u8{'?'} ** 4;
    const single = single_backing[1..2];
    const single_written = vsprintf.vscnprintf(single, "{s}", .{"wide"});
    try std.testing.expectEqual(@as(usize, 0), single_written);
    try std.testing.expectEqual(@as(u8, '?'), single_backing[0]);
    try std.testing.expectEqual(@as(u8, 0), single_backing[1]);
    try std.testing.expectEqual(@as(u8, '?'), single_backing[2]);
    try std.testing.expectEqual(@as(u8, '?'), single_backing[3]);
}

test "phase1 helper ports C keeps zalloc zero-length and re-zeroed ownership aligned" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u32,
        flags: [3]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);

    var first: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u32, 0), first.?.count);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &first.?.flags);
    first.?.count = 99;
    first.?.flags = .{ 1, 2, 3 };
    zalloc.zfreeValue(allocator, Value, &first);
    try std.testing.expect(first == null);

    var second: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &second);
    try std.testing.expectEqual(@as(u32, 0), second.?.count);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &second.?.flags);
}
