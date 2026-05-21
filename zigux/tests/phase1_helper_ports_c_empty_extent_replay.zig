const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports c replay keeps empty slab arrays balanced" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocArray(0, 32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "phase1 helper ports c replay keeps empty strerror views contained" {
    var storage = [_]u8{0xaa} ** 10;
    const rendered = str_error_r.strErrorR(22, storage[4..4]);

    try std.testing.expectEqual(@as(usize, 0), rendered.len);
    try std.testing.expectEqual(@as(u8, 0xaa), storage[3]);
    try std.testing.expectEqual(@as(u8, 0xaa), storage[4]);
    try std.testing.expectEqual(@as(u8, 0xaa), storage[5]);
}

test "phase1 helper ports c replay resets zero logical size formatter views before reuse" {
    var storage = [_]u8{0xaa} ** 8;

    const zero_written = vsprintf.scnprintfPad(storage[2..7], 0, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), zero_written);
    try std.testing.expectEqual(@as(u8, 0xaa), storage[1]);
    try std.testing.expectEqual(@as(u8, 0), storage[2]);
    try std.testing.expectEqual(@as(u8, 0xaa), storage[3]);
    try std.testing.expectEqual(@as(u8, 0xaa), storage[7]);

    const reused_written = vsprintf.scnprintfPad(storage[2..7], 4, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 3), reused_written);
    try std.testing.expectEqualSlices(u8, "ok  ", storage[2..6]);
    try std.testing.expectEqual(@as(u8, 0), storage[6]);
}

test "phase1 helper ports c replay zeroes empty byte slices and nested optional values" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);

    const Nested = struct {
        count: u16,
        enabled: bool,
        maybe_label: ?[]const u8,
    };

    var value: ?*Nested = try zalloc.zallocValue(allocator, Nested);
    defer zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);
    try std.testing.expect(value.?.maybe_label == null);
}
