const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "formatters collapse zero-length and one-byte caller slots to terminator-only state" {
    var empty: [0]u8 = .{};
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(empty[0..], "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(empty[0..], "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintfPad(empty[0..], 7, "{s}", .{"zigux"}));

    var scn_slot = [_]u8{ 'A', 'B', 'C' };
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(scn_slot[1..2], "{s}", .{"zigux"}));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'A', 0, 'C' }, &scn_slot);

    var vscn_slot = [_]u8{ 'D', 'E', 'F' };
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(vscn_slot[1..2], "{s}", .{"zigux"}));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'D', 0, 'F' }, &vscn_slot);

    var pad_slot = [_]u8{ 'G', 'H', 'I' };
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintfPad(pad_slot[1..2], 9, "{s}", .{"zigux"}));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'G', 0, 'I' }, &pad_slot);
}

test "strErrorR collapses zero-length and one-byte caller slots to terminator-only state" {
    var empty: [0]u8 = .{};
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(13, empty[0..]));
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(4096, empty[0..]));

    var known_slot = [_]u8{ 'J', 'K', 'L' };
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(13, known_slot[1..2]));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'J', 0, 'L' }, &known_slot);

    var unknown_slot = [_]u8{ 'M', 'N', 'O' };
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(4096, unknown_slot[1..2]));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'M', 0, 'O' }, &unknown_slot);
}

test "slab and zalloc null-reset paths stay idempotent across empty teardown calls" {
    slab.kmalloc_nr_allocated = 0;
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const slab_bytes = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    var slab_optional: ?[]u8 = slab_bytes;
    slab.kfree(slab_optional);
    slab_optional = null;
    slab.kfree(slab_optional);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = null;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const Value = struct {
        first: u8,
        second: bool,
    };

    var value: ?*Value = null;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u8, 0), value.?.first);
    try std.testing.expectEqual(false, value.?.second);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
