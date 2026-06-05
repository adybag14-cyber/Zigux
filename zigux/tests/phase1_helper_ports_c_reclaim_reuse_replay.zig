const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const ReclaimValue = struct {
    generation: u32,
    active: bool,
    label: [8]u8,
    bytes: ?[]u8,
};

test "slab formatted windows can be released before zalloc zeroed reacquire" {
    slab.kmalloc_nr_allocated = 0;

    const owner = slab.kmallocBytes(48, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    const owner_len = owner.len;

    const formatted = owner[4..24];
    const formatted_len = vsprintf.scnprintf(formatted, "lane10:{d}:{s}", .{ 10, "slab" });
    try std.testing.expectEqualStrings("lane10:10:slab", formatted[0..formatted_len]);
    try std.testing.expectEqual(@as(u8, 0), formatted[formatted_len]);

    const message = str_error_r.strErrorR(22, owner[24..42]);
    try std.testing.expectEqualStrings("Invalid argument", message);
    try std.testing.expectEqual(@as(u8, 0), owner[24 + message.len]);

    for (owner[0..4]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    for (owner[42..]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(owner);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const allocator = std.testing.allocator;
    var reacquired: ?[]u8 = try zalloc.zallocBytes(allocator, owner_len);
    defer zalloc.zfreeBytes(allocator, &reacquired);

    for (reacquired.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const fallback = str_error_r.strErrorR(4096, reacquired.?[3..35]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096", fallback);
    try std.testing.expectEqual(@as(u8, 0), reacquired.?[3 + fallback.len]);
    try std.testing.expectEqual(@as(u8, 0), reacquired.?[0]);
    try std.testing.expectEqual(@as(u8, 0), reacquired.?[1]);
    try std.testing.expectEqual(@as(u8, 0), reacquired.?[2]);

    zalloc.zfreeBytes(allocator, &reacquired);
    try std.testing.expect(reacquired == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "zalloc value owners reset while slab siblings preserve allocation accounting" {
    slab.kmalloc_nr_allocated = 0;

    const allocator = std.testing.allocator;
    var value: ?*ReclaimValue = try zalloc.zallocValue(allocator, ReclaimValue);
    defer zalloc.zfreeValue(allocator, ReclaimValue, &value);

    try std.testing.expectEqual(@as(u32, 0), value.?.generation);
    try std.testing.expectEqual(false, value.?.active);
    try std.testing.expect(value.?.bytes == null);
    for (value.?.label) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    value.?.generation = 3;
    value.?.active = true;
    @memcpy(value.?.label[0..6], "reuse!");

    const sibling = slab.kmallocArray(3, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(sibling);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const render_len = vsprintf.vscnprintf(sibling[2..18], "gen={d}:{s}", .{ value.?.generation, value.?.label[0..6] });
    try std.testing.expectEqualStrings("gen=3:reuse!", sibling[2 .. 2 + render_len]);
    try std.testing.expectEqual(@as(u8, 0), sibling[2 + render_len]);

    const no_reclaim = slab.kmallocBytes(16, slab.__GFP_ZERO);
    try std.testing.expect(no_reclaim == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeValue(allocator, ReclaimValue, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, ReclaimValue);
    try std.testing.expectEqual(@as(u32, 0), value.?.generation);
    try std.testing.expectEqual(false, value.?.active);
    try std.testing.expect(value.?.bytes == null);
    for (value.?.label) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expectEqualStrings("gen=3:reuse!", sibling[2 .. 2 + render_len]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
