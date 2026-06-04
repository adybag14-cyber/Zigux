const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab overflow failure preserves zalloc value owner reset" {
    const allocator = std.testing.allocator;
    const Record = struct {
        len: usize,
        err: i32,
        ready: bool,
        bytes: [12]u8,
    };

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record != null);
    try std.testing.expectEqual(@as(usize, 0), record.?.len);
    try std.testing.expectEqual(@as(i32, 0), record.?.err);
    try std.testing.expectEqual(false, record.?.ready);
    try std.testing.expectEqualSlices(u8, &([_]u8{0} ** 12), record.?.bytes[0..]);

    const payload = slab.kmallocArray(3, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(payload);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    const written = vsprintf.scnprintf(payload[1..9], "E{d}", .{22});
    try std.testing.expectEqual(@as(usize, 3), written);
    try std.testing.expectEqual(@as(u8, 0), payload[0]);
    try std.testing.expectEqualSlices(u8, "E22", payload[1..4]);
    try std.testing.expectEqual(@as(u8, 0), payload[4]);
    try std.testing.expectEqual(@as(u8, 0), payload[9]);

    @memcpy(record.?.bytes[0..payload.len], payload);
    record.?.len = written;
    record.?.err = 22;
    record.?.ready = true;
    try std.testing.expectEqualSlices(u8, payload, record.?.bytes[0..payload.len]);

    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);
    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "empty format and strerror windows preserve sentinels" {
    var backing = [_]u8{
        0xa1, 0xa2, 0xa3, 0xa4,
        0xa5, 0xa6, 0xa7, 0xa8,
        0xa9, 0xaa, 0xab, 0xac,
    };

    const empty_written = vsprintf.scnprintf(backing[3..3], "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqual(@as(u8, 0xa3), backing[2]);
    try std.testing.expectEqual(@as(u8, 0xa4), backing[3]);

    const padded_written = vsprintf.scnprintfPad(backing[4..10], 5, "{s}", .{"io"});
    try std.testing.expect(padded_written >= 4);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'o', ' ', ' ', ' ', 0 }, backing[4..10]);
    try std.testing.expectEqual(@as(u8, 0xa4), backing[3]);
    try std.testing.expectEqual(@as(u8, 0xab), backing[10]);

    var err_backing: [14]u8 = @splat(0xdd);
    const empty = str_error_r.strErrorR(13, err_backing[2..2]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, 0xdd), err_backing[1]);
    try std.testing.expectEqual(@as(u8, 0xdd), err_backing[2]);

    const truncated = str_error_r.strErrorR(4096, err_backing[3..10]);
    try std.testing.expectEqualStrings("INTERN", truncated);
    try std.testing.expectEqual(@as(u8, 0), err_backing[9]);
    try std.testing.expectEqual(@as(u8, 0xdd), err_backing[2]);
    try std.testing.expectEqual(@as(u8, 0xdd), err_backing[10]);
}

test "zalloc byte owner receives formatted slab copy and frees idempotently" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    const slab_bytes = slab.kmallocArray(4, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, slab_bytes.len);
    defer zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner != null);
    for (owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const first = vsprintf.vscnprintf(slab_bytes[0..6], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 5), first);
    const second = str_error_r.strErrorR(2, slab_bytes[6..12]);
    try std.testing.expectEqualStrings("No su", second);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[11]);

    @memcpy(owner.?, slab_bytes);
    try std.testing.expectEqualSlices(u8, slab_bytes, owner.?);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
