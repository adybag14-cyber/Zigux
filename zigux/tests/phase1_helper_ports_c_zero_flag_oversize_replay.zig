const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "zero-flag helper islands keep neighboring caller windows bounded" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: usize,
        maybe_tail: ?usize,
        tag: [4]u8,
    };

    slab.kmalloc_nr_allocated = 0;
    const slab_bytes = slab.kmallocArray(3, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var zbuf: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &zbuf);
    for (zbuf.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(usize, 0), value.?.count);
    try std.testing.expect(value.?.maybe_tail == null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &value.?.tag);

    const err = str_error_r.strErrorR(22, zbuf.?[3..13]);
    try std.testing.expectEqualStrings("Invalid a", err);
    try std.testing.expectEqual(@as(u8, 0), zbuf.?[2]);
    try std.testing.expectEqual(@as(u8, 0), zbuf.?[12]);
    try std.testing.expectEqual(@as(u8, 0), zbuf.?[13]);

    const written = vsprintf.scnprintf(slab_bytes[4..15], "err={s}", .{err});
    try std.testing.expectEqual(@as(usize, 10), written);
    try std.testing.expectEqualStrings("err=Invali", slab_bytes[4 .. 4 + written]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[3]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[14]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[15]);

    zalloc.zfreeBytes(allocator, &zbuf);
    try std.testing.expect(zbuf == null);
    zalloc.zfreeBytes(allocator, &zbuf);
    try std.testing.expect(zbuf == null);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}

test "oversized vsprintf renders fail without consuming slab scratch windows" {
    const oversized = [_]u8{'x'} ** (vsprintf.max_render_bytes + 1);

    slab.kmalloc_nr_allocated = 0;
    const scratch = slab.kmallocBytes(16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(scratch);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(scratch, 0x5a);

    const failed_direct = vsprintf.vscnprintf(scratch[2..14], "{s}", .{oversized[0..]});
    try std.testing.expectEqual(@as(usize, 0), failed_direct);
    try std.testing.expectEqualSlices(u8, &[_]u8{0x5a} ** 16, scratch);

    const failed_padded = vsprintf.scnprintfPad(scratch[4..12], 6, "{s}", .{oversized[0..]});
    try std.testing.expectEqual(@as(usize, 0), failed_padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{0x5a} ** 16, scratch);

    const fallback = str_error_r.strErrorR(4096, scratch[1..9]);
    try std.testing.expectEqualStrings("INTERNA", fallback);
    try std.testing.expectEqual(@as(u8, 0x5a), scratch[0]);
    try std.testing.expectEqual(@as(u8, 0), scratch[8]);
    try std.testing.expectEqual(@as(u8, 0x5a), scratch[9]);
}
