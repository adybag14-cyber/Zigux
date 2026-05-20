const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectFilled(slice: []const u8, value: u8) !void {
    for (slice) |item| {
        try std.testing.expectEqual(value, item);
    }
}

test "phase1 helper ports c windowed replay keeps slab allocations independent" {
    slab.kmalloc_nr_allocated = 0;

    const first: ?[]u8 = slab.kmallocBytes(6, slab.GFP_KERNEL);
    defer slab.kfree(first);
    var second: ?[]u8 = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer slab.kfree(second);

    try std.testing.expect(first != null);
    try std.testing.expect(second != null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    @memset(first.?, 0xa5);
    for (second.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try expectFilled(first.?, 0xa5);

    slab.kfree(second);
    second = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectFilled(first.?, 0xa5);
}

test "phase1 helper ports c windowed replay keeps strerror_r writes inside caller view" {
    var storage = [_]u8{0xcc} ** 48;
    const known_view = storage[7..20];
    const known = str_error_r.strErrorR(13, known_view);

    try std.testing.expectEqualStrings("Permission d", known);
    try std.testing.expectEqual(@as(u8, 0), known_view[known.len]);
    try expectFilled(storage[0..7], 0xcc);
    try expectFilled(storage[20..], 0xcc);

    var growth_storage = [_]u8{0xdd} ** 72;
    const small_view = growth_storage[4..9];
    try std.testing.expectEqualStrings("INTE", str_error_r.strErrorR(4096, small_view));
    try std.testing.expectEqual(@as(u8, 0), small_view[4]);
    try expectFilled(growth_storage[0..4], 0xdd);
    try expectFilled(growth_storage[9..], 0xdd);
}

test "phase1 helper ports c windowed replay keeps vsprintf writes inside caller view" {
    var storage = [_]u8{0xaa} ** 24;
    const view = storage[3..11];

    const truncated = vsprintf.scnprintf(view, "{s}{d}", .{ "abcdef", 12 });
    try std.testing.expectEqual(@as(usize, 7), truncated);
    try std.testing.expectEqualStrings("abcdef1", view[0..truncated]);
    try std.testing.expectEqual(@as(u8, 0), view[truncated]);
    try expectFilled(storage[0..3], 0xaa);
    try expectFilled(storage[11..], 0xaa);

    const padded = vsprintf.scnprintfPad(view, 6, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 5), padded);
    try std.testing.expectEqualStrings("xy    ", view[0..6]);
    try std.testing.expectEqual(@as(u8, 0), view[6]);
    try expectFilled(storage[0..3], 0xaa);
    try expectFilled(storage[11..], 0xaa);
}

test "phase1 helper ports c windowed replay re-zeroes nested zalloc values" {
    const allocator = std.testing.allocator;

    const Cell = struct {
        count: u16,
        bytes: [3]u8,
        enabled: bool,
    };
    const Matrix = struct {
        rows: [2]Cell,
        total: u32,
    };

    var first: ?*Matrix = try zalloc.zallocValue(allocator, Matrix);
    defer zalloc.zfreeValue(allocator, Matrix, &first);
    first.?.rows[0].count = 9;
    first.?.rows[0].bytes = .{ 1, 2, 3 };
    first.?.rows[0].enabled = true;
    first.?.rows[1].count = 7;
    first.?.rows[1].bytes = .{ 4, 5, 6 };
    first.?.rows[1].enabled = true;
    first.?.total = 99;

    zalloc.zfreeValue(allocator, Matrix, &first);
    try std.testing.expect(first == null);

    var second: ?*Matrix = try zalloc.zallocValue(allocator, Matrix);
    defer zalloc.zfreeValue(allocator, Matrix, &second);
    try std.testing.expectEqual(@as(u16, 0), second.?.rows[0].count);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0 }, &second.?.rows[0].bytes);
    try std.testing.expectEqual(false, second.?.rows[0].enabled);
    try std.testing.expectEqual(@as(u16, 0), second.?.rows[1].count);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0 }, &second.?.rows[1].bytes);
    try std.testing.expectEqual(false, second.?.rows[1].enabled);
    try std.testing.expectEqual(@as(u32, 0), second.?.total);
}
