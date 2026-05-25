const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps mirrored allocation windows balanced" {
    slab.kmalloc_nr_allocated = 0;

    const left = slab.kmallocBytes(2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), left[0]);
    try std.testing.expectEqual(@as(u8, 0), left[1]);

    const right = slab.kmallocArray(1, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 3), right.len);
    for (right) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(left);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(right);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps mirrored caller windows fenced" {
    var backing = [_]u8{0xaa} ** 18;

    const left = str_error_r.strErrorR(12, backing[1..8]);
    try std.testing.expectEqualStrings("Cannot", left);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[8]);

    const right = str_error_r.strErrorR(0, backing[10..18]);
    try std.testing.expectEqualStrings("Success", right);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[9]);
    try std.testing.expectEqual(@as(u8, 0), backing[17]);
}

test "vsprintf keeps mirrored caller windows isolated" {
    var backing = [_]u8{0xdd} ** 14;

    const left = vsprintf.scnprintfPad(backing[1..7], 4, "{s}", .{"L"});
    try std.testing.expectEqual(@as(usize, 3), left);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xdd, 'L', ' ', ' ', ' ', 0, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd },
        &backing,
    );

    const right = vsprintf.vscnprintf(backing[8..13], "{s}", .{"mirror"});
    try std.testing.expectEqual(@as(usize, 4), right);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xdd, 'L', ' ', ' ', ' ', 0, 0xdd, 0xdd, 'm', 'i', 'r', 'r', 0, 0xdd },
        &backing,
    );
}

test "zalloc refreshes mirrored byte and value allocations" {
    const allocator = std.testing.allocator;
    const Mirror = struct {
        left: u16,
        right: u16,
        armed: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);
    bytes.?[0] = 0x11;
    bytes.?[3] = 0x22;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);

    var mirror: ?*Mirror = try zalloc.zallocValue(allocator, Mirror);
    try std.testing.expectEqual(@as(u16, 0), mirror.?.left);
    try std.testing.expectEqual(@as(u16, 0), mirror.?.right);
    try std.testing.expectEqual(false, mirror.?.armed);
    mirror.?.* = .{ .left = 7, .right = 9, .armed = true };
    zalloc.zfreeValue(allocator, Mirror, &mirror);
    try std.testing.expect(mirror == null);

    mirror = try zalloc.zallocValue(allocator, Mirror);
    defer zalloc.zfreeValue(allocator, Mirror, &mirror);
    try std.testing.expectEqual(@as(u16, 0), mirror.?.left);
    try std.testing.expectEqual(@as(u16, 0), mirror.?.right);
    try std.testing.expectEqual(false, mirror.?.armed);
}
