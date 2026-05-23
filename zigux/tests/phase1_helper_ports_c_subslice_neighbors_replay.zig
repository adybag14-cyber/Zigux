const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps counters honest across mixed live and fail paths" {
    slab.kmalloc_nr_allocated = 0;

    const live = slab.kmallocBytes(6, slab.__GFP_DIRECT_RECLAIM | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (live) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(live);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocBytes(6, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR reuses offset caller views without touching neighbors" {
    var backing = [_]u8{0xaa} ** 24;
    const view = backing[3..21];

    const first = str_error_r.strErrorR(13, view);
    try std.testing.expectEqualStrings("Permission denied", first);
    try std.testing.expectEqual(@as(u8, 0), view[first.len]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[2]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[21]);

    const second = str_error_r.strErrorR(0, view);
    try std.testing.expectEqualStrings("Success", second);
    try std.testing.expectEqual(@as(u8, 0), view[second.len]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[2]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[21]);
}

test "vsprintf rewrites offset views and preserves neighbor bytes" {
    var backing = [_]u8{0x5a} ** 16;
    const view = backing[4..11];

    const first = vsprintf.vscnprintf(view, "{s}", .{"abcdefghi"});
    try std.testing.expectEqual(@as(usize, 6), first);
    try std.testing.expectEqualStrings("abcdef", view[0..first]);
    try std.testing.expectEqual(@as(u8, 0), view[first]);

    const second = vsprintf.scnprintfPad(view, 12, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 5), second);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', ' ', 0 }, view);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[3]);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[11]);
}

test "zalloc re-zeroes nested extern storage after a dirty free" {
    const allocator = std.testing.allocator;
    const Cell = extern union {
        word: u32,
        bytes: [4]u8,
    };
    const Record = extern struct {
        tag: u8,
        flags: u8,
        padding: [2]u8,
        cells: [2]Cell,
    };

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expectEqual(@as(u8, 0), record.?.tag);
    try std.testing.expectEqual(@as(u8, 0), record.?.flags);
    for (record.?.padding) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    for (&record.?.cells) |*cell| {
        for (std.mem.asBytes(cell)) |byte| {
            try std.testing.expectEqual(@as(u8, 0), byte);
        }
    }

    record.?.tag = 9;
    record.?.flags = 7;
    @memset(&record.?.padding, 0xcc);
    record.?.cells[0].word = 0xffffffff;
    record.?.cells[1].bytes = .{ 1, 2, 3, 4 };
    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);

    record = try zalloc.zallocValue(allocator, Record);
    try std.testing.expectEqual(@as(u8, 0), record.?.tag);
    try std.testing.expectEqual(@as(u8, 0), record.?.flags);
    for (record.?.padding) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    for (&record.?.cells) |*cell| {
        for (std.mem.asBytes(cell)) |byte| {
            try std.testing.expectEqual(@as(u8, 0), byte);
        }
    }
}
