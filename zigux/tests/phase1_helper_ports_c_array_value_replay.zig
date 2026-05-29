const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "array and value allocations survive mixed formatter views" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    var slab_bytes: ?[]u8 = slab.kmallocArray(3, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const visible = vsprintf.scnprintf(slab_bytes.?[2..10], "{s}:{d}", .{ "arr", slab_bytes.?.len });
    try std.testing.expectEqual(@as(usize, 6), visible);
    try std.testing.expectEqualStrings("arr:12", slab_bytes.?[2 .. 2 + visible]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes.?[2 + visible]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes.?[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes.?[1]);

    const State = struct {
        count: u32,
        failed: bool,
        text: [16]u8,
    };

    var state: ?*State = try zalloc.zallocValue(allocator, State);
    defer zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expectEqual(@as(u32, 0), state.?.count);
    try std.testing.expectEqual(false, state.?.failed);
    try std.testing.expectEqualSlices(u8, &([_]u8{0} ** 16), &state.?.text);

    const rendered = str_error_r.strErrorR(22, state.?.text[0..]);
    try std.testing.expectEqualStrings("Invalid argumen", rendered);
    try std.testing.expectEqual(@as(u8, 0), state.?.text[rendered.len]);

    zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expect(state == null);
    slab.kfree(slab_bytes);
    slab_bytes = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "slab fail paths and zalloc buffers do not disturb caller-owned windows" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    bytes.?[0] = 'L';
    bytes.?[1] = ':';
    const fallback = str_error_r.strErrorR(4096, bytes.?[2..12]);
    try std.testing.expectEqualStrings("INTERNAL ", fallback);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[2 + fallback.len]);
    try std.testing.expectEqualStrings("L:", bytes.?[0..2]);

    const written = vsprintf.vscnprintf(bytes.?[12..], "{s}{d}", .{ "z", fallback.len });
    try std.testing.expectEqual(@as(usize, 2), written);
    try std.testing.expectEqualStrings("z9", bytes.?[12 .. 12 + written]);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[12 + written]);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
