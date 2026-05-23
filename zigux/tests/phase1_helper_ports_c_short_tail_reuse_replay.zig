const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab free ordering and failed reclaimless retries preserve allocation counts" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const second = slab.kmallocArray(1, 1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), first[0]);

    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(1, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR rewrites short interior windows without touching neighbors" {
    var known_window = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    const known = str_error_r.strErrorR(13, known_window[1..4]);
    try std.testing.expectEqualStrings("Pe", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 'P', 'e', 0, 0xaa }, &known_window);

    var unknown_window = [_]u8{ 0xbb, 0xbb, 0xbb, 0xbb, 0xbb };
    const unknown = str_error_r.strErrorR(4096, unknown_window[1..3]);
    try std.testing.expectEqualStrings("I", unknown);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xbb, 'I', 0, 0xbb, 0xbb }, &unknown_window);
}

test "vsprintf short rewrites reset the tail terminator and preserve outer bytes" {
    var window = [_]u8{ 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc };
    const padded = vsprintf.scnprintfPad(window[1..7], 5, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 4), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 'x', 'y', ' ', ' ', ' ', 0, 0xcc }, &window);

    const rewritten = vsprintf.vscnprintf(window[1..7], "{s}", .{"z"});
    try std.testing.expectEqual(@as(usize, 1), rewritten);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 'z', 0, ' ', ' ', ' ', 0, 0xcc }, &window);
}

test "zalloc double free stays null and fresh allocations re-zero dirty state" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [3]u8,
        flag: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);
    bytes.?[1] = 0x7f;
    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    value.?.bytes = .{ 9, 8, 7 };
    value.?.flag = true;
    zalloc.zfreeValue(allocator, Value, &value);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    var fresh: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &fresh);
    try std.testing.expectEqual(@as([3]u8, .{ 0, 0, 0 }), fresh.?.bytes);
    try std.testing.expectEqual(false, fresh.?.flag);
}
