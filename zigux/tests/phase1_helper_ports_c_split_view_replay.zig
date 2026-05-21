const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "zero-sized slab allocations stay balanced around fail paths" {
    slab.kmalloc_nr_allocated = 0;

    const empty_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    defer slab.kfree(empty_bytes);
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const empty_array = slab.kmallocArray(0, 32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    defer slab.kfree(empty_array);
    try std.testing.expectEqual(@as(usize, 0), empty_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
}

test "strErrorR reuses offset views after a one-byte caller slice" {
    var backing = [_]u8{'#'} ** 64;

    const tiny = str_error_r.strErrorR(4096, backing[7..8]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, '#'), backing[6]);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);
    try std.testing.expectEqual(@as(u8, '#'), backing[8]);

    const full = str_error_r.strErrorR(4096, backing[7..58]);
    try std.testing.expectEqualStrings(
        "INTERNAL ERROR: strerror_r(4096, [buf], 51)=22",
        full,
    );
    try std.testing.expectEqual(@as(u8, '#'), backing[6]);
    try std.testing.expectEqual(@as(u8, '#'), backing[58]);
}

test "vsprintf split views keep outer storage intact across truncation and padding" {
    var backing = [_]u8{'x'} ** 18;
    const view = backing[3..12];

    const truncated = vsprintf.vscnprintf(view, "{s}", .{"alphabet"});
    try std.testing.expectEqual(@as(usize, 8), truncated);
    try std.testing.expectEqualStrings("alphabet", view[0..truncated]);
    try std.testing.expectEqual(@as(u8, 0), view[truncated]);
    try std.testing.expectEqual(@as(u8, 'x'), backing[2]);
    try std.testing.expectEqual(@as(u8, 'x'), backing[12]);

    const padded = vsprintf.scnprintfPad(view, view.len - 1, "id={d}", .{9});
    try std.testing.expectEqual(@as(usize, 7), padded);
    try std.testing.expectEqualStrings("id=9    ", view[0 .. view.len - 1]);
    try std.testing.expectEqual(@as(u8, 0), view[view.len - 1]);
    try std.testing.expectEqual(@as(u8, 'x'), backing[2]);
    try std.testing.expectEqual(@as(u8, 'x'), backing[12]);
}

test "zalloc zero-sized buffers and recreated values reset cleanly" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: usize,
        bytes: [3]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(usize, 0), value.?.count);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);
    value.?.count = 11;
    value.?.bytes = .{ 1, 2, 3 };
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(usize, 0), value.?.count);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);
}
