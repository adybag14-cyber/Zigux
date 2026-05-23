const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps live allocations balanced across reclaim-less failures" {
    slab.kmalloc_nr_allocated = 0;

    const zeroed = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const plain = slab.kmallocArray(2, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocBytes(4, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR minimal caller windows keep neighboring sentinels intact" {
    var empty_backing = [_]u8{'#'} ** 4;
    const empty = str_error_r.strErrorR(13, empty_backing[1..1]);
    try std.testing.expectEqualStrings("", empty);
    try std.testing.expectEqual(@as(u8, '#'), empty_backing[0]);
    try std.testing.expectEqual(@as(u8, '#'), empty_backing[1]);
    try std.testing.expectEqual(@as(u8, '#'), empty_backing[2]);

    var single_backing = [_]u8{'!'} ** 5;
    const single = str_error_r.strErrorR(4096, single_backing[2..3]);
    try std.testing.expectEqualStrings("", single);
    try std.testing.expectEqual(@as(u8, '!'), single_backing[1]);
    try std.testing.expectEqual(@as(u8, 0), single_backing[2]);
    try std.testing.expectEqual(@as(u8, '!'), single_backing[3]);
}

test "vsprintf minimal windows and logical-zero padding stay contained" {
    var zero_backing = [_]u8{'?'} ** 4;
    const zero_window = zero_backing[1..1];
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(zero_window, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, '?'), zero_backing[0]);
    try std.testing.expectEqual(@as(u8, '?'), zero_backing[1]);
    try std.testing.expectEqual(@as(u8, '?'), zero_backing[2]);

    var single_backing = [_]u8{'*'} ** 5;
    const single_window = single_backing[2..3];
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(single_window, "{d}", .{42}));
    try std.testing.expectEqual(@as(u8, '*'), single_backing[1]);
    try std.testing.expectEqual(@as(u8, 0), single_backing[2]);
    try std.testing.expectEqual(@as(u8, '*'), single_backing[3]);

    var padded_backing = [_]u8{'@'} ** 6;
    const padded_window = padded_backing[1..5];
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintfPad(padded_window, 0, "{s}", .{"id"}));
    try std.testing.expectEqual(@as(u8, '@'), padded_backing[0]);
    try std.testing.expectEqual(@as(u8, 0), padded_backing[1]);
    try std.testing.expectEqual(@as(u8, '@'), padded_backing[5]);
}

test "zalloc null-safe frees and minimal reallocation zeroing remain stable" {
    const allocator = std.testing.allocator;
    const Payload = struct {
        flag: bool,
        byte: u8,
    };

    var no_bytes: ?[]u8 = null;
    zalloc.zfreeBytes(allocator, &no_bytes);
    try std.testing.expect(no_bytes == null);

    var no_payload: ?*Payload = null;
    zalloc.zfreeValue(allocator, Payload, &no_payload);
    try std.testing.expect(no_payload == null);

    var first_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expect(first_bytes != null);
    first_bytes.?[0] = 0xaa;
    zalloc.zfreeBytes(allocator, &first_bytes);
    try std.testing.expect(first_bytes == null);
    zalloc.zfreeBytes(allocator, &first_bytes);
    try std.testing.expect(first_bytes == null);

    var second_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &second_bytes);
    try std.testing.expect(second_bytes != null);
    try std.testing.expectEqual(@as(u8, 0), second_bytes.?[0]);

    var first_payload: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expect(first_payload != null);
    first_payload.?.flag = true;
    first_payload.?.byte = 99;
    zalloc.zfreeValue(allocator, Payload, &first_payload);
    try std.testing.expect(first_payload == null);
    zalloc.zfreeValue(allocator, Payload, &first_payload);
    try std.testing.expect(first_payload == null);

    var second_payload: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &second_payload);
    try std.testing.expect(second_payload != null);
    try std.testing.expectEqual(false, second_payload.?.flag);
    try std.testing.expectEqual(@as(u8, 0), second_payload.?.byte);
}
