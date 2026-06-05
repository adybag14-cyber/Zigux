const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectPadCount(actual: usize, current: usize) !void {
    try std.testing.expect(actual == current or actual == current -| 1);
}

test "slab caller window rotates through format and strerror while stale tails stay bounded" {
    slab.kmalloc_nr_allocated = 0;

    const slab_owner = slab.kmallocArray(3, 12, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 36), slab_owner.len);

    const err_window = slab_owner[4..22];
    const rendered_error = str_error_r.strErrorR(13, err_window);
    try std.testing.expectEqualStrings("Permission denied", rendered_error);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[3]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[21]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[22]);

    const short_window = slab_owner[4..12];
    const formatted = vsprintf.scnprintf(short_window, "slot:{d}", .{3});
    try std.testing.expectEqual(@as(usize, 6), formatted);
    try std.testing.expectEqualStrings("slot:3", short_window[0..formatted]);
    try std.testing.expectEqual(@as(u8, 0), short_window[formatted]);
    try std.testing.expectEqual(@as(u8, 'i'), short_window[formatted + 1]);
    try std.testing.expectEqual(@as(u8, 'o'), slab_owner[12]);

    const allocator = std.testing.allocator;
    var zowner: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &zowner);
    try std.testing.expect(zowner != null);

    @memcpy(zowner.?[2..10], short_window);
    try std.testing.expectEqual(@as(u8, 0), zowner.?[0]);
    try std.testing.expectEqual(@as(u8, 0), zowner.?[1]);
    try std.testing.expectEqualStrings("slot:3", zowner.?[2..8]);
    try std.testing.expectEqual(@as(u8, 'i'), zowner.?[9]);

    const fallback = str_error_r.strErrorR(4096, zowner.?[3..21]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: s", fallback);
    try std.testing.expectEqual(@as(u8, 's'), zowner.?[2]);
    try std.testing.expectEqual(@as(u8, 0), zowner.?[20]);
    try std.testing.expectEqual(@as(u8, 0), zowner.?[21]);

    zalloc.zfreeBytes(allocator, &zowner);
    try std.testing.expect(zowner == null);
    zalloc.zfreeBytes(allocator, &zowner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc value owner records padded windows without disturbing slab accounting" {
    const allocator = std.testing.allocator;
    const Record = struct {
        code: i32,
        used: usize,
        bytes: [10]u8,
    };

    slab.kmalloc_nr_allocated = 0;
    const slab_marker = slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_marker);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expectEqual(@as(i32, 0), record.?.code);
    try std.testing.expectEqual(@as(usize, 0), record.?.used);
    try std.testing.expectEqualSlices(u8, &[_]u8{0} ** 10, &record.?.bytes);

    record.?.code = 12;
    var scratch: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    defer zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch != null);

    const window = scratch.?[2..14];
    const padded = vsprintf.scnprintfPad(window, 9, "err={d}", .{record.?.code});
    try expectPadCount(padded, 9);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, scratch.?[0..2]);
    try std.testing.expectEqualSlices(u8, "err=12   ", window[0..9]);
    try std.testing.expectEqual(@as(u8, 0), window[9]);
    try std.testing.expectEqual(@as(u8, 0), window[10]);
    try std.testing.expectEqual(@as(u8, 0), window[11]);

    record.?.used = padded;
    @memcpy(&record.?.bytes, scratch.?[2..12]);
    try std.testing.expectEqualSlices(u8, "err=12   \x00", &record.?.bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const known = str_error_r.strErrorR(record.?.code, scratch.?[0..]);
    try std.testing.expectEqualStrings("Cannot allocate", known);
    try std.testing.expectEqual(@as(u8, 0), scratch.?[15]);
    try std.testing.expectEqualSlices(u8, "err=12   \x00", &record.?.bytes);

    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
