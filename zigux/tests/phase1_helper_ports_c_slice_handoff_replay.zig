const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C hand off slab slices through formatting and strerror windows" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memset(bytes, 0xa5);
    const rendered = vsprintf.scnprintf(bytes[3..13], "slot={d}", .{7});
    try std.testing.expectEqual(@as(usize, 6), rendered);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa5, 0xa5, 0xa5 }, bytes[0..3]);
    try std.testing.expectEqualStrings("slot=7", bytes[3 .. 3 + rendered]);
    try std.testing.expectEqual(@as(u8, 0), bytes[3 + rendered]);
    try std.testing.expectEqual(@as(u8, 0xa5), bytes[13]);

    const error_text = str_error_r.strErrorR(22, bytes[8..18]);
    try std.testing.expectEqualStrings("Invalid a", error_text);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 's', 'l', 'o', 't', '=' }, bytes[3..8]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'I', 'n', 'v', 'a', 'l', 'i', 'd', ' ', 'a', 0 }, bytes[8..18]);
    try std.testing.expectEqual(@as(u8, 0xa5), bytes[18]);
}

test "phase1 helper ports C move formatted bytes into zalloc ownership and reset cleanly" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    const slab_bytes = slab.kmallocBytes(16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const written = vsprintf.scnprintf(slab_bytes, "handoff:{d}", .{42});
    try std.testing.expectEqualStrings("handoff:42", slab_bytes[0..written]);

    var owned: ?[]u8 = try zalloc.zallocBytes(allocator, written + 1);
    defer zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned != null);
    for (owned.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memcpy(owned.?[0..written], slab_bytes[0..written]);
    try std.testing.expectEqualStrings("handoff:42", owned.?[0..written]);
    try std.testing.expectEqual(@as(u8, 0), owned.?[written]);

    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);
    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "phase1 helper ports C keep fallback error lengths tied to the active zalloc view" {
    const allocator = std.testing.allocator;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 56);
    defer zalloc.zfreeBytes(allocator, &owner);

    @memset(owner.?, 0xcc);
    const window = owner.?[5..47];
    const rendered = str_error_r.strErrorR(4096, window);

    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 4", rendered);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc, 0xcc, 0xcc }, owner.?[0..5]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[46]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[47]);

    const rewritten = vsprintf.scnprintfPad(owner.?[8..20], 12, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 11), rewritten);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'o', 'k', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0 },
        owner.?[8..20],
    );
    try std.testing.expectEqual(@as(u8, 'I'), owner.?[5]);
    try std.testing.expectEqual(@as(u8, ' '), owner.?[20]);
}
