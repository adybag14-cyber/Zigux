const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab staggered frees keep live allocation accounting aligned" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (first) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const second = slab.kmallocArray(2, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const replacement = slab.kmallocArray(1, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(replacement);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (replacement) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "strErrorR reuses dirty caller storage without escaping the new subview" {
    var backing = [_]u8{0xaa} ** 24;

    const wide = str_error_r.strErrorR(4096, backing[4..16]);
    try std.testing.expectEqualStrings("INTERNAL ER", wide);
    try std.testing.expectEqual(@as(u8, 'I'), backing[4]);
    try std.testing.expectEqual(@as(u8, 0), backing[15]);

    const inner = str_error_r.strErrorR(0, backing[6..14]);
    try std.testing.expectEqualStrings("Success", inner);
    try std.testing.expectEqual(@as(u8, 'N'), backing[5]);
    try std.testing.expectEqual(@as(u8, 0), backing[13]);
    try std.testing.expectEqual(@as(u8, 'R'), backing[14]);
    try std.testing.expectEqual(@as(u8, 0), backing[15]);
}

test "vsprintf nested subviews keep earlier outer bytes stable across reuse" {
    var backing = [_]u8{0xcc} ** 12;
    const outer = backing[2..10];
    const outer_written = vsprintf.scnprintf(outer, "{s}", .{"tooling"});
    try std.testing.expectEqual(@as(usize, 7), outer_written);
    try std.testing.expectEqual(@as(u8, 't'), backing[2]);
    try std.testing.expectEqual(@as(u8, 'o'), backing[3]);
    try std.testing.expectEqual(@as(u8, 'g'), backing[8]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);

    const inner = backing[4..8];
    const inner_written = vsprintf.scnprintfPad(inner, 3, "{s}", .{"x"});
    try std.testing.expectEqual(@as(usize, 2), inner_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 't', 'o', 'x', ' ', ' ', 0, 'g', 0, 0xcc, 0xcc }, &backing);
}

test "zalloc fresh allocations stay zeroed while neighboring live values remain dirty" {
    const allocator = std.testing.allocator;
    const Value = extern struct {
        bytes: [2]u8,
        mark: u16,
    };

    var dirty_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(dirty_bytes != null);
    @memset(dirty_bytes.?, 0x5a);

    var live_value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &live_value);
    live_value.?.bytes = .{ 7, 8 };
    live_value.?.mark = 9;

    zalloc.zfreeBytes(allocator, &dirty_bytes);
    try std.testing.expect(dirty_bytes == null);

    var fresh_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &fresh_bytes);
    for (fresh_bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expectEqual(@as([2]u8, .{ 7, 8 }), live_value.?.bytes);
    try std.testing.expectEqual(@as(u16, 9), live_value.?.mark);

    zalloc.zfreeValue(allocator, Value, &live_value);
    try std.testing.expect(live_value == null);

    var fresh_value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &fresh_value);
    try std.testing.expectEqual(std.mem.zeroes(Value), fresh_value.?.*);
}
