const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab reclaims zero-extent helper allocations without counter drift" {
    slab.kmalloc_nr_allocated = 0;

    const zero_array = slab.kmallocArray(2, 0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR reuses exact caller windows without touching neighbors" {
    var known_backing = [_]u8{ '@', '@', '@', '@', '@', '@' };
    const known = str_error_r.strErrorR(0, known_backing[1..3]);
    try std.testing.expectEqualStrings("S", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '@', 'S', 0, '@', '@', '@' }, &known_backing);

    var unknown_backing = [_]u8{ '%', '%', '%', '%', '%', '%', '%' };
    const unknown = str_error_r.strErrorR(77, unknown_backing[2..7]);
    try std.testing.expectEqualStrings("INTE", unknown);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '%', '%', 'I', 'N', 'T', 'E', 0 }, &unknown_backing);
}

test "vsprintf can reuse the same interior window for exact-fit and reset renders" {
    var backing = [_]u8{ '?', '?', '?', '?', '?', '?', '?', '?', '?' };
    const window = backing[2..7];

    const first_written = vsprintf.scnprintfPad(window, 4, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 3), first_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '?', '?', 'x', 'y', ' ', ' ', 0, '?', '?' }, &backing);

    const second_written = vsprintf.vscnprintf(window, "{s}", .{"wxyz"});
    try std.testing.expectEqual(@as(usize, 4), second_written);
    try std.testing.expectEqualStrings("wxyz", window[0..second_written]);
    try std.testing.expectEqual(@as(u8, 0), window[second_written]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '?', '?', 'w', 'x', 'y', 'z', 0, '?', '?' }, &backing);

    const reset_written = vsprintf.scnprintfPad(window, 0, "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), reset_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '?', '?', 0, 'x', 'y', 'z', 0, '?', '?' }, &backing);
}

test "zalloc re-zeroes dirty bytes and idempotently resets optional owners" {
    const allocator = std.testing.allocator;
    const Node = struct {
        level: u8,
        active: bool,
        next: ?*u8,
    };

    var first_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, first_bytes.?);
    first_bytes.?[0] = 9;
    zalloc.zfreeBytes(allocator, &first_bytes);
    try std.testing.expect(first_bytes == null);
    zalloc.zfreeBytes(allocator, &first_bytes);
    try std.testing.expect(first_bytes == null);

    var second_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &second_bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, second_bytes.?);

    var node: ?*Node = try zalloc.zallocValue(allocator, Node);
    try std.testing.expectEqual(@as(u8, 0), node.?.level);
    try std.testing.expectEqual(false, node.?.active);
    try std.testing.expect(node.?.next == null);
    zalloc.zfreeValue(allocator, Node, &node);
    try std.testing.expect(node == null);
    zalloc.zfreeValue(allocator, Node, &node);
    try std.testing.expect(node == null);
}
