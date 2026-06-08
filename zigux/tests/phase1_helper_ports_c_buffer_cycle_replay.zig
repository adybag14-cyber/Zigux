const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "buffer cycle replays slab windows through strerror and vsprintf" {
    slab.kmalloc_nr_allocated = 0;

    const backing = slab.kmallocBytes(48, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(backing);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (backing) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const known_window = backing[3..24];
    const known = str_error_r.strErrorR(22, known_window);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0), backing[19]);
    try std.testing.expectEqual(@as(u8, 0), backing[20]);
    try std.testing.expectEqual(@as(u8, 0), backing[21]);

    const summary_window = backing[24..40];
    const summary_written = vsprintf.scnprintf(summary_window, "err:{s}:{d}", .{ known, known.len });
    try std.testing.expectEqual(@as(usize, 15), summary_written);
    try std.testing.expectEqualStrings("err:Invalid arg", summary_window[0..summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary_window[summary_written]);

    const pad_window = backing[8..18];
    _ = vsprintf.scnprintfPad(pad_window, 8, "{s}", .{"io"});
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'o', ' ', ' ', ' ', ' ', ' ', ' ', 0, 'n' }, pad_window);

    try std.testing.expect(slab.slabIsAvailable());
    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc owners can carry formatted fallback summaries and reset cleanly" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 64);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const fallback = str_error_r.strErrorR(4096, bytes.?[4..52]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 48)=22", fallback);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[51]);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[52]);

    const rendered = vsprintf.vscnprintf(bytes.?[0..18], "fallback:{d}", .{fallback.len});
    try std.testing.expectEqual(@as(usize, 11), rendered);
    try std.testing.expectEqualStrings("fallback:46", bytes.?[0..rendered]);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[rendered]);

    const Owner = struct {
        len: usize,
        first: u8,
    };
    var owner: ?*Owner = try zalloc.zallocValue(allocator, Owner);
    defer zalloc.zfreeValue(allocator, Owner, &owner);
    try std.testing.expectEqual(@as(usize, 0), owner.?.len);
    try std.testing.expectEqual(@as(u8, 0), owner.?.first);

    owner.?.len = fallback.len;
    owner.?.first = bytes.?[0];
    try std.testing.expectEqual(@as(usize, 46), owner.?.len);
    try std.testing.expectEqual(@as(u8, 'f'), owner.?.first);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    zalloc.zfreeValue(allocator, Owner, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeValue(allocator, Owner, &owner);
    try std.testing.expect(owner == null);
}
