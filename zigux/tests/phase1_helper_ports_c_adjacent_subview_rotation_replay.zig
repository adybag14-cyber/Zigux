const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab adjacent subviews rotate format and strerror windows" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocArray(3, 12, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    errdefer slab.kfree(bytes);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 36), bytes.len);

    const left = bytes[0..12];
    const middle = bytes[12..24];
    const right = bytes[24..36];

    @memset(left, 0x11);
    @memset(middle, 0x22);
    @memset(right, 0x33);

    const left_written = vsprintf.scnprintf(left[2..10], "slab:{d}", .{7});
    try std.testing.expectEqual(@as(usize, 6), left_written);
    try std.testing.expectEqualStrings("slab:7", left[2 .. 2 + left_written]);
    try std.testing.expectEqual(@as(u8, 0), left[2 + left_written]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x11, 0x11 }, left[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x11, 0x11 }, left[10..12]);

    const middle_rendered = str_error_r.strErrorR(12, middle[1..9]);
    try std.testing.expectEqualStrings("Cannot ", middle_rendered);
    try std.testing.expectEqual(@as(u8, 0), middle[8]);
    try std.testing.expectEqual(@as(u8, 0x22), middle[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x22, 0x22, 0x22 }, middle[9..12]);

    const right_written = vsprintf.scnprintfPad(right[3..11], 7, "{s}", .{"io"});
    try std.testing.expectEqual(@as(usize, 6), right_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'o', ' ', ' ', ' ', ' ', ' ', 0 }, right[3..11]);
    try std.testing.expectEqual(@as(u8, 0x33), right[2]);
    try std.testing.expectEqual(@as(u8, 0x33), right[11]);

    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "zalloc scratch can be freed after bounded formatter fallback reuse" {
    const allocator = std.testing.allocator;

    var scratch: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &scratch);

    try std.testing.expect(scratch != null);
    for (scratch.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const first = scratch.?[0..8];
    const second = scratch.?[8..16];
    const third = scratch.?[16..24];

    @memset(first, 0xa1);
    @memset(second, 0xb2);
    @memset(third, 0xc3);

    const first_written = vsprintf.scnprintf(first[1..7], "z{d}", .{42});
    try std.testing.expectEqual(@as(usize, 3), first_written);
    try std.testing.expectEqualStrings("z42", first[1 .. 1 + first_written]);
    try std.testing.expectEqual(@as(u8, 0), first[1 + first_written]);
    try std.testing.expectEqual(@as(u8, 0xa1), first[0]);
    try std.testing.expectEqual(@as(u8, 0xa1), first[7]);

    const fallback = str_error_r.strErrorR(4096, second[2..8]);
    try std.testing.expectEqualStrings("INTER", fallback);
    try std.testing.expectEqual(@as(u8, 0), second[7]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xb2, 0xb2 }, second[0..2]);

    const third_written = vsprintf.vscnprintf(third[0..5], "{s}", .{"tail-room"});
    try std.testing.expectEqual(@as(usize, 4), third_written);
    try std.testing.expectEqualStrings("tail", third[0..third_written]);
    try std.testing.expectEqual(@as(u8, 0), third[third_written]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xc3, 0xc3, 0xc3 }, third[5..8]);

    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
}
