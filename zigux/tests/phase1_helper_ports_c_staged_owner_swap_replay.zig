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

test "staged owner swap preserves slab sentinels while zalloc records strerror output" {
    slab.kmalloc_nr_allocated = 0;

    const slab_frame = slab.kmallocBytes(80, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_frame);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(slab_frame);

    const slab_window = slab_frame[6..44];
    const fallback = str_error_r.strErrorR(7001, slab_window);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(7001, [buf", fallback);
    try std.testing.expectEqual(@as(u8, 0), slab_window[fallback.len]);
    try expectZeroed(slab_frame[0..6]);
    try expectZeroed(slab_frame[44..]);

    var z_owner: ?[]u8 = try zalloc.zallocBytes(std.testing.allocator, 56);
    defer zalloc.zfreeBytes(std.testing.allocator, &z_owner);
    try expectZeroed(z_owner.?);

    const copied = @min(fallback.len, z_owner.?.len - 10);
    @memcpy(z_owner.?[5 .. 5 + copied], fallback[0..copied]);
    z_owner.?[5 + copied] = 0;
    try std.testing.expectEqualStrings(fallback[0..copied], z_owner.?[5 .. 5 + copied]);
    try expectZeroed(z_owner.?[0..5]);
    try expectZeroed(z_owner.?[5 + copied + 1 ..]);

    const formatted = vsprintf.scnprintf(slab_frame[45..66], "copy={d}:alloc={d}", .{ copied, slab.kmalloc_nr_allocated });
    try std.testing.expectEqual(@as(usize, 15), formatted);
    try std.testing.expectEqualStrings("copy=37:alloc=1", slab_frame[45 .. 45 + formatted]);
    try std.testing.expectEqual(@as(u8, 0), slab_frame[45 + formatted]);
    try expectZeroed(slab_frame[66..]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc owner reuse feeds padded slab array summary and resets cleanly" {
    slab.kmalloc_nr_allocated = 0;

    var owner: ?[]u8 = try zalloc.zallocBytes(std.testing.allocator, 36);
    defer zalloc.zfreeBytes(std.testing.allocator, &owner);
    try expectZeroed(owner.?);

    const first = vsprintf.vscnprintf(owner.?[3..23], "stage:{d}:{s}", .{ 2, "swap" });
    try std.testing.expectEqual(@as(usize, 12), first);
    try std.testing.expectEqualStrings("stage:2:swap", owner.?[3 .. 3 + first]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[3 + first]);
    try expectZeroed(owner.?[0..3]);
    try expectZeroed(owner.?[23..]);

    zalloc.zfreeBytes(std.testing.allocator, &owner);
    try std.testing.expect(owner == null);

    owner = try zalloc.zallocBytes(std.testing.allocator, 36);
    try expectZeroed(owner.?);

    const short = str_error_r.strErrorR(0, owner.?[4..14]);
    try std.testing.expectEqualStrings("Success", short);
    try std.testing.expectEqual(@as(u8, 0), owner.?[4 + short.len]);
    try expectZeroed(owner.?[0..4]);
    try expectZeroed(owner.?[14..]);

    const slab_array = slab.kmallocArray(4, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(slab_array);

    const padded = vsprintf.scnprintfPad(slab_array[8..24], 11, "ok:{s}", .{short});
    try std.testing.expect(padded == 11 or padded == 10);
    try std.testing.expectEqualStrings("ok:Success ", slab_array[8..19]);
    try std.testing.expectEqual(@as(u8, 0), slab_array[19]);
    try expectZeroed(slab_array[0..8]);
    try expectZeroed(slab_array[24..]);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
