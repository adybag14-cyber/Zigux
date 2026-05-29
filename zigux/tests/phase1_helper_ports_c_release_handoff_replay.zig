const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectFilled(bytes: []const u8, expected: u8) !void {
    for (bytes) |value| {
        try std.testing.expectEqual(expected, value);
    }
}

test "released slab buffer does not disturb later zalloc formatting handoff" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_window = slab.kmallocBytes(40, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectFilled(slab_window, 0);

    const slab_written = vsprintf.scnprintf(slab_window, "slab:{d}", .{17});
    try std.testing.expectEqualStrings("slab:17", slab_window[0..slab_written]);
    slab.kfree(slab_window);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    try expectFilled(zbytes.?, 0);

    const strerror = str_error_r.strErrorR(12, zbytes.?[8..32]);
    try std.testing.expectEqualStrings("Cannot allocate memory", strerror);
    try expectFilled(zbytes.?[0..8], 0);
    try std.testing.expectEqual(@as(u8, 0), zbytes.?[8 + strerror.len]);

    const rendered = vsprintf.vscnprintf(zbytes.?[0..16], "reuse:{d}", .{slab.kmalloc_nr_allocated});
    try std.testing.expectEqualStrings("reuse:0", zbytes.?[0..rendered]);
    try std.testing.expectEqual(@as(u8, 0), zbytes.?[rendered]);
}

test "staggered slab and zalloc subviews preserve neighboring sentinels" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const owned = slab.kmallocArray(64, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(owned);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectFilled(owned, 0);

    @memset(owned, 0xaa);
    const err_text = str_error_r.strErrorR(22, owned[16..36]);
    try std.testing.expectEqualStrings("Invalid argument", err_text);
    try expectFilled(owned[0..16], 0xaa);
    try expectFilled(owned[37..], 0xaa);
    try std.testing.expectEqual(@as(u8, 0), owned[16 + err_text.len]);

    var scratch: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &scratch);
    try expectFilled(scratch.?, 0);

    @memset(scratch.?, 0xbb);
    const formatted = vsprintf.scnprintfPad(scratch.?[4..24], 16, "{s}:{d}", .{ err_text, slab.kmalloc_nr_allocated });
    try std.testing.expectEqual(@as(usize, 16), formatted);
    try std.testing.expectEqualStrings("Invalid argument", scratch.?[4 .. 4 + formatted]);
    try std.testing.expectEqual(@as(u8, 0), scratch.?[20]);
    try expectFilled(scratch.?[0..4], 0xbb);
    try expectFilled(scratch.?[21..], 0xbb);
}

test "zero-length views and idempotent frees keep helper ownership independent" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const zero_slab = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_slab.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var backing = [_]u8{0xcc} ** 4;
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(13, backing[0..0]).len);
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(backing[0..0], "{s}", .{"ignored"}));
    try expectFilled(&backing, 0xcc);

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes != null);
    try std.testing.expectEqual(@as(usize, 0), zbytes.?.len);

    zalloc.zfreeBytes(allocator, &zbytes);
    zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes == null);

    slab.kfree(zero_slab);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
