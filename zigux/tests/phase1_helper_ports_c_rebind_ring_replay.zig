const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectZeroed(bytes: []const u8) !void {
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "slab caller window rebinds from formatted text into strerror and zalloc summary" {
    slab.kmalloc_nr_allocated = 0;

    const frame = slab.kmallocBytes(72, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(frame);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(frame);

    const caller = frame[9..35];
    const first_written = vsprintf.scnprintf(caller, "slot={d}:len={d}", .{ 3, caller.len });
    try std.testing.expectEqual(@as(usize, 13), first_written);
    try std.testing.expectEqualStrings("slot=3:len=26", caller[0..first_written]);
    try std.testing.expectEqual(@as(u8, 0), caller[first_written]);
    try expectZeroed(frame[0..9]);
    try expectZeroed(frame[35..]);

    const err = str_error_r.strErrorR(12, caller);
    try std.testing.expectEqualStrings("Cannot allocate memory", err);
    try std.testing.expectEqual(@as(u8, 0), caller[err.len]);
    try expectZeroed(frame[0..9]);
    try expectZeroed(frame[35..]);

    var summary: ?[]u8 = try zalloc.zallocBytes(std.testing.allocator, 40);
    defer zalloc.zfreeBytes(std.testing.allocator, &summary);
    try expectZeroed(summary.?);

    const padded = vsprintf.scnprintfPad(summary.?[4..24], 12, "err={s}", .{err[0..6]});
    try std.testing.expect(padded == 12 or padded == 11);
    try std.testing.expectEqualStrings("err=Cannot  ", summary.?[4..16]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[16]);
    try expectZeroed(summary.?[0..4]);
    try expectZeroed(summary.?[24..]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc ring is released and rebound while slab array accounting remains stable" {
    slab.kmalloc_nr_allocated = 0;

    var ring: ?[]u8 = try zalloc.zallocBytes(std.testing.allocator, 48);
    defer zalloc.zfreeBytes(std.testing.allocator, &ring);
    try expectZeroed(ring.?);

    const fallback = str_error_r.strErrorR(5000, ring.?[5..45]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(5000, [buf],", fallback);
    try std.testing.expectEqual(@as(u8, 0), ring.?[5 + fallback.len]);
    try expectZeroed(ring.?[0..5]);
    try expectZeroed(ring.?[45..]);

    zalloc.zfreeBytes(std.testing.allocator, &ring);
    try std.testing.expect(ring == null);

    ring = try zalloc.zallocBytes(std.testing.allocator, 48);
    try expectZeroed(ring.?);
    const shorter = vsprintf.vscnprintf(ring.?[8..23], "ok:{d}", .{fallback.len});
    try std.testing.expectEqual(@as(usize, 5), shorter);
    try std.testing.expectEqualStrings("ok:39", ring.?[8 .. 8 + shorter]);
    try std.testing.expectEqual(@as(u8, 0), ring.?[8 + shorter]);
    try expectZeroed(ring.?[0..8]);
    try expectZeroed(ring.?[23..]);

    const slab_array = slab.kmallocArray(3, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(slab_array);

    const copied = @min(shorter, slab_array.len - 1);
    @memcpy(slab_array[0..copied], ring.?[8 .. 8 + copied]);
    slab_array[copied] = 0;
    try std.testing.expectEqualStrings("ok:39", slab_array[0..copied]);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
