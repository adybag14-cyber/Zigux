const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectAll(bytes: []const u8, expected: u8) !void {
    for (bytes) |value| {
        try std.testing.expectEqual(expected, value);
    }
}

test "phase 1 helper ports C keep zero-length caller views inert" {
    slab.kmalloc_nr_allocated = 0;

    const owner = slab.kmallocArray(4, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectAll(owner, 0);

    @memset(owner, 0xa5);
    const empty_mid = owner[7..7];
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(empty_mid, "ignored={d}", .{99}));
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintfPad(empty_mid, 0, "pad", .{}));
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(4096, empty_mid));
    try expectAll(owner, 0xa5);

    var optional_bytes: ?[]u8 = try zalloc.zallocBytes(std.testing.allocator, 0);
    try std.testing.expect(optional_bytes != null);
    try std.testing.expectEqual(@as(usize, 0), optional_bytes.?.len);
    zalloc.zfreeBytes(std.testing.allocator, &optional_bytes);
    try std.testing.expect(optional_bytes == null);

    var reacquired: ?[]u8 = try zalloc.zallocBytes(std.testing.allocator, 5);
    defer zalloc.zfreeBytes(std.testing.allocator, &reacquired);
    try expectAll(reacquired.?, 0);
}

test "phase 1 helper ports C preserve slab windows across bounded fallback and padded tails" {
    slab.kmalloc_nr_allocated = 0;

    const owner = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectAll(owner, 0);

    @memset(owner, 0xcc);
    owner[3] = 0x51;
    owner[16] = 0x52;
    owner[26] = 0x53;

    const fallback = str_error_r.strErrorR(4096, owner[4..16]);
    try std.testing.expectEqual(@as(usize, 11), fallback.len);
    try std.testing.expectEqualStrings("INTERNAL ER", fallback);
    try std.testing.expectEqual(@as(u8, 0x51), owner[3]);
    try std.testing.expectEqual(@as(u8, 0), owner[15]);
    try std.testing.expectEqual(@as(u8, 0x52), owner[16]);

    const padded_len = vsprintf.scnprintfPad(owner[17..26], 8, "id={d}", .{7});
    try std.testing.expectEqual(@as(usize, 8), padded_len);
    try std.testing.expectEqualStrings("id=7    ", owner[17..25]);
    try std.testing.expectEqual(@as(u8, 0), owner[25]);
    try std.testing.expectEqual(@as(u8, 0x53), owner[26]);

    const direct_len = vsprintf.vscnprintf(owner[27..32], "{s}", .{"tail"});
    try std.testing.expectEqual(@as(usize, 4), direct_len);
    try std.testing.expectEqualStrings("tail", owner[27..31]);
    try std.testing.expectEqual(@as(u8, 0), owner[31]);

    const value = try zalloc.zallocValue(std.testing.allocator, struct {
        count: u32,
        ready: bool,
        marker: u8,
    });
    defer std.testing.allocator.destroy(value);
    try std.testing.expectEqual(@as(u32, 0), value.count);
    try std.testing.expectEqual(false, value.ready);
    try std.testing.expectEqual(@as(u8, 0), value.marker);
}
