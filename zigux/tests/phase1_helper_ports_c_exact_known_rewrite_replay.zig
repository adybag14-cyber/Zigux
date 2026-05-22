const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab preserves live zeroed allocation across failed growth attempts" {
    slab.kmalloc_nr_allocated = 0;

    const live = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (live) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(live);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR exact-fit known windows preserve neighboring sentinels" {
    var success_backing = [_]u8{'*'} ** 12;
    const success = str_error_r.strErrorR(0, success_backing[2..10]);
    try std.testing.expectEqualStrings("Success", success);
    try std.testing.expectEqual(@as(u8, 0), success_backing[9]);
    try std.testing.expectEqual(@as(u8, '*'), success_backing[1]);
    try std.testing.expectEqual(@as(u8, '*'), success_backing[10]);

    var invalid_backing = [_]u8{'!'} ** 24;
    const invalid = str_error_r.strErrorR(22, invalid_backing[3..20]);
    try std.testing.expectEqualStrings("Invalid argument", invalid);
    try std.testing.expectEqual(@as(u8, 0), invalid_backing[19]);
    try std.testing.expectEqual(@as(u8, '!'), invalid_backing[2]);
    try std.testing.expectEqual(@as(u8, '!'), invalid_backing[20]);
}

test "vscnprintf exact-fit windows can be rewritten shorter in place" {
    var backing = [_]u8{'?'} ** 10;
    const window = backing[2..8];

    const first = vsprintf.vscnprintf(window, "{s}", .{"abcde"});
    try std.testing.expectEqual(@as(usize, 5), first);
    try std.testing.expectEqualStrings("abcde", window[0..first]);
    try std.testing.expectEqual(@as(u8, 0), window[first]);

    const second = vsprintf.vscnprintf(window, "{s}", .{"q"});
    try std.testing.expectEqual(@as(usize, 1), second);
    try std.testing.expectEqual(@as(u8, 'q'), window[0]);
    try std.testing.expectEqual(@as(u8, 0), window[1]);
    try std.testing.expectEqual(@as(u8, '?'), backing[1]);
    try std.testing.expectEqual(@as(u8, '?'), backing[8]);
}

test "zalloc exact-size allocations re-zero bytes and values after dirty frees" {
    const allocator = std.testing.allocator;
    const Payload = struct {
        bytes: [3]u8,
        marker: u16,
    };

    var first_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(first_bytes != null);
    @memset(first_bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &first_bytes);
    try std.testing.expect(first_bytes == null);

    var second_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &second_bytes);
    try std.testing.expect(second_bytes != null);
    for (second_bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var first_value: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expect(first_value != null);
    @memset(first_value.?.bytes[0..], 0xbb);
    first_value.?.marker = 77;
    zalloc.zfreeValue(allocator, Payload, &first_value);
    try std.testing.expect(first_value == null);

    var second_value: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &second_value);
    try std.testing.expect(second_value != null);
    for (second_value.?.bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try std.testing.expectEqual(@as(u16, 0), second_value.?.marker);
}
