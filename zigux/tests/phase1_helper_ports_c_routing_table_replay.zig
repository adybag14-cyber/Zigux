const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectZeroed(bytes: []const u8) !void {
    for (bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "routing table ferries slab windows through zalloc summaries" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    const table = slab.kmallocArray(4, 24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 96), table.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(table);

    var mirror: ?[]u8 = try zalloc.zallocBytes(allocator, table.len);
    defer zalloc.zfreeBytes(allocator, &mirror);
    try expectZeroed(mirror.?);

    const known = str_error_r.strErrorR(13, table[0..24]);
    try std.testing.expectEqualStrings("Permission denied", known);
    try std.testing.expectEqual(@as(u8, 0), table[known.len]);

    const fallback = str_error_r.strErrorR(4096, table[24..48]);
    try std.testing.expectEqual(@as(usize, 23), fallback.len);
    try std.testing.expect(std.mem.startsWith(u8, fallback, "INTERNAL ERROR:"));
    try std.testing.expectEqual(@as(u8, 0), table[47]);

    const direct_len = vsprintf.scnprintf(table[48..72], "route:{d}:{s}", .{ 2, "zalloc" });
    try std.testing.expectEqual(@as(usize, 14), direct_len);
    try std.testing.expectEqualStrings("route:2:zalloc", table[48 .. 48 + direct_len]);
    try std.testing.expectEqual(@as(u8, 0), table[48 + direct_len]);

    const padded_len = vsprintf.scnprintfPad(table[72..96], 16, "{s}", .{"pad"});
    try std.testing.expect(padded_len == 15 or padded_len == 16);
    try std.testing.expectEqualSlices(u8, "pad             ", table[72..88]);
    try std.testing.expectEqual(@as(u8, 0), table[88]);

    @memcpy(mirror.?, table);
    try std.testing.expectEqualStrings("Permission denied", mirror.?[0..known.len]);
    try std.testing.expectEqualSlices(u8, fallback, mirror.?[24 .. 24 + fallback.len]);
    try std.testing.expectEqualStrings("route:2:zalloc", mirror.?[48 .. 48 + direct_len]);
    try std.testing.expectEqualSlices(u8, "pad             ", mirror.?[72..88]);

    const failed = slab.kmallocBytes(16, slab.__GFP_ZERO);
    try std.testing.expect(failed == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(table);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "routing table owner reset and slab reacquire zeroing" {
    const allocator = std.testing.allocator;
    const RouteState = struct {
        ids: [3]u16,
        last_len: usize,
        active: bool,
    };

    slab.kmalloc_nr_allocated = 0;

    var state: ?*RouteState = try zalloc.zallocValue(allocator, RouteState);
    defer zalloc.zfreeValue(allocator, RouteState, &state);
    try std.testing.expectEqualSlices(u16, &[_]u16{ 0, 0, 0 }, &state.?.ids);
    try std.testing.expectEqual(@as(usize, 0), state.?.last_len);
    try std.testing.expect(!state.?.active);

    const slot = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(slot);

    const success = str_error_r.strErrorR(0, slot[1..10]);
    try std.testing.expectEqualStrings("Success", success);
    const route_len = vsprintf.scnprintf(slot[12..32], "ok:{d}:{s}", .{ success.len, success });
    try std.testing.expectEqualStrings("ok:7:Success", slot[12 .. 12 + route_len]);

    state.?.ids = .{ 7, 12, @intCast(route_len) };
    state.?.last_len = route_len;
    state.?.active = true;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &owner);
    const owner_pad = vsprintf.scnprintfPad(owner.?, 18, "rt:{d}:{d}:{d}", .{
        state.?.ids[0],
        state.?.ids[1],
        state.?.ids[2],
    });
    try std.testing.expect(owner_pad == 17 or owner_pad == 18);
    try std.testing.expectEqualSlices(u8, "rt:7:12:12        ", owner.?[0..18]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[18]);

    zalloc.zfreeValue(allocator, RouteState, &state);
    try std.testing.expect(state == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);

    slab.kfree(slot);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const reacquired = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(reacquired);
    try expectZeroed(reacquired);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
