const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C keep failed slab allocations out of accounting" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(16, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const bytes = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.slabIsAvailable());
}

test "phase1 helper ports C reset zalloc owners after repeated and zero-sized frees" {
    const allocator = std.testing.allocator;
    const Owner = struct {
        count: usize,
        enabled: bool,
    };

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(empty != null);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);

    var value: ?*Owner = try zalloc.zallocValue(allocator, Owner);
    try std.testing.expectEqual(@as(usize, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);
    zalloc.zfreeValue(allocator, Owner, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Owner, &value);
    try std.testing.expect(value == null);
}

test "phase1 helper ports C share subview boundaries across strerror and vsprintf" {
    var backing = [_]u8{
        0xa1, 0xa2, 0xa3, 0xa4,
        0xa5, 0xa6, 0xa7, 0xa8,
        0xa9, 0xaa, 0xab, 0xac,
    };

    const formatted = vsprintf.scnprintf(backing[2..9], "id={d}", .{42});
    try std.testing.expectEqual(@as(usize, 5), formatted);
    try std.testing.expectEqualStrings("id=42", backing[2 .. 2 + formatted]);
    try std.testing.expectEqual(@as(u8, 0), backing[2 + formatted]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa1, 0xa2 }, backing[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xab, 0xac }, backing[9..12]);

    const rendered = str_error_r.strErrorR(13, backing[4..10]);
    try std.testing.expectEqualStrings("Permi", rendered);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa1, 0xa2, 'i', 'd' }, backing[0..4]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'P', 'e', 'r', 'm', 'i', 0 }, backing[4..10]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xab, 0xac }, backing[10..12]);
}

test "phase1 helper ports C pad formatting and strerror fallback report active windows" {
    var padded = [_]u8{ 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb };
    const padded_written = vsprintf.scnprintfPad(&padded, padded.len - 1, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 7), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', ' ', ' ', ' ', ' ', ' ', 0 }, &padded);

    var fallback: [48]u8 = @splat(0xcc);
    const fallback_window = fallback[3..45];
    const fallback_rendered = str_error_r.strErrorR(4096, fallback_window);

    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 4", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0xcc), fallback[2]);
    try std.testing.expectEqual(@as(u8, 0), fallback[44]);
    try std.testing.expectEqual(@as(u8, 0xcc), fallback[45]);
}
