const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "recycled slab windows carry formatted bytes into resettable zalloc owners" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slab_bytes = slab.kmallocBytes(48, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(slab_bytes, 0xa5);
    const slab_window = slab_bytes[6..24];
    const padded = vsprintf.scnprintfPad(slab_window, 12, "err={d}", .{22});
    try std.testing.expect(padded == 11 or padded == 12);
    try std.testing.expectEqualSlices(u8, "err=22      ", slab_window[0..12]);
    try std.testing.expectEqual(@as(u8, 0), slab_window[12]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_bytes[5]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_bytes[24]);

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    defer zalloc.zfreeBytes(allocator, &owner);
    for (owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    @memcpy(owner.?[0..12], slab_window[0..12]);
    try std.testing.expectEqualSlices(u8, "err=22      ", owner.?[0..12]);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);

    owner = try zalloc.zallocBytes(allocator, 16);
    for (owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const recycled = str_error_r.strErrorR(12, owner.?[2..16]);
    try std.testing.expectEqualStrings("Cannot alloca", recycled);
    try std.testing.expectEqual(@as(u8, 0), owner.?[15]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[0]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[1]);

    slab.kfree(slab_bytes);
    slab_bytes = &[_]u8{};
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "caller windows can be reused for error text and vscnprintf sentinels" {
    var backing: [40]u8 = @splat(0xd3);

    const first = str_error_r.strErrorR(2, backing[4..31]);
    try std.testing.expectEqualStrings("No such file or directory", first);
    try std.testing.expectEqual(@as(u8, 0xd3), backing[3]);
    try std.testing.expectEqual(@as(u8, 0), backing[29]);
    try std.testing.expectEqual(@as(u8, 0xd3), backing[31]);

    const second = vsprintf.vscnprintf(backing[4..16], "{s}", .{"reuse-window"});
    try std.testing.expectEqual(@as(usize, 11), second);
    try std.testing.expectEqualSlices(u8, "reuse-windo", backing[4..15]);
    try std.testing.expectEqual(@as(u8, 0), backing[15]);
    try std.testing.expectEqual(@as(u8, 0xd3), backing[3]);
    try std.testing.expectEqual(@as(u8, ' '), backing[16]);
    try std.testing.expectEqual(@as(u8, 'o'), backing[17]);
    try std.testing.expectEqual(@as(u8, 'r'), backing[18]);

    const fallback = str_error_r.strErrorR(4097, backing[18..27]);
    try std.testing.expectEqualStrings("INTERNAL", fallback);
    try std.testing.expectEqual(@as(u8, 0), backing[26]);
    try std.testing.expectEqual(@as(u8, 'o'), backing[17]);
    try std.testing.expectEqual(@as(u8, 'r'), backing[27]);
}

test "zalloc value owners reset after slab allocation failure leaves accounting stable" {
    const allocator = std.testing.allocator;
    const Value = struct {
        counter: u32,
        armed: bool,
        tag: [4]u8,
    };

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.counter);
    try std.testing.expectEqual(false, value.?.armed);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &value.?.tag);

    value.?.counter = 7;
    value.?.armed = true;
    value.?.tag = .{ 'l', '1', '0', 0 };

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u32, 0), value.?.counter);
    try std.testing.expectEqual(false, value.?.armed);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &value.?.tag);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
