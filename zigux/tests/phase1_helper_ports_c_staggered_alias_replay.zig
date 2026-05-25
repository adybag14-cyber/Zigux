const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps mixed allocation counters balanced across staggered frees" {
    slab.kmalloc_nr_allocated = 0;

    const zero = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const array = slab.kmallocArray(3, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 0), zero.len);
    try std.testing.expectEqual(@as(usize, 6), array.len);
    for (array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(zero);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR refreshes tight caller windows without leaking prior bytes" {
    var single: [1]u8 = [_]u8{0xaa};
    const empty = str_error_r.strErrorR(0, &single);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, 0), single[0]);

    var tiny: [2]u8 = [_]u8{ 0xaa, 0xbb };
    const clipped = str_error_r.strErrorR(13, &tiny);
    try std.testing.expectEqualStrings("P", clipped);
    try std.testing.expectEqual(@as(u8, 'P'), tiny[0]);
    try std.testing.expectEqual(@as(u8, 0), tiny[1]);

    var unknown: [8]u8 = [_]u8{0xcc} ** 8;
    const rendered = str_error_r.strErrorR(4096, &unknown);
    try std.testing.expectEqualStrings("INTERNA", rendered);
    try std.testing.expectEqual(@as(u8, 0), unknown[7]);
}

test "vsprintf clamps logical size and terminator-only windows cleanly" {
    var terminator_only: [1]u8 = [_]u8{0xaa};
    const empty_written = vsprintf.scnprintf(&terminator_only, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);

    var padded: [6]u8 = [_]u8{0xaa} ** 6;
    const pad_written = vsprintf.scnprintfPad(&padded, 9, "{s}", .{"Z"});
    try std.testing.expectEqual(@as(usize, 4), pad_written);
    try std.testing.expectEqualStrings("Z    ", padded[0 .. padded.len - 1]);
    try std.testing.expectEqual(@as(u8, 0), padded[padded.len - 1]);

    var direct: [5]u8 = [_]u8{0xaa} ** 5;
    const direct_written = vsprintf.vscnprintf(&direct, "{s}", .{"longer"});
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqualStrings("long", direct[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), direct[4]);
}

test "zalloc re-zeroes reused bytes and keeps free helpers idempotent on null" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [3]u8,
        flag: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0x5a);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var value: ?*Value = null;
    zalloc.zfreeValue(allocator, Value, &value);
    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(std.mem.zeroes([3]u8), value.?.bytes);
    try std.testing.expectEqual(false, value.?.flag);
}
