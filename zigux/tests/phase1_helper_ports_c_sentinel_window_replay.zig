const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab fail paths keep live allocation accounting stable" {
    slab.kmalloc_nr_allocated = 0;

    const live = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(live);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (live) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocArray(4, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR stays inside offset caller windows for truncated and exact-fit renders" {
    var backing = [_]u8{0xaa} ** 48;

    const truncated = str_error_r.strErrorR(4096, backing[5..13]);
    try std.testing.expectEqualStrings("INTERNA", truncated);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[4]);
    try std.testing.expectEqual(@as(u8, 0), backing[12]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[13]);

    const exact_fit = str_error_r.strErrorR(0, backing[20..28]);
    try std.testing.expectEqualStrings("Success", exact_fit);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[19]);
    try std.testing.expectEqual(@as(u8, 0), backing[27]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[28]);
}

test "vsprintf offset caller windows preserve outer sentinels across padded reuse" {
    var backing = [_]u8{0xcc} ** 12;
    const window = backing[2..8];

    const padded_written = vsprintf.scnprintfPad(window, 5, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ' ', ' ', ' ', 0 }, window);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[8]);

    const direct_written = vsprintf.scnprintf(window, "{s}", .{"tooling"});
    try std.testing.expectEqual(@as(usize, 5), direct_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 't', 'o', 'o', 'l', 'i', 0 }, window);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[8]);
}

test "zalloc zeroes fresh bytes and values after earlier dirty frees" {
    const allocator = std.testing.allocator;
    const Value = extern struct {
        bytes: [3]u8,
        flag: u8,
    };

    var first_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expect(first_bytes != null);
    @memset(first_bytes.?, 0x5a);
    zalloc.zfreeBytes(allocator, &first_bytes);
    try std.testing.expect(first_bytes == null);

    var second_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &second_bytes);
    for (second_bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var first_value: ?*Value = try zalloc.zallocValue(allocator, Value);
    first_value.?.bytes = .{ 1, 2, 3 };
    first_value.?.flag = 1;
    zalloc.zfreeValue(allocator, Value, &first_value);
    try std.testing.expect(first_value == null);

    var second_value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &second_value);
    try std.testing.expectEqual(std.mem.zeroes(Value), second_value.?.*);
}
