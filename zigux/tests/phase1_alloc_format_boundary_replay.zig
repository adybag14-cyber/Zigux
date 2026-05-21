const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 alloc-format boundary replay keeps slab and zalloc null-safe edges aligned" {
    slab.kmalloc_nr_allocated = 0;
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(2, 4, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 0), zeroed.len);
    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const allocator = std.testing.allocator;
    var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(zero_bytes != null);
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.?.len);
    zalloc.zfreeBytes(allocator, &zero_bytes);
    try std.testing.expect(zero_bytes == null);
    zalloc.zfreeBytes(allocator, &zero_bytes);
    try std.testing.expect(zero_bytes == null);

    const ZeroValue = struct {
        count: u8,
        enabled: bool,
    };
    var value: ?*ZeroValue = try zalloc.zallocValue(allocator, ZeroValue);
    try std.testing.expectEqual(@as(u8, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);
    zalloc.zfreeValue(allocator, ZeroValue, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, ZeroValue, &value);
    try std.testing.expect(value == null);
}

test "phase1 alloc-format boundary replay keeps str_error_r truncation edges aligned" {
    var empty: [0]u8 = .{};
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(13, &empty));

    var single: [1]u8 = undefined;
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(13, &single));
    try std.testing.expectEqual(@as(u8, 0), single[0]);

    var tiny_known: [5]u8 = undefined;
    try std.testing.expectEqualStrings("Perm", str_error_r.strErrorR(13, &tiny_known));
    try std.testing.expectEqual(@as(u8, 0), tiny_known[4]);

    var tiny_unknown: [8]u8 = undefined;
    try std.testing.expectEqualStrings("INTERNA", str_error_r.strErrorR(4096, &tiny_unknown));
    try std.testing.expectEqual(@as(u8, 0), tiny_unknown[7]);
}

test "phase1 alloc-format boundary replay keeps vsprintf buffer limits aligned" {
    var empty: [0]u8 = .{};
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(&empty, "{s}", .{"zigux"}));

    var one: [1]u8 = undefined;
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(&one, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, 0), one[0]);

    var truncated: [5]u8 = undefined;
    const truncated_len = vsprintf.scnprintf(&truncated, "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 4), truncated_len);
    try std.testing.expectEqualStrings("abcd", truncated[0..truncated_len]);
    try std.testing.expectEqual(@as(u8, 0), truncated[4]);

    var padded_zero: [4]u8 = undefined;
    const padded_zero_len = vsprintf.scnprintfPad(&padded_zero, 0, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), padded_zero_len);
    try std.testing.expectEqual(@as(u8, 0), padded_zero[0]);

    var clipped_pad: [5]u8 = undefined;
    const clipped_pad_len = vsprintf.scnprintfPad(&clipped_pad, 99, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 3), clipped_pad_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', 0 }, &clipped_pad);

    var alias: [6]u8 = undefined;
    const alias_len = vsprintf.vscnprintf(&alias, "{s}", .{"hello!"});
    try std.testing.expectEqual(@as(usize, 5), alias_len);
    try std.testing.expectEqualStrings("hello", alias[0..alias_len]);
}
