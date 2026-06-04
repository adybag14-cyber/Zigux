const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "helper ports C roundtrip matrix preserves zeroing and ownership boundaries" {
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocArray(3, 16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(usize, 48), slab_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const formatted = vsprintf.scnprintf(slab_bytes[0..16], "slot={d}:{s}", .{ 7, "ok" });
    try std.testing.expectEqual(@as(usize, 9), formatted);
    try std.testing.expectEqualStrings("slot=7:ok", slab_bytes[0..formatted]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[formatted]);

    const err = str_error_r.strErrorR(22, slab_bytes[16..40]);
    try std.testing.expectEqualStrings("Invalid argument", err);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[16 + err.len]);

    const allocator = std.testing.allocator;
    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, formatted + err.len + 1);
    defer zalloc.zfreeBytes(allocator, &owner);
    for (owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memcpy(owner.?[0..formatted], slab_bytes[0..formatted]);
    owner.?[formatted] = '|';
    @memcpy(owner.?[formatted + 1 ..], err);
    try std.testing.expectEqualStrings("slot=7:ok|Invalid argument", owner.?);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "helper ports C caller windows compose padded formatting and fallback errors" {
    slab.kmalloc_nr_allocated = 0;

    const backing = slab.kmallocBytes(64, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(backing);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(backing, 0x5a);

    const padded_written = vsprintf.scnprintfPad(backing[5..20], 10, "x{d}", .{9});
    try std.testing.expectEqual(@as(usize, 10), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x5a, 0x5a, 0x5a, 0x5a, 0x5a }, backing[0..5]);
    try std.testing.expectEqualStrings("x9        ", backing[5..15]);
    try std.testing.expectEqual(@as(u8, 0), backing[15]);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[20]);

    const fallback = str_error_r.strErrorR(4096, backing[24..34]);
    try std.testing.expectEqualStrings("INTERNAL ", fallback);
    try std.testing.expectEqual(@as(u8, 0), backing[33]);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[23]);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[34]);

    const MatrixCell = struct {
        count: u16,
        active: bool,
        label: [4]u8,
    };

    const allocator = std.testing.allocator;
    var cell: ?*MatrixCell = try zalloc.zallocValue(allocator, MatrixCell);
    defer zalloc.zfreeValue(allocator, MatrixCell, &cell);
    try std.testing.expectEqual(@as(u16, 0), cell.?.count);
    try std.testing.expectEqual(false, cell.?.active);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &cell.?.label);

    cell.?.count = @intCast(padded_written + fallback.len);
    cell.?.active = true;
    @memcpy(&cell.?.label, "c10!");
    try std.testing.expectEqual(@as(u16, 19), cell.?.count);
    try std.testing.expect(cell.?.active);

    zalloc.zfreeValue(allocator, MatrixCell, &cell);
    try std.testing.expect(cell == null);
}
