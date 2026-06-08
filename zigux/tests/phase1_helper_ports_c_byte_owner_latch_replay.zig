const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectPaddedReturn(written: usize, logical_size: usize) !void {
    try std.testing.expect(written == logical_size or written + 1 == logical_size);
}

test "byte owner latch carries formatted slab windows through zalloc storage" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocArray(2, 18, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    var release_slab = true;
    defer if (release_slab) slab.kfree(slab_bytes);

    try std.testing.expectEqual(@as(usize, 36), slab_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(slab_bytes, 0x5a);
    const err_window = slab_bytes[3..24];
    const rendered = str_error_r.strErrorR(22, err_window);
    try std.testing.expectEqualStrings("Invalid argument", rendered);
    try std.testing.expectEqual(@as(u8, 0x5a), slab_bytes[2]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[3 + rendered.len]);
    try std.testing.expectEqual(@as(u8, 0x5a), slab_bytes[24]);

    var record_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &record_owner);
    for (record_owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const record_written = vsprintf.scnprintf(record_owner.?, "err={s};len={d}", .{ rendered, rendered.len });
    try std.testing.expectEqual(@as(usize, 27), record_written);
    try std.testing.expectEqualStrings("err=Invalid argument;len=16", record_owner.?[0..record_written]);
    try std.testing.expectEqual(@as(u8, 0), record_owner.?[record_written]);

    const pad_window = slab_bytes[25..32];
    const pad_written = vsprintf.scnprintfPad(pad_window, 5, "{s}", .{"ok"});
    try expectPaddedReturn(pad_written, 5);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', ' ', ' ', ' ', 0 }, slab_bytes[25..31]);
    try std.testing.expectEqual(@as(u8, 0x5a), slab_bytes[32]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &record_owner);
    try std.testing.expect(record_owner == null);
    zalloc.zfreeBytes(allocator, &record_owner);
    try std.testing.expect(record_owner == null);

    slab.kfree(slab_bytes);
    release_slab = false;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
