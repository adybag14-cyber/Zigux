const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-byte bytes and arrays balance the counter beside a live sibling allocation" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const sibling = slab.kmallocBytes(2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 2), sibling.len);
    try std.testing.expectEqual(@as(u8, 0), sibling[0]);
    try std.testing.expectEqual(@as(u8, 0), sibling[1]);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    const zero_array = slab.kmallocArray(2, 0, slab.GFP_KERNEL) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 3), slab.kmalloc_nr_allocated);

    slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    slab.kfree(sibling);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR two-slot windows keep one byte of payload and fence both gutters" {
    var known = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd };
    const known_rendered = str_error_r.strErrorR(13, known[1..3]);
    try std.testing.expectEqualStrings("P", known_rendered);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 'P', 0x00, 0xdd }, &known);

    var fallback = [_]u8{ 0x11, 0x22, 0x33, 0x44 };
    const fallback_rendered = str_error_r.strErrorR(4096, fallback[1..3]);
    try std.testing.expectEqualStrings("I", fallback_rendered);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x11, 'I', 0x00, 0x44 }, &fallback);
}

test "vsprintf two-slot windows contain direct, alias, and padded writes" {
    var direct = [_]u8{ 0x90, 0x91, 0x92, 0x93 };
    const direct_written = vsprintf.scnprintf(direct[1..3], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 1), direct_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x90, 'z', 0x00, 0x93 }, &direct);

    var alias = [_]u8{ 0xa0, 0xa1, 0xa2, 0xa3 };
    const alias_written = vsprintf.vscnprintf(alias[1..3], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 1), alias_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa0, 'z', 0x00, 0xa3 }, &alias);

    var padded = [_]u8{ 0xb0, 0xb1, 0xb2, 0xb3 };
    const padded_written = vsprintf.scnprintfPad(padded[1..3], 2, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 1), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xb0, 'x', 0x00, 0xb3 }, &padded);
}

test "zalloc bytes and values reset cleanly across repeated two-slot owners" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u8,
        right: u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 2);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);
    bytes.?[0] = 0xfe;
    bytes.?[1] = 0xed;

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u8, 0), pair.?.left);
    try std.testing.expectEqual(@as(u8, 0), pair.?.right);
    pair.?.left = 7;
    pair.?.right = 9;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expect(pair != null);

    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);

    var next_pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &next_pair);
    try std.testing.expectEqual(@as(u8, 0), next_pair.?.left);
    try std.testing.expectEqual(@as(u8, 0), next_pair.?.right);
}
