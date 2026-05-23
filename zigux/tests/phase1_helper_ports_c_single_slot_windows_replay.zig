const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab single-slot allocations keep counters balanced" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(1, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const byte = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(byte);

    try std.testing.expectEqual(@as(usize, 1), byte.len);
    try std.testing.expectEqual(@as(u8, 0), byte[0]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR preserves outer sentinels around one-slot views" {
    var one_slot = [_]u8{ 0xaa, 0xaa, 0xaa };
    const empty = str_error_r.strErrorR(0, one_slot[1..2]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0, 0xaa }, &one_slot);

    var two_slot = [_]u8{ 0xbb, 0xbb, 0xbb, 0xbb };
    const short = str_error_r.strErrorR(0, two_slot[1..3]);
    try std.testing.expectEqualStrings("S", short);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xbb, 'S', 0, 0xbb }, &two_slot);
}

test "vsprintf single-slot caller windows still reserve a terminator" {
    var empty_window = [_]u8{0xcc};
    const empty_written = vsprintf.vscnprintf(&empty_window, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqual(@as(u8, 0), empty_window[0]);

    var one_char = [_]u8{ 0xdd, 0xdd };
    const one_char_written = vsprintf.scnprintfPad(&one_char, 1, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 1), one_char_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 0 }, &one_char);
}

test "zalloc single-slot helpers zero and clear optionals" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 1), bytes.?.len);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[0]);

    const Tiny = struct {
        tag: u8,
    };

    var value: ?*Tiny = try zalloc.zallocValue(allocator, Tiny);
    defer zalloc.zfreeValue(allocator, Tiny, &value);
    try std.testing.expectEqual(@as(u8, 0), value.?.tag);

    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    zalloc.zfreeValue(allocator, Tiny, &value);
    zalloc.zfreeValue(allocator, Tiny, &value);
    try std.testing.expect(value == null);
}
