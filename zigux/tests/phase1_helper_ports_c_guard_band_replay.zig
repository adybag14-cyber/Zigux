const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab reuses dirty and zero-width allocations without counter drift" {
    slab.kmalloc_nr_allocated = 0;

    const dirty = slab.kmallocArray(3, 0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), dirty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const bytes = slab.kmallocBytes(3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(bytes, 0x5a);
    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, zeroed);

    slab.kfree(dirty);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps exact-fit and single-byte guard bands fenced" {
    var exact = [_]u8{ '.', '.', '.', '.', '.', '.', '.', '.', '.', '.' };
    const known = str_error_r.strErrorR(0, exact[1..9]);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ '.', 'S', 'u', 'c', 'c', 'e', 's', 's', 0, '.' },
        &exact,
    );

    var tiny = [_]u8{ '#', '#', '#', '#' };
    const fallback = str_error_r.strErrorR(4096, tiny[1..3]);
    try std.testing.expectEqualStrings("I", fallback);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', 'I', 0, '#' }, &tiny);
}

test "vsprintf keeps guard-band interior views isolated across padded and exact writes" {
    var backing = [_]u8{ '?', '?', '?', '?', '?', '?', '?', '?', '?', '?' };
    const padded = backing[2..7];

    const padded_written = vsprintf.scnprintfPad(padded, 4, "{s}", .{"x"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ '?', '?', 'x', ' ', ' ', ' ', 0, '?', '?', '?' },
        &backing,
    );

    const exact = backing[4..8];
    const exact_written = vsprintf.vscnprintf(exact, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 2), exact_written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ '?', '?', 'x', ' ', 'a', 'b', 0, '?', '?', '?' },
        &backing,
    );
}

test "zalloc resets byte and value owners for guarded reentry" {
    const allocator = std.testing.allocator;
    const Guarded = extern struct {
        count: u16,
        flag: bool,
        ptr: ?*u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, bytes.?);
    bytes.?[0] = 0x44;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, bytes.?);

    var guarded: ?*Guarded = try zalloc.zallocValue(allocator, Guarded);
    try std.testing.expectEqual(@as(u16, 0), guarded.?.count);
    try std.testing.expectEqual(false, guarded.?.flag);
    try std.testing.expect(guarded.?.ptr == null);
    guarded.?.count = 9;
    guarded.?.flag = true;
    zalloc.zfreeValue(allocator, Guarded, &guarded);
    try std.testing.expect(guarded == null);

    guarded = try zalloc.zallocValue(allocator, Guarded);
    defer zalloc.zfreeValue(allocator, Guarded, &guarded);
    try std.testing.expectEqual(@as(u16, 0), guarded.?.count);
    try std.testing.expectEqual(false, guarded.?.flag);
    try std.testing.expect(guarded.?.ptr == null);
}
