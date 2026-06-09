const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const ShadowSummary = struct {
    errnum: i32,
    known_len: usize,
    fallback_len: usize,
    formatted_len: usize,
    slab_allocations: isize,
};

test "shadow ring carries slab strerror and zalloc formatting ownership" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const ring = slab.kmallocArray(3, 16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 48), ring.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memset(ring, 0xcc);

    const known = str_error_r.strErrorR(22, ring[2..19]);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0xcc), ring[1]);
    try std.testing.expectEqual(@as(u8, 0), ring[18]);
    try std.testing.expectEqual(@as(u8, 0xcc), ring[19]);

    const fallback = str_error_r.strErrorR(31337, ring[20..48]);
    try std.testing.expectEqual(@as(usize, 27), fallback.len);
    try std.testing.expect(std.mem.startsWith(u8, fallback, "INTERNAL ERROR: strerror_r"));
    try std.testing.expectEqual(@as(u8, 0), ring[47]);

    var formatted_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &formatted_owner);
    for (formatted_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const formatted_len = vsprintf.scnprintf(
        formatted_owner.?,
        "known={s};fallback={d}",
        .{ known, fallback.len },
    );
    try std.testing.expectEqual(@as(usize, 34), formatted_len);
    try std.testing.expectEqualStrings("known=Invalid argument;fallback=27", formatted_owner.?[0..formatted_len]);
    try std.testing.expectEqual(@as(u8, 0), formatted_owner.?[formatted_len]);

    var summary_owner: ?*ShadowSummary = try zalloc.zallocValue(allocator, ShadowSummary);
    defer zalloc.zfreeValue(allocator, ShadowSummary, &summary_owner);
    try std.testing.expectEqual(@as(i32, 0), summary_owner.?.errnum);
    try std.testing.expectEqual(@as(usize, 0), summary_owner.?.known_len);

    summary_owner.?.* = .{
        .errnum = 31337,
        .known_len = known.len,
        .fallback_len = fallback.len,
        .formatted_len = formatted_len,
        .slab_allocations = slab.kmalloc_nr_allocated,
    };
    try std.testing.expectEqual(@as(i32, 31337), summary_owner.?.errnum);
    try std.testing.expectEqual(@as(usize, 16), summary_owner.?.known_len);
    try std.testing.expectEqual(@as(usize, 27), summary_owner.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 34), summary_owner.?.formatted_len);
    try std.testing.expectEqual(@as(isize, 1), summary_owner.?.slab_allocations);

    zalloc.zfreeValue(allocator, ShadowSummary, &summary_owner);
    try std.testing.expect(summary_owner == null);
    zalloc.zfreeBytes(allocator, &formatted_owner);
    try std.testing.expect(formatted_owner == null);

    slab.kfree(ring);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "shadow ring preserves failed allocations and padded handoff sentinels" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_window = slab.kmallocBytes(12, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(slab_window, 0xaa);

    try std.testing.expect(slab.kmallocBytes(16, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var empty_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(empty_owner != null);
    try std.testing.expectEqual(@as(usize, 0), empty_owner.?.len);
    zalloc.zfreeBytes(allocator, &empty_owner);
    try std.testing.expect(empty_owner == null);
    zalloc.zfreeBytes(allocator, &empty_owner);
    try std.testing.expect(empty_owner == null);

    var pad_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 10);
    defer zalloc.zfreeBytes(allocator, &pad_owner);
    const pad_written = vsprintf.scnprintfPad(pad_owner.?, 7, "id={d}", .{5});
    try std.testing.expect(pad_written == 7 or pad_written == 6);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'd', '=', '5', ' ', ' ', ' ', 0 }, pad_owner.?[0..8]);
    try std.testing.expectEqual(@as(u8, 0), pad_owner.?[8]);
    try std.testing.expectEqual(@as(u8, 0), pad_owner.?[9]);

    const status_len = vsprintf.vscnprintf(slab_window[1..11], "pad={d}", .{pad_written});
    try std.testing.expectEqual(@as(usize, 5), status_len);
    try std.testing.expect(std.mem.eql(u8, slab_window[1..5], "pad="));
    try std.testing.expect(slab_window[5] == '6' or slab_window[5] == '7');
    try std.testing.expectEqual(@as(u8, 0), slab_window[6]);
    try std.testing.expectEqual(@as(u8, 0xaa), slab_window[0]);
    try std.testing.expectEqual(@as(u8, 0xaa), slab_window[7]);

    zalloc.zfreeBytes(allocator, &pad_owner);
    try std.testing.expect(pad_owner == null);

    slab.kfree(slab_window);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
