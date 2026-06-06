const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "zalloc ring feeds slab formatted slices and fallback error windows" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var ring_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &ring_owner);
    const ring = ring_owner.?;
    for (ring) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const slab_words = slab.kmallocArray(3, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_words);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_words) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const ring_padded = vsprintf.scnprintfPad(ring[4..14], 8, "slot-{d}", .{7});
    try std.testing.expect(ring_padded == 7 or ring_padded == 8);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, ring[0..4]);
    try std.testing.expectEqualSlices(u8, "slot-7  ", ring[4..12]);
    try std.testing.expectEqual(@as(u8, 0), ring[12]);
    try std.testing.expectEqual(@as(u8, 0), ring[13]);

    const fallback = str_error_r.strErrorR(77, ring[14..24]);
    try std.testing.expectEqualStrings("INTERNAL ", fallback);
    try std.testing.expectEqual(@as(u8, 0), ring[23]);
    for (ring[24..32]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const slab_written = vsprintf.vscnprintf(slab_words[8..16], "{s}:{d}", .{ fallback[0..3], ring_padded });
    try std.testing.expectEqual(@as(usize, 5), slab_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0, 0, 0 }, slab_words[0..8]);
    try std.testing.expectEqualStrings("INT:", slab_words[8..12]);
    try std.testing.expect(slab_words[12] == '7' or slab_words[12] == '8');
    try std.testing.expectEqual(@as(u8, 0), slab_words[13]);
    try std.testing.expectEqual(@as(u8, 0), slab_words[14]);
    try std.testing.expectEqual(@as(u8, 0), slab_words[15]);

    zalloc.zfreeBytes(allocator, &ring_owner);
    zalloc.zfreeBytes(allocator, &ring_owner);
    try std.testing.expect(ring_owner == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "slab array slices record zalloc value lengths across known errors" {
    const allocator = std.testing.allocator;
    const Record = struct {
        known_len: usize,
        padded_len: usize,
        direct_len: usize,
        saw_zeroed_owner: bool,
    };

    slab.kmalloc_nr_allocated = 0;

    var record_owner: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record_owner);
    try std.testing.expect(record_owner.?.saw_zeroed_owner == false);
    try std.testing.expectEqual(@as(usize, 0), record_owner.?.known_len);

    const slab_bytes = slab.kmallocArray(4, 10, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const known = str_error_r.strErrorR(12, slab_bytes[1..24]);
    record_owner.?.known_len = known.len;
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[23]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[0]);

    const padded_len = vsprintf.scnprintfPad(slab_bytes[24..34], 7, "e{d}", .{record_owner.?.known_len});
    record_owner.?.padded_len = padded_len;
    try std.testing.expect(padded_len == 6 or padded_len == 7);
    try std.testing.expectEqualSlices(u8, "e22    ", slab_bytes[24..31]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[31]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[32]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[33]);

    var direct_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 9);
    defer zalloc.zfreeBytes(allocator, &direct_owner);
    const direct = direct_owner.?;
    record_owner.?.saw_zeroed_owner = true;
    record_owner.?.direct_len = vsprintf.scnprintf(direct, "{s}-{d}", .{ "ok", padded_len });
    try std.testing.expectEqual(@as(usize, 4), record_owner.?.direct_len);
    try std.testing.expectEqualStrings("ok-", direct[0..3]);
    try std.testing.expect(direct[3] == '6' or direct[3] == '7');
    try std.testing.expectEqual(@as(u8, 0), direct[4]);
    for (direct[5..]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(record_owner.?.saw_zeroed_owner);
    try std.testing.expectEqual(@as(usize, 22), record_owner.?.known_len);
    try std.testing.expect(record_owner.?.padded_len == 6 or record_owner.?.padded_len == 7);
    try std.testing.expectEqual(@as(usize, 4), record_owner.?.direct_len);
}
