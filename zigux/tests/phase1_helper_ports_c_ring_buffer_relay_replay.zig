const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab ring windows relay strerror output into zalloc summaries" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(24, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var ring_owner: ?[]u8 = slab.kcallocBytes(3, 40, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer if (ring_owner) |bytes| slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (ring_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    for (summary_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const ring = ring_owner.?;
    const first_slot = ring[0..40];
    const second_slot = ring[40..80];
    const third_slot = ring[80..120];

    const known = str_error_r.strErrorR(2, first_slot[1..32]);
    try std.testing.expectEqualStrings("No such file or directory", known);
    try std.testing.expectEqual(@as(u8, 0), first_slot[0]);
    try std.testing.expectEqual(@as(u8, 0), first_slot[known.len + 1]);

    const fallback = str_error_r.strErrorR(8008, second_slot[2..34]);
    try std.testing.expectEqual(@as(usize, 31), fallback.len);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(8008", fallback);
    try std.testing.expectEqual(@as(u8, 0), second_slot[0]);
    try std.testing.expectEqual(@as(u8, 0), second_slot[1]);
    try std.testing.expectEqual(@as(u8, 0), second_slot[33]);

    const exact = str_error_r.strErrorR(22, third_slot[4..21]);
    try std.testing.expectEqualStrings("Invalid argument", exact);
    try std.testing.expectEqual(@as(u8, 0), third_slot[3]);
    try std.testing.expectEqual(@as(u8, 0), third_slot[20]);

    const summary = summary_owner.?;
    const direct_written = vsprintf.scnprintf(summary[0..24], "r0:{d}:{s}", .{ known.len, known[0..2] });
    try std.testing.expectEqual(@as(usize, 8), direct_written);
    try std.testing.expectEqualStrings("r0:25:No", summary[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), summary[direct_written]);

    const padded_written = vsprintf.scnprintfPad(summary[24..48], 17, "e{d}:{d}", .{ 8008, fallback.len });
    try std.testing.expectEqual(@as(usize, 17), padded_written);
    try std.testing.expectEqualStrings("e8008:31         ", summary[24 .. 24 + padded_written]);
    try std.testing.expectEqual(@as(u8, 0), summary[24 + padded_written]);

    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);

    slab.kfree(ring_owner);
    ring_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "relay owners can be released and reacquired as zeroed records" {
    const allocator = std.testing.allocator;
    const Record = struct {
        len: usize,
        err: i32,
        copied: [12]u8,
    };

    slab.kmalloc_nr_allocated = 0;

    var scratch_owner: ?[]u8 = slab.kzallocBytes(64, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer if (scratch_owner) |bytes| slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const scratch = scratch_owner.?;
    const rendered = str_error_r.strErrorR(12, scratch[7..31]);
    try std.testing.expectEqualStrings("Cannot allocate memory", rendered);
    try std.testing.expectEqual(@as(u8, 0), scratch[6]);
    try std.testing.expectEqual(@as(u8, 0), scratch[7 + rendered.len]);

    var relay_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &relay_owner);

    const relay = relay_owner.?;
    const relay_written = vsprintf.scnprintf(relay[3..20], "m:{s}:{d}", .{ rendered[0..6], rendered.len });
    try std.testing.expectEqual(@as(usize, 11), relay_written);
    try std.testing.expectEqualStrings("m:Cannot:22", relay[3 .. 3 + relay_written]);
    try std.testing.expectEqual(@as(u8, 0), relay[3 + relay_written]);

    var record_owner: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record_owner);
    try std.testing.expectEqual(@as(usize, 0), record_owner.?.len);
    try std.testing.expectEqual(@as(i32, 0), record_owner.?.err);
    for (record_owner.?.copied) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    record_owner.?.len = relay_written;
    record_owner.?.err = 12;
    @memcpy(record_owner.?.copied[0..relay_written], relay[3 .. 3 + relay_written]);
    try std.testing.expectEqualStrings("m:Cannot:22", record_owner.?.copied[0..relay_written]);

    zalloc.zfreeBytes(allocator, &relay_owner);
    try std.testing.expect(relay_owner == null);

    relay_owner = try zalloc.zallocBytes(allocator, 8);
    for (relay_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    zalloc.zfreeValue(allocator, Record, &record_owner);
    try std.testing.expect(record_owner == null);

    slab.kfree(scratch_owner);
    scratch_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
