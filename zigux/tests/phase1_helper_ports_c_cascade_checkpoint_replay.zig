const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const Checkpoint = struct {
    code: i32,
    used: usize,
    padded: usize,
    fallback_len: usize,
};

test "cascade checkpoint preserves owners and caller windows" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slab_backing = slab.kmallocBytes(36, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_backing);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_backing) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const error_window = slab_backing[3..28];
    const known = str_error_r.strErrorR(12, error_window);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqual(@as(u8, 0), slab_backing[3 + known.len]);
    try std.testing.expectEqual(@as(u8, 0), slab_backing[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_backing[28]);

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    for (summary_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const written = vsprintf.scnprintf(summary_owner.?, "C:{d}:{s}", .{ @as(u32, 7), known });
    try std.testing.expectEqual(@as(usize, 17), written);
    try std.testing.expectEqualStrings("C:7:Cannot alloca", summary_owner.?[0..written]);
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[written]);

    var checkpoint: ?*Checkpoint = try zalloc.zallocValue(allocator, Checkpoint);
    defer zalloc.zfreeValue(allocator, Checkpoint, &checkpoint);
    try std.testing.expectEqual(@as(i32, 0), checkpoint.?.code);
    try std.testing.expectEqual(@as(usize, 0), checkpoint.?.used);
    checkpoint.?.code = 12;
    checkpoint.?.used = written;

    var padded = [_]u8{0xa5} ** 16;
    const padded_written = vsprintf.scnprintfPad(padded[2..13], 9, "S:{d}", .{checkpoint.?.code});
    try std.testing.expectEqual(@as(usize, 9), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa5, 0xa5 }, padded[0..2]);
    try std.testing.expectEqualStrings("S:12     ", padded[2..11]);
    try std.testing.expectEqual(@as(u8, 0), padded[11]);
    try std.testing.expectEqual(@as(u8, 0xa5), padded[13]);
    checkpoint.?.padded = padded_written;

    const fail_before = slab.kmalloc_nr_allocated;
    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(fail_before, slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);
    zalloc.zfreeValue(allocator, Checkpoint, &checkpoint);
    try std.testing.expect(checkpoint == null);
}

test "cascade fallback rewrites through zalloc and slab reclaim accounting" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var records_owner: ?[]u8 = slab.kmallocArray(3, 10, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(records_owner);
    const records = records_owner.?;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (records) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var caller = [_]u8{0xcc} ** 44;
    const fallback = str_error_r.strErrorR(9002, caller[4..39]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(9002,", fallback[0..32]);
    try std.testing.expectEqual(@as(u8, 0xcc), caller[3]);
    try std.testing.expectEqual(@as(u8, 0), caller[4 + fallback.len]);
    try std.testing.expectEqual(@as(u8, 0xcc), caller[39]);

    var relay: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &relay);
    const relay_written = vsprintf.scnprintf(relay.?, "F:{d}:{d}", .{ fallback.len, slab.kmalloc_nr_allocated });
    try std.testing.expectEqual(@as(usize, 6), relay_written);
    try std.testing.expectEqualStrings("F:34:1", relay.?[0..relay_written]);
    try std.testing.expectEqual(@as(u8, 0), relay.?[relay_written]);

    @memcpy(records[0..relay_written], relay.?[0..relay_written]);
    try std.testing.expectEqualStrings("F:34:1", records[0..relay_written]);

    var short = [_]u8{0xdd} ** 6;
    const short_written = vsprintf.vscnprintf(&short, "{s}", .{fallback});
    try std.testing.expectEqual(@as(usize, 5), short_written);
    try std.testing.expectEqualStrings("INTER", short[0..short_written]);
    try std.testing.expectEqual(@as(u8, 0), short[short_written]);

    zalloc.zfreeBytes(allocator, &relay);
    try std.testing.expect(relay == null);
    const before_free = slab.kmalloc_nr_allocated;
    slab.kfree(records);
    records_owner = null;
    try std.testing.expectEqual(before_free - 1, slab.kmalloc_nr_allocated);
}
