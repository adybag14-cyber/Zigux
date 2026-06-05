const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab and zalloc byte owners survive alternating helper rewrites" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;

    const slab_owner = slab.kcallocBytes(2, 8, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_owner);
    const slab_sibling = slab.kzallocBytes(12, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_sibling);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes != null);
    for (zbytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(zbytes.?, 0xee);

    const padded_window = slab_owner[1..9];
    const padded = vsprintf.scnprintfPad(padded_window, 7, "id={d}", .{42});
    try std.testing.expectEqual(@as(usize, 7), padded);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[0]);
    try std.testing.expectEqualSlices(u8, "id=42  ", slab_owner[1..8]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[8]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[9]);

    const slab_rewrite = str_error_r.strErrorR(12, slab_owner[3..11]);
    try std.testing.expectEqualStrings("Cannot ", slab_rewrite);
    try std.testing.expectEqualSlices(u8, "id", slab_owner[1..3]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[10]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[11]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[15]);

    const z_window = zbytes.?[2..15];
    const direct = vsprintf.vscnprintf(z_window, "owner-{d}", .{7});
    try std.testing.expectEqual(@as(usize, 7), direct);
    try std.testing.expectEqualSlices(u8, "owner-7", zbytes.?[2..9]);
    try std.testing.expectEqual(@as(u8, 0), zbytes.?[9]);
    try std.testing.expectEqual(@as(u8, 0xee), zbytes.?[1]);
    try std.testing.expectEqual(@as(u8, 0xee), zbytes.?[15]);

    const z_rewrite = str_error_r.strErrorR(13, z_window);
    try std.testing.expectEqualStrings("Permission d", z_rewrite);
    try std.testing.expectEqual(@as(u8, 0), zbytes.?[14]);
    try std.testing.expectEqual(@as(u8, 0xee), zbytes.?[1]);
    try std.testing.expectEqual(@as(u8, 0xee), zbytes.?[15]);

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes == null);
    zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes == null);

    zbytes = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expect(zbytes != null);
    for (zbytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "value owner churn leaves slab siblings and failure accounting stable" {
    const allocator = std.testing.allocator;
    const Payload = struct {
        ready: bool,
        count: u16,
        slot: ?[]u8,
        bytes: [4]u8,
    };

    slab.kmalloc_nr_allocated = 0;

    const guard = slab.kcallocBytes(3, 6, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(guard);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var payload: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(payload != null);
    try std.testing.expectEqual(false, payload.?.ready);
    try std.testing.expectEqual(@as(u16, 0), payload.?.count);
    try std.testing.expect(payload.?.slot == null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &payload.?.bytes);

    payload.?.ready = true;
    payload.?.count = 9;
    @memset(&payload.?.bytes, 0xa5);

    const first_render = vsprintf.scnprintf(guard[2..10], "cnt={d}", .{payload.?.count});
    try std.testing.expectEqual(@as(usize, 5), first_render);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, guard[0..2]);
    try std.testing.expectEqualSlices(u8, "cnt=9", guard[2..7]);
    try std.testing.expectEqual(@as(u8, 0), guard[7]);

    zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(payload == null);
    zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(payload == null);

    payload = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expectEqual(false, payload.?.ready);
    try std.testing.expectEqual(@as(u16, 0), payload.?.count);
    try std.testing.expect(payload.?.slot == null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &payload.?.bytes);

    const rewritten = str_error_r.strErrorR(22, guard[4..18]);
    try std.testing.expectEqualStrings("Invalid argum", rewritten);
    try std.testing.expectEqual(@as(u8, 0), guard[17]);
    try std.testing.expectEqual(@as(u8, 0), guard[0]);
    try std.testing.expectEqual(@as(u8, 0), guard[1]);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
