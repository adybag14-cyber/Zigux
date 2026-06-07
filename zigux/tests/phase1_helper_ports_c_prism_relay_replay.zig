const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const testing = std.testing;

test "prism relay preserves slab windows through strerror and vsprintf" {
    slab.kmalloc_nr_allocated = 0;

    const backing = slab.kmallocArray(1, 112, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(backing);
    try testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (backing) |byte| {
        try testing.expectEqual(@as(u8, 0), byte);
    }

    const known_window = backing[4..31];
    const known = str_error_r.strErrorR(12, known_window);
    try testing.expectEqualStrings("Cannot allocate memory", known);
    try testing.expectEqual(@as(u8, 0), backing[4 + known.len]);
    try testing.expectEqual(@as(u8, 0), backing[3]);
    try testing.expectEqual(@as(u8, 0), backing[31]);

    const fallback_window = backing[40..93];
    const fallback = str_error_r.strErrorR(7777, fallback_window);
    try testing.expectEqualStrings("INTERNAL ERROR: strerror_r(7777, [buf], 53)=22", fallback);
    try testing.expectEqual(@as(u8, 0), backing[40 + fallback.len]);
    try testing.expectEqual(@as(u8, 0), backing[39]);
    try testing.expectEqual(@as(u8, 0), backing[93]);

    var relay: [64]u8 = @splat(0xaa);
    const written = vsprintf.scnprintf(&relay, "known={d} fallback={d}", .{ known.len, fallback.len });
    try testing.expectEqual(@as(usize, 20), written);
    try testing.expectEqualStrings("known=22 fallback=46", relay[0..written]);
    try testing.expectEqual(@as(u8, 0), relay[written]);
    try testing.expectEqual(@as(u8, 0xaa), relay[written + 1]);

    var padded: [24]u8 = @splat(0xbb);
    const padded_written = vsprintf.scnprintfPad(padded[3..20], 14, "prism:{d}", .{slab.kmalloc_nr_allocated});
    try testing.expect(padded_written == 13 or padded_written == 14);
    try testing.expectEqualSlices(u8, &[_]u8{ 0xbb, 0xbb, 0xbb }, padded[0..3]);
    try testing.expectEqualStrings("prism:1       ", padded[3..17]);
    try testing.expectEqual(@as(u8, 0), padded[17]);
    try testing.expectEqual(@as(u8, 0xbb), padded[20]);
}

test "prism relay resets zalloc owners and preserves slab accounting on failed requests" {
    const allocator = testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try testing.expectEqual(@as(u8, 0), byte);
    }

    const permission = str_error_r.strErrorR(13, bytes.?[2..22]);
    try testing.expectEqualStrings("Permission denied", permission);
    try testing.expectEqual(@as(u8, 0), bytes.?[2 + permission.len]);
    try testing.expectEqual(@as(u8, 0), bytes.?[1]);

    const formatted = vsprintf.vscnprintf(bytes.?[0..18], "relay:{s}:{d}", .{ permission[0..4], permission.len });
    try testing.expectEqual(@as(usize, 13), formatted);
    try testing.expectEqualStrings("relay:Perm:17", bytes.?[0..formatted]);
    try testing.expectEqual(@as(u8, 0), bytes.?[formatted]);

    zalloc.zfreeBytes(allocator, &bytes);
    try testing.expect(bytes == null);

    var reacquired: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &reacquired);
    try testing.expect(reacquired != null);
    try testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0 }, reacquired.?);

    const before_failed = slab.kmalloc_nr_allocated;
    try testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL | slab.__GFP_ZERO) == null);
    try testing.expect(slab.kmallocBytes(16, 0) == null);
    try testing.expectEqual(before_failed, slab.kmalloc_nr_allocated);

    const Record = struct {
        len: usize,
        ok: bool,
        tag: [4]u8,
    };

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try testing.expect(record != null);
    try testing.expectEqual(@as(usize, 0), record.?.len);
    try testing.expectEqual(false, record.?.ok);
    try testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &record.?.tag);

    record.?.len = formatted;
    record.?.ok = true;
    record.?.tag = "prsm".*;
    try testing.expectEqual(@as(usize, 13), record.?.len);
    try testing.expect(record.?.ok);
    try testing.expectEqualSlices(u8, "prsm", &record.?.tag);

    zalloc.zfreeValue(allocator, Record, &record);
    try testing.expect(record == null);
}
