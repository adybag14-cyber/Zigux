const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 alloc-format edges import the live helper modules" {
    try std.testing.expect(@hasDecl(slab, "kmallocArray"));
    try std.testing.expect(@hasDecl(str_error_r, "strErrorR"));
    try std.testing.expect(@hasDecl(vsprintf, "vscnprintf"));
    try std.testing.expect(@hasDecl(zalloc, "zallocValue"));
}

test "phase1 alloc-format edges keep allocation helpers deterministic" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocArray(3, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocArray(3, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const allocator = std.testing.allocator;
    const Pair = struct {
        left: i16,
        right: bool,
    };

    var empty_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes != null);
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.?.len);

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expectEqual(@as(i16, 0), pair.?.left);
    try std.testing.expectEqual(false, pair.?.right);

    zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes == null);
    zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes == null);

    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);
    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);
}

test "phase1 alloc-format edges keep message rendering aligned" {
    var tiny_error: [8]u8 = undefined;
    try std.testing.expectEqualStrings("Permiss", str_error_r.strErrorR(13, &tiny_error));

    var zero_error: [0]u8 = undefined;
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(2, &zero_error).len);

    var exact_render: [10]u8 = undefined;
    const exact_len = vsprintf.vscnprintf(&exact_render, "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(@as(usize, 7), exact_len);
    try std.testing.expectEqualStrings("zigux:7", exact_render[0..exact_len]);

    var truncated_render: [6]u8 = undefined;
    const truncated_len = vsprintf.scnprintf(&truncated_render, "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(@as(usize, 5), truncated_len);
    try std.testing.expectEqualStrings("zigux", truncated_render[0..truncated_len]);
    try std.testing.expectEqual(@as(u8, 0), truncated_render[truncated_len]);

    var zero_render: [0]u8 = undefined;
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(&zero_render, "{d}", .{1}));

    var padded_render: [6]u8 = undefined;
    const padded_len = vsprintf.scnprintfPad(&padded_render, 12, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 4), padded_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'd', ' ', ' ', ' ', 0 }, &padded_render);
}
