const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab rebounds from a dirty single-byte allocation into a zeroed caller slot" {
    slab.kmalloc_nr_allocated = 0;

    const dirty = slab.kmallocBytes(1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    dirty[0] = 0xaa;
    slab.kfree(dirty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), zeroed[0]);
}

test "strErrorR preserves terminators on one-byte and two-byte caller views" {
    var tiny = [_]u8{0xaa};
    const tiny_written = str_error_r.strErrorR(0, &tiny);
    try std.testing.expectEqual(@as(usize, 0), tiny_written.len);
    try std.testing.expectEqual(@as(u8, 0), tiny[0]);

    var short = [_]u8{ 0xaa, 0xaa };
    const short_written = str_error_r.strErrorR(0, &short);
    try std.testing.expectEqualStrings("S", short_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'S', 0 }, &short);
}

test "vsprintf reuses tiny caller buffers without leaking old bytes" {
    var buffer = [_]u8{ 0xaa, 0xaa };
    const first_written = vsprintf.scnprintf(&buffer, "{s}", .{"abc"});
    try std.testing.expectEqual(@as(usize, 1), first_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 0 }, &buffer);

    buffer = [_]u8{ 0xdd, 0xdd };
    const padded_written = vsprintf.scnprintfPad(&buffer, 4, "{s}", .{"z"});
    try std.testing.expectEqual(@as(usize, 1), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 0 }, &buffer);
}

test "zalloc zeroes tiny byte and value allocations and resets optionals on free" {
    const allocator = std.testing.allocator;
    const Tiny = struct {
        flag: bool,
        byte: u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[0]);
    bytes.?[0] = 0xaa;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Tiny = try zalloc.zallocValue(allocator, Tiny);
    try std.testing.expect(value != null);
    try std.testing.expectEqual(false, value.?.flag);
    try std.testing.expectEqual(@as(u8, 0), value.?.byte);
    zalloc.zfreeValue(allocator, Tiny, &value);
    try std.testing.expect(value == null);
}
