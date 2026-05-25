const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps alternating zeroed slices and counter balance isolated" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zero_bytes = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zero_bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const zero_array = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zero_array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
}

test "strErrorR alternates exact and tiny caller slices without leaking neighbors" {
    var backing = [_]u8{0xaa} ** 24;

    const exact_view = backing[4..12];
    const exact_rendered = str_error_r.strErrorR(0, exact_view);
    try std.testing.expectEqualStrings("Success", exact_rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[3]);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[12]);

    @memset(backing[0..], 0xbb);
    const tiny_view = backing[9..10];
    const tiny_rendered = str_error_r.strErrorR(4096, tiny_view);
    try std.testing.expectEqualStrings("", tiny_rendered);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[8]);
    try std.testing.expectEqual(@as(u8, 0), tiny_view[0]);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[10]);
}

test "vsprintf keeps alternating offset slices fenced across truncation and padding" {
    var scn_backing = [_]u8{0xaa} ** 12;
    const scn_view = scn_backing[2..7];
    const scn_written = vsprintf.scnprintf(scn_view, "{s}", .{"tooling"});
    try std.testing.expectEqual(@as(usize, 4), scn_written);
    try std.testing.expectEqualStrings("tool", scn_view[0..scn_written]);
    try std.testing.expectEqual(@as(u8, 0), scn_view[scn_written]);
    try std.testing.expectEqual(@as(u8, 0xaa), scn_backing[1]);
    try std.testing.expectEqual(@as(u8, 0xaa), scn_backing[7]);

    var pad_backing = [_]u8{0xcc} ** 12;
    const pad_view = pad_backing[3..9];
    const pad_written = vsprintf.scnprintfPad(pad_view, 4, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 3), pad_written);
    try std.testing.expectEqualStrings("id ", pad_view[0..pad_written]);
    try std.testing.expectEqual(@as(u8, ' '), pad_view[3]);
    try std.testing.expectEqual(@as(u8, 0), pad_view[4]);
    try std.testing.expectEqual(@as(u8, 0xcc), pad_backing[2]);
    try std.testing.expectEqual(@as(u8, 0xcc), pad_backing[9]);
}

test "zalloc alternates byte and value ownership with clean resets" {
    const allocator = std.testing.allocator;
    const Value = struct {
        left: u16,
        right: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    @memset(bytes.?, 0xaa);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u16, 0), value.?.left);
    try std.testing.expectEqual(@as(u16, 0), value.?.right);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    var fresh: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &fresh);
    for (fresh.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}
