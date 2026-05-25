const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps threshold-sized allocations zeroed and balanced" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const one = slab.kmallocArray(1, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), one.len);
    try std.testing.expectEqual(@as(u8, 0), one[0]);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(one);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps threshold caller windows terminated without neighbor writes" {
    var backing = [_]u8{0xaa} ** 24;

    const one_byte = str_error_r.strErrorR(2, backing[5..6]);
    try std.testing.expectEqualStrings("", one_byte);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[4]);
    try std.testing.expectEqual(@as(u8, 0), backing[5]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[6]);

    @memset(backing[0..], 0xbb);
    const threshold = str_error_r.strErrorR(4096, backing[8..12]);
    try std.testing.expectEqualStrings("INT", threshold);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[7]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'I', 'N', 'T', 0 }, backing[8..12]);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[12]);
}

test "vsprintf keeps threshold windows isolated across exact and padded renders" {
    var exact_backing = [_]u8{0xcc} ** 10;
    const exact_written = vsprintf.scnprintf(exact_backing[2..6], "{s}", .{"wide"});
    try std.testing.expectEqual(@as(usize, 3), exact_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'w', 'i', 'd', 0 }, exact_backing[2..6]);
    try std.testing.expectEqual(@as(u8, 0xcc), exact_backing[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), exact_backing[6]);

    var pad_backing = [_]u8{0xdd} ** 9;
    const pad_written = vsprintf.scnprintfPad(pad_backing[1..5], 1, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 1), pad_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 0, 0xdd, 0xdd }, pad_backing[1..5]);
    try std.testing.expectEqual(@as(u8, 0xdd), pad_backing[0]);
    try std.testing.expectEqual(@as(u8, 0xdd), pad_backing[5]);
}

test "zalloc keeps zero-length and single-value thresholds reusable" {
    const allocator = std.testing.allocator;
    const Threshold = struct {
        count: u8,
        ready: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expectEqual(@as(usize, 1), bytes.?.len);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[0]);

    var threshold: ?*Threshold = try zalloc.zallocValue(allocator, Threshold);
    defer zalloc.zfreeValue(allocator, Threshold, &threshold);
    try std.testing.expectEqual(@as(u8, 0), threshold.?.count);
    try std.testing.expectEqual(false, threshold.?.ready);
    threshold.?.* = .{ .count = 1, .ready = true };

    zalloc.zfreeValue(allocator, Threshold, &threshold);
    try std.testing.expect(threshold == null);

    threshold = try zalloc.zallocValue(allocator, Threshold);
    try std.testing.expectEqual(@as(u8, 0), threshold.?.count);
    try std.testing.expectEqual(false, threshold.?.ready);
}
