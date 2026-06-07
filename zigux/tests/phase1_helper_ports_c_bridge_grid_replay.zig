const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "bridge grid preserves slab windows through strerror format and zalloc ownership" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    const grid = slab.kmallocArray(3, 24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(grid);

    try std.testing.expectEqual(@as(usize, 72), grid.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (grid) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(grid[0..24], 0xa5);
    const known = str_error_r.strErrorR(12, grid[1..24]);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqual(@as(u8, 0xa5), grid[0]);
    try std.testing.expectEqual(@as(u8, 0), grid[23]);

    @memset(grid[24..48], 0x5a);
    const fallback = str_error_r.strErrorR(8008, grid[26..48]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strer", fallback);
    try std.testing.expectEqual(@as(u8, 0x5a), grid[24]);
    try std.testing.expectEqual(@as(u8, 0x5a), grid[25]);
    try std.testing.expectEqual(@as(u8, 0), grid[47]);

    @memset(grid[48..72], 0xcc);
    const summary_window = grid[51..63];
    const padded = vsprintf.scnprintfPad(summary_window, 10, "{s}:{d}", .{ "ok", fallback.len });
    try std.testing.expect(padded == 9 or padded == 10);
    try std.testing.expectEqualSlices(u8, "ok:21     ", summary_window[0..10]);
    try std.testing.expectEqual(@as(u8, 0), summary_window[10]);
    try std.testing.expectEqual(@as(u8, 0xcc), grid[50]);
    try std.testing.expectEqual(@as(u8, 0xcc), grid[63]);

    var owned: ?[]u8 = try zalloc.zallocBytes(allocator, summary_window[0..10].len);
    defer zalloc.zfreeBytes(allocator, &owned);
    for (owned.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    @memcpy(owned.?, summary_window[0..10]);
    try std.testing.expectEqualStrings("ok:21     ", owned.?);

    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "bridge grid failure paths keep owners and accounting recoverable" {
    const allocator = std.testing.allocator;
    const Snapshot = struct {
        code: i32,
        bytes_seen: usize,
        rendered: [32]u8,
    };

    slab.kmalloc_nr_allocated = 0;
    var snapshot: ?*Snapshot = try zalloc.zallocValue(allocator, Snapshot);
    defer zalloc.zfreeValue(allocator, Snapshot, &snapshot);

    try std.testing.expectEqual(@as(i32, 0), snapshot.?.code);
    try std.testing.expectEqual(@as(usize, 0), snapshot.?.bytes_seen);
    for (snapshot.?.rendered) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocBytes(16, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const bytes = slab.kmallocBytes(18, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const rendered = str_error_r.strErrorR(13, bytes[2..18]);
    try std.testing.expectEqualStrings("Permission deni", rendered);
    try std.testing.expectEqual(@as(u8, 0), bytes[17]);

    snapshot.?.code = 13;
    snapshot.?.bytes_seen = rendered.len;
    @memset(&snapshot.?.rendered, 0xee);
    const written = vsprintf.scnprintf(&snapshot.?.rendered, "E{d}:{s}:{d}", .{ snapshot.?.code, rendered[0..4], snapshot.?.bytes_seen });
    try std.testing.expectEqual(@as(usize, 11), written);
    try std.testing.expectEqualStrings("E13:Perm:15", snapshot.?.rendered[0..written]);
    try std.testing.expectEqual(@as(u8, 0), snapshot.?.rendered[written]);

    zalloc.zfreeValue(allocator, Snapshot, &snapshot);
    try std.testing.expect(snapshot == null);
    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
