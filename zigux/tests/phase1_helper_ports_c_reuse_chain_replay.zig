const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps zero-sized and zeroed live allocations independently balanced" {
    slab.kmalloc_nr_allocated = 0;

    const zero = slab.kmallocBytes(0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    const zeroed = slab.kmallocArray(3, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        slab.kfree(zero);
        return error.TestUnexpectedResult;
    };

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 0), zero.len);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zero);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR rewrites a generated offset window with a shorter known message" {
    var backing = [_]u8{'!'} ** 18;
    const window = backing[3..12];

    const generated = str_error_r.strErrorR(4096, window);
    try std.testing.expectEqualStrings("INTERNAL", generated);
    try std.testing.expectEqual(@as(u8, 0), window[generated.len]);
    try std.testing.expectEqual(@as(u8, '!'), backing[2]);
    try std.testing.expectEqual(@as(u8, '!'), backing[12]);

    const known = str_error_r.strErrorR(0, window);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0), window[known.len]);
    try std.testing.expectEqual(@as(u8, '!'), backing[2]);
    try std.testing.expectEqual(@as(u8, '!'), backing[12]);
}

test "vsprintf rewrites a padded offset window with a shorter direct render" {
    var backing = [_]u8{'#'} ** 11;
    const window = backing[2..9];

    const padded = vsprintf.scnprintfPad(window, 6, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 5), padded);
    try std.testing.expectEqualStrings("xy    ", window[0..6]);
    try std.testing.expectEqual(@as(u8, 0), window[6]);

    const rewritten = vsprintf.vscnprintf(window, "{s}", .{"q"});
    try std.testing.expectEqual(@as(usize, 1), rewritten);
    try std.testing.expectEqual(@as(u8, 'q'), window[0]);
    try std.testing.expectEqual(@as(u8, 0), window[1]);
    try std.testing.expectEqual(@as(u8, ' '), window[2]);
    try std.testing.expectEqual(@as(u8, '#'), backing[1]);
    try std.testing.expectEqual(@as(u8, '#'), backing[9]);
}

test "zalloc re-zeroes byte slices and nested extern-union arrays across reuse" {
    const allocator = std.testing.allocator;

    var first_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expect(first_bytes != null);
    @memset(first_bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &first_bytes);
    try std.testing.expect(first_bytes == null);

    var second_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &second_bytes);
    try std.testing.expect(second_bytes != null);
    for (second_bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const Cell = extern union {
        pair: [2]u16,
        flag: u8,
    };
    const Payload = extern struct {
        tag: u16,
        cells: [2]Cell,
        tail: u8,
    };

    var first_value: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expect(first_value != null);
    first_value.?.tag = 7;
    first_value.?.cells[0].pair = .{ 1, 2 };
    first_value.?.cells[1].pair = .{ 3, 4 };
    first_value.?.tail = 9;
    zalloc.zfreeValue(allocator, Payload, &first_value);
    try std.testing.expect(first_value == null);

    var second_value: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &second_value);
    try std.testing.expect(second_value != null);
    try std.testing.expectEqual(@as(u16, 0), second_value.?.tag);
    try std.testing.expectEqual(@as(u16, 0), second_value.?.cells[0].pair[0]);
    try std.testing.expectEqual(@as(u16, 0), second_value.?.cells[0].pair[1]);
    try std.testing.expectEqual(@as(u16, 0), second_value.?.cells[1].pair[0]);
    try std.testing.expectEqual(@as(u16, 0), second_value.?.cells[1].pair[1]);
    try std.testing.expectEqual(@as(u8, 0), second_value.?.tail);
}
