const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "helper ports C reuse tail windows without touching sentinels" {
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocBytes(24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(slab_bytes, 0xa5);
    const err_window = slab_bytes[3..20];
    const err = str_error_r.strErrorR(22, err_window);
    try std.testing.expectEqualStrings("Invalid argument", err);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_bytes[2]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[19]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_bytes[20]);

    @memset(slab_bytes, 0xcc);
    const fmt_window = slab_bytes[5..16];
    const written = vsprintf.scnprintfPad(fmt_window, fmt_window.len - 1, "tail={d}", .{7});
    try std.testing.expectEqual(@as(usize, 10), written);
    try std.testing.expectEqualSlices(u8, "tail=7    ", fmt_window[0 .. fmt_window.len - 1]);
    try std.testing.expectEqual(@as(u8, 0xcc), slab_bytes[4]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[15]);
    try std.testing.expectEqual(@as(u8, 0xcc), slab_bytes[16]);

    slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "zalloc owners can be released and reused beside formatted tails" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(bytes.?, 0x7b);
    const known = str_error_r.strErrorR(2, bytes.?[2..12]);
    try std.testing.expectEqualStrings("No such f", known);
    try std.testing.expectEqual(@as(u8, 0x7b), bytes.?[1]);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[11]);
    try std.testing.expectEqual(@as(u8, 0x7b), bytes.?[12]);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 18);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(bytes.?, 0x44);
    const written = vsprintf.vscnprintf(bytes.?[4..10], "{s}", .{"reuse"});
    try std.testing.expectEqual(@as(usize, 5), written);
    try std.testing.expectEqualStrings("reuse", bytes.?[4..9]);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[9]);
    try std.testing.expectEqual(@as(u8, 0x44), bytes.?[3]);
    try std.testing.expectEqual(@as(u8, 0x44), bytes.?[10]);
}

test "zero-length slab slices and value owners keep release accounting independent" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const Value = struct {
        count: u32,
        enabled: bool,
    };

    const allocator = std.testing.allocator;
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    var backing: [1]u8 = .{0xee};
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(4096, backing[0..0]).len);
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(backing[0..0], "{s}", .{"unused"}));
    try std.testing.expectEqual(@as(u8, 0xee), backing[0]);
}
