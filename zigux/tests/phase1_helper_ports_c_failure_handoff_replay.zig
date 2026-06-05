const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "allocation failures leave owned zalloc and caller windows intact" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owned: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    defer zalloc.zfreeBytes(allocator, &owned);

    for (owned.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const formatted = vsprintf.scnprintf(owned.?[2..12], "owned={d}", .{7});
    try std.testing.expectEqual(@as(usize, 7), formatted);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, owned.?[0..2]);
    try std.testing.expectEqualStrings("owned=7", owned.?[2 .. 2 + formatted]);
    try std.testing.expectEqual(@as(u8, 0), owned.?[2 + formatted]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0 }, owned.?[10..16]);

    var fallback_backing: [40]u8 = @splat(0x44);
    const fallback_window = fallback_backing[5..30];
    const fallback = str_error_r.strErrorR(8192, fallback_window);
    try std.testing.expectEqual(@as(usize, fallback_window.len - 1), fallback.len);
    try std.testing.expect(std.mem.startsWith(u8, fallback, "INTERNAL ERROR: strerror"));
    try std.testing.expectEqual(@as(u8, 0x44), fallback_backing[4]);
    try std.testing.expectEqual(@as(u8, 0), fallback_backing[29]);
    try std.testing.expectEqual(@as(u8, 0x44), fallback_backing[30]);

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);
    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "empty slab views and exact zalloc views hand off without sentinel drift" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var guard = [_]u8{0xaa};
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(guard[0..0], "{s}", .{"ignored"}));
    try std.testing.expectEqual(@as(u8, 0xaa), guard[0]);

    const slab_bytes = slab.kmallocBytes(14, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    defer slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    const padded = vsprintf.scnprintfPad(slab_bytes[1..8], 3, "x{d}", .{5});
    try std.testing.expectEqual(@as(usize, 3), padded);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', '5', ' ', 0 }, slab_bytes[1..5]);
    for (slab_bytes[5..]) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var exact: ?[]u8 = try zalloc.zallocBytes(allocator, 12);
    defer zalloc.zfreeBytes(allocator, &exact);
    const success = str_error_r.strErrorR(0, exact.?[2..10]);
    try std.testing.expectEqualStrings("Success", success);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, exact.?[0..2]);
    try std.testing.expectEqual(@as(u8, 0), exact.?[9]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, exact.?[10..12]);

    const Tail = struct {
        len: usize,
        ok: bool,
        code: u8,
    };
    var tail: ?*Tail = try zalloc.zallocValue(allocator, Tail);
    defer zalloc.zfreeValue(allocator, Tail, &tail);
    try std.testing.expectEqual(@as(usize, 0), tail.?.len);
    try std.testing.expectEqual(false, tail.?.ok);
    try std.testing.expectEqual(@as(u8, 0), tail.?.code);

    zalloc.zfreeValue(allocator, Tail, &tail);
    try std.testing.expect(tail == null);
}
