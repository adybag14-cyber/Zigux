const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "fragmented slab windows survive formatting and release order" {
    slab.kmalloc_nr_allocated = 0;

    const left = slab.kmallocBytes(9, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const right = slab.kmallocArray(2, 5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0 }, left);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }, right);

    const left_written = vsprintf.scnprintf(left[2..8], "{s}", .{"kernel"});
    try std.testing.expectEqual(@as(usize, 5), left_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 'k', 'e', 'r', 'n', 'e', 0, 0 }, left);

    const right_error = str_error_r.strErrorR(13, right[1..7]);
    try std.testing.expectEqualStrings("Permi", right_error);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 'P', 'e', 'r', 'm', 'i', 0, 0, 0, 0 }, right);

    slab.kfree(right);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(left);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "fragmented caller buffers keep fallback and padded views bounded" {
    var backing = [_]u8{
        0xa1, 0xa1, 0xa1, 0xa1,
        0xa1, 0xa1, 0xa1, 0xa1,
        0xa1, 0xa1, 0xa1, 0xa1,
        0xa1, 0xa1,
    };

    const fallback = str_error_r.strErrorR(7777, backing[3..10]);
    try std.testing.expectEqualStrings("INTERN", fallback);
    try std.testing.expectEqual(@as(u8, 0xa1), backing[2]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqual(@as(u8, 0xa1), backing[10]);

    const padded = vsprintf.scnprintfPad(backing[5..13], 6, "{s}", .{"io"});
    try std.testing.expectEqual(@as(usize, 6), padded);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xa1, 0xa1, 0xa1, 'I', 'N', 'i', 'o', ' ', ' ', ' ', ' ', 0, 0xa1, 0xa1 },
        &backing,
    );

    const direct = vsprintf.vscnprintf(backing[1..5], "{s}", .{"abcd"});
    try std.testing.expectEqual(@as(usize, 3), direct);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xa1, 'a', 'b', 'c', 0, 'i', 'o', ' ', ' ', ' ', ' ', 0, 0xa1, 0xa1 },
        &backing,
    );
}

test "zalloc owners reacquire zeroed storage after formatted handoff" {
    const allocator = std.testing.allocator;

    var scratch: ?[]u8 = try zalloc.zallocBytes(allocator, 12);
    defer zalloc.zfreeBytes(allocator, &scratch);

    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }, scratch.?);
    const written = vsprintf.scnprintf(scratch.?[4..10], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 5), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 'z', 'i', 'g', 'u', 'x', 0, 0, 0 }, scratch.?);

    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
    scratch = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0 }, scratch.?);

    const Record = struct {
        id: u32,
        ready: bool,
        tag: u8,
    };
    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    try std.testing.expectEqual(@as(u32, 0), record.?.id);
    try std.testing.expectEqual(false, record.?.ready);
    try std.testing.expectEqual(@as(u8, 0), record.?.tag);
    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);
}
