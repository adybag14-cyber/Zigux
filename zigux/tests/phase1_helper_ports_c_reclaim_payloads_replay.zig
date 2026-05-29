const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports c keep reclaim payload handoffs bounded" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slab_payload = slab.kmallocBytes(13, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_payload);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &([_]u8{0} ** 13), slab_payload);

    const rendered = vsprintf.scnprintfPad(slab_payload[1..12], 7, "err={d}", .{22});
    try std.testing.expectEqual(@as(usize, 6), rendered);
    try std.testing.expectEqual(@as(u8, 0), slab_payload[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'e', 'r', 'r', '=', '2', '2', ' ', 0 }, slab_payload[1..9]);
    try std.testing.expectEqual(@as(u8, 0), slab_payload[12]);

    var scratch: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expectEqualSlices(u8, &([_]u8{0} ** 24), scratch.?);

    const message = str_error_r.strErrorR(13, scratch.?[3..15]);
    try std.testing.expectEqualStrings("Permission ", message);
    try std.testing.expectEqual(@as(u8, 0), scratch.?[15 - 1]);
    try std.testing.expectEqualSlices(u8, &([_]u8{0} ** 3), scratch.?[0..3]);

    slab.kfree(slab_payload);
    slab_payload = &[_]u8{};
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
}

test "phase1 helper ports c reject unreclaimable scratch without disturbing owned buffers" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owned: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    defer zalloc.zfreeBytes(allocator, &owned);
    const padded = vsprintf.scnprintfPad(owned.?[2..14], 5, "{s}", .{"io"});
    try std.testing.expectEqual(@as(usize, 4), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'o', ' ', ' ', ' ', 0 }, owned.?[2..8]);

    try std.testing.expect(slab.kmallocBytes(8, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var tiny = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const fallback = str_error_r.strErrorR(7777, tiny[1..3]);
    try std.testing.expectEqualStrings("I", fallback);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 'I', 0, 0xaa }, &tiny);

    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);
}
