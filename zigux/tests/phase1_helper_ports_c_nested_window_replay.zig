const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab rebound zeroing survives dirty array frees" {
    slab.kmalloc_nr_allocated = 0;

    const dirty = slab.kmallocArray(2, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(dirty, 0x5a);
    slab.kfree(dirty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const rebound = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(rebound);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, rebound);
}

test "strErrorR nested slices only rewrite the addressed caller window" {
    var backing = [_]u8{0xaa} ** 10;

    const outer = str_error_r.strErrorR(4096, backing[1..8]);
    try std.testing.expectEqualStrings("INTERN", outer);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xaa, 'I', 'N', 'T', 'E', 'R', 'N', 0, 0xaa, 0xaa },
        &backing,
    );

    const inner = str_error_r.strErrorR(0, backing[3..6]);
    try std.testing.expectEqualStrings("Su", inner);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xaa, 'I', 'N', 'S', 'u', 0, 'N', 0, 0xaa, 0xaa },
        &backing,
    );
}

test "vsprintf nested slices keep outer caller bytes stable across rewrites" {
    var direct_backing = [_]u8{0xcc} ** 9;
    const outer_written = vsprintf.scnprintf(direct_backing[1..8], "{s}:{d}", .{ "host", 7 });
    try std.testing.expectEqual(@as(usize, 6), outer_written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xcc, 'h', 'o', 's', 't', ':', '7', 0, 0xcc },
        &direct_backing,
    );

    const inner_written = vsprintf.vscnprintf(direct_backing[3..6], "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 2), inner_written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xcc, 'h', 'o', 'o', 'k', 0, '7', 0, 0xcc },
        &direct_backing,
    );

    var padded_backing = [_]u8{0xdd} ** 8;
    const padded_written = vsprintf.scnprintfPad(padded_backing[2..6], 3, "{s}", .{"x"});
    try std.testing.expectEqual(@as(usize, 2), padded_written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xdd, 0xdd, 'x', ' ', ' ', 0, 0xdd, 0xdd },
        &padded_backing,
    );
}

test "zalloc byte slices re-zero after dirty frees" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0 }, bytes.?);

    @memset(bytes.?, 0x6d);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var rebound: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &rebound);
    try std.testing.expect(rebound != null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0 }, rebound.?);
}
