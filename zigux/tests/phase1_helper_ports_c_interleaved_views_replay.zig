const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 replay keeps slab counters stable across interleaved byte and array lifetimes" {
    slab.kmalloc_nr_allocated = 0;

    var bytes = slab.kmallocBytes(3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocArray(2, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(bytes, 0x7c);
    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    bytes = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 replay keeps interleaved strErrorR caller views isolated" {
    var backing = [_]u8{'!'} ** 32;

    const empty = str_error_r.strErrorR(2, backing[0..0]);
    try std.testing.expectEqualStrings("", empty);
    try std.testing.expectEqual(@as(u8, '!'), backing[0]);

    const known = str_error_r.strErrorR(12, backing[2..25]);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqual(@as(u8, '!'), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[24]);
    try std.testing.expectEqual(@as(u8, '!'), backing[25]);

    const unknown = str_error_r.strErrorR(4096, backing[26..32]);
    try std.testing.expectEqualStrings("INTER", unknown);
    try std.testing.expectEqual(@as(u8, '!'), backing[25]);
    try std.testing.expectEqual(@as(u8, 0), backing[31]);
}

test "lane10 replay keeps interleaved vsprintf caller windows fenced" {
    var backing = [_]u8{'#'} ** 18;
    const left = backing[1..8];
    const right = backing[9..17];

    const left_written = vsprintf.scnprintf(left, "{d}:{s}", .{ 7, "xy" });
    try std.testing.expectEqual(@as(usize, 4), left_written);
    try std.testing.expectEqualStrings("7:xy", left[0..left_written]);
    try std.testing.expectEqual(@as(u8, 0), left[left_written]);
    try std.testing.expectEqual(@as(u8, '#'), backing[0]);
    try std.testing.expectEqual(@as(u8, '#'), backing[8]);

    const right_written = vsprintf.scnprintfPad(right, 5, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 4), right_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ' ', ' ', ' ', 0 }, right[0..6]);
    try std.testing.expectEqual(@as(u8, '#'), backing[8]);
    try std.testing.expectEqual(@as(u8, '#'), backing[17]);

    const narrowed_written = vsprintf.vscnprintf(left[2..6], "{s}", .{"tool"});
    try std.testing.expectEqual(@as(usize, 3), narrowed_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '7', ':', 't', 'o', 'o', 0, '#' }, left);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ' ', ' ', ' ', 0 }, right[0..6]);
}

test "lane10 replay keeps zalloc byte and value lanes independently reset" {
    const allocator = std.testing.allocator;

    const Payload = extern union {
        raw: [4]u8,
        words: [2]u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);
    bytes.?[0] = 9;
    bytes.?[1] = 8;

    var payload: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expectEqual(@as([4]u8, .{ 0, 0, 0, 0 }), payload.?.raw);
    payload.?.raw = .{ 1, 2, 3, 4 };

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as([4]u8, .{ 1, 2, 3, 4 }), payload.?.raw);

    zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(payload == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);

    payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expectEqual(@as([4]u8, .{ 0, 0, 0, 0 }), payload.?.raw);
}
