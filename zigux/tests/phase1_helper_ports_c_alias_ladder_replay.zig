const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps allocation counts balanced across staggered frees and failed reclaim-less calls" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    const second = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (second) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.slabIsAvailable());
}

test "strErrorR keeps caller windows fenced while reusing inner views" {
    var backing = [_]u8{'#'} ** 20;
    const outer = str_error_r.strErrorR(12, backing[4..]);
    try std.testing.expectEqualStrings("Cannot allocate", outer);
    try std.testing.expectEqualSlices(u8, "####", backing[0..4]);
    const prefix_before_inner = backing[8];
    const suffix_before_inner = backing[17];

    const inner = str_error_r.strErrorR(4096, backing[9..17]);
    try std.testing.expectEqualStrings("INTERNA", inner);
    try std.testing.expectEqual(prefix_before_inner, backing[8]);
    try std.testing.expectEqual(@as(u8, 0), backing[16]);
    try std.testing.expectEqual(suffix_before_inner, backing[17]);
}

test "vsprintf reuses offset caller windows without disturbing surrounding sentinels" {
    var backing = [_]u8{'!'} ** 12;

    const padded = vsprintf.scnprintfPad(backing[2..10], 5, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 4), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', 'x', 'y', ' ', ' ', ' ', 0, '!', '!', '!', '!' }, &backing);

    const direct = vsprintf.vscnprintf(backing[6..11], "{d}", .{42});
    try std.testing.expectEqual(@as(usize, 2), direct);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', 'x', 'y', ' ', ' ', '4', '2', 0, '!', '!' }, backing[0..11]);
    try std.testing.expectEqual(@as(u8, '!'), backing[11]);
}

test "zalloc reacquires fresh zeroed owners after in-place release resets" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [3]u8,
        enabled: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0x5a);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 2);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expect(value != null);
    value.?.bytes = .{ 1, 2, 3 };
    value.?.enabled = true;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);
    try std.testing.expectEqual(false, value.?.enabled);
}
