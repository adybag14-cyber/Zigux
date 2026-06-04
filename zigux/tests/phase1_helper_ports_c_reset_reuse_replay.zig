const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectAllZero(bytes: []const u8) !void {
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "slab zeroed arrays can be formatted freed and reacquired cleanly" {
    slab.kmalloc_nr_allocated = 0;

    var first: ?[]u8 = slab.kmallocArray(4, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectAllZero(first.?);

    const formatted = vsprintf.scnprintf(first.?[4..18], "reset-{d}", .{17});
    try std.testing.expectEqual(@as(usize, 8), formatted);
    try std.testing.expectEqualStrings("reset-17", first.?[4 .. 4 + formatted]);
    try std.testing.expectEqual(@as(u8, 0), first.?[4 + formatted]);

    const err = str_error_r.strErrorR(13, first.?[20..32]);
    try std.testing.expectEqualStrings("Permission ", err);
    try std.testing.expectEqual(@as(u8, 0), first.?[31]);

    slab.kfree(first);
    first = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const second = slab.kmallocArray(4, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectAllZero(second);
}

test "zalloc owners reset after copying slab formatted bytes" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_payload = slab.kmallocBytes(24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_payload);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const source_len = vsprintf.scnprintf(slab_payload[2..18], "owner:{d}", .{42});
    try std.testing.expectEqualStrings("owner:42", slab_payload[2 .. 2 + source_len]);

    var owned: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    try expectAllZero(owned.?);
    @memcpy(owned.?[1 .. 1 + source_len], slab_payload[2 .. 2 + source_len]);
    try std.testing.expectEqualStrings("owner:42", owned.?[1 .. 1 + source_len]);

    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);
    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);

    owned = try zalloc.zallocBytes(allocator, 16);
    defer zalloc.zfreeBytes(allocator, &owned);
    try expectAllZero(owned.?);
}

test "reused caller windows preserve sentinels across strerror and padded formats" {
    var backing = [_]u8{
        0xa0, 0xa1, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7,
        0xa8, 0xa9, 0xaa, 0xab, 0xac, 0xad, 0xae, 0xaf,
        0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7,
        0xb8, 0xb9, 0xba, 0xbb, 0xbc, 0xbd, 0xbe, 0xbf,
    };

    const pad_window = backing[3..14];
    const padded = vsprintf.scnprintfPad(pad_window, 9, "id={d}", .{5});
    try std.testing.expectEqual(@as(usize, 9), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa0, 0xa1, 0xa2 }, backing[0..3]);
    try std.testing.expectEqualSlices(u8, "id=5     ", backing[3..12]);
    try std.testing.expectEqual(@as(u8, 0), backing[12]);
    try std.testing.expectEqual(@as(u8, 0xad), backing[13]);

    const strerror_window = backing[15..29];
    const rendered = str_error_r.strErrorR(4096, strerror_window);
    try std.testing.expectEqualStrings("INTERNAL ERRO", rendered);
    try std.testing.expectEqual(@as(u8, 0xae), backing[15 - 1]);
    try std.testing.expectEqual(@as(u8, 0), backing[28]);
    try std.testing.expectEqual(@as(u8, 0xbd), backing[29]);

    @memset(backing[3..29], 0);
    try expectAllZero(backing[3..29]);

    const rewritten = vsprintf.vscnprintf(backing[8..18], "{s}-{d}", .{ "reuse", 3 });
    try std.testing.expectEqual(@as(usize, 7), rewritten);
    try std.testing.expectEqualStrings("reuse-3", backing[8 .. 8 + rewritten]);
    try std.testing.expectEqual(@as(u8, 0), backing[8 + rewritten]);
    try std.testing.expectEqual(@as(u8, 0xa0), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xbf), backing[31]);
}
