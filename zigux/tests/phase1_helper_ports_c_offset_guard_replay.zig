const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C keeps offset views and reset guards contained" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocArray(3, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const plain = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(plain, 0xaa);
    slab.kfree(plain);
    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var message_backing: [12]u8 = @splat('#');
    const empty = str_error_r.strErrorR(13, message_backing[4..4]);
    try std.testing.expectEqualStrings("", empty);
    const expected_message_backing: [12]u8 = @splat('#');
    try std.testing.expectEqualSlices(u8, &expected_message_backing, &message_backing);

    const offset_message = str_error_r.strErrorR(13, message_backing[2..9]);
    try std.testing.expectEqualStrings("Permis", offset_message);
    try std.testing.expectEqualSlices(u8, "##", message_backing[0..2]);
    try std.testing.expectEqual(@as(u8, 0), message_backing[8]);
    try std.testing.expectEqualSlices(u8, "###", message_backing[9..12]);

    var padded_backing: [12]u8 = @splat('!');
    const padded_len = vsprintf.scnprintfPad(padded_backing[2..9], 6, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 6), padded_len);
    try std.testing.expectEqualSlices(u8, "!!", padded_backing[0..2]);
    try std.testing.expectEqualSlices(u8, "id    ", padded_backing[2..8]);
    try std.testing.expectEqual(@as(u8, 0), padded_backing[8]);
    try std.testing.expectEqualSlices(u8, "!!!", padded_backing[9..12]);

    var reset_backing: [6]u8 = @splat('?');
    const reset_len = vsprintf.scnprintfPad(reset_backing[1..5], 0, "{d}", .{42});
    try std.testing.expectEqual(@as(usize, 0), reset_len);
    try std.testing.expectEqual(@as(u8, '?'), reset_backing[0]);
    try std.testing.expectEqual(@as(u8, 0), reset_backing[1]);
    try std.testing.expectEqualSlices(u8, "????", reset_backing[2..6]);

    const allocator = std.testing.allocator;
    var bytes: ?[]u8 = null;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 5);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const Nested = struct {
        count: u16 = 9,
        enabled: bool = true,
        payload: [3]u8 = .{ 1, 2, 3 },
        maybe: ?u8 = 7,
    };

    var value: ?*Nested = try zalloc.zallocValue(allocator, Nested);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0 }, &value.?.payload);
    try std.testing.expectEqual(@as(?u8, null), value.?.maybe);
    zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expect(value == null);
}
