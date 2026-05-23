const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab tracks fail then success transitions across multiple live allocations" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const first = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const second = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (second) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR covers the current known errno catalog exactly" {
    var success: [16]u8 = undefined;
    var nomem: [32]u8 = undefined;
    var denied: [32]u8 = undefined;
    var invalid: [32]u8 = undefined;

    try std.testing.expectEqualStrings("Success", str_error_r.strErrorR(0, &success));
    try std.testing.expectEqualStrings("Cannot allocate memory", str_error_r.strErrorR(12, &nomem));
    try std.testing.expectEqualStrings("Permission denied", str_error_r.strErrorR(13, &denied));
    try std.testing.expectEqualStrings("Invalid argument", str_error_r.strErrorR(22, &invalid));
}

test "vsprintf keeps direct and padded exact-fit renders in lockstep" {
    var direct: [8]u8 = undefined;
    var padded: [8]u8 = undefined;

    const direct_written = vsprintf.vscnprintf(&direct, "{s}:{d}", .{ "zigux", 7 });
    const padded_written = vsprintf.scnprintfPad(&padded, 7, "{s}:{d}", .{ "zigux", 7 });

    try std.testing.expectEqual(@as(usize, 7), direct_written);
    try std.testing.expectEqual(direct_written, padded_written);
    try std.testing.expectEqualStrings("zigux:7", direct[0..direct_written]);
    try std.testing.expectEqualStrings(direct[0..direct_written], padded[0..padded_written]);
    try std.testing.expectEqual(@as(u8, 0), direct[direct_written]);
    try std.testing.expectEqual(@as(u8, 0), padded[padded_written]);
}

test "zalloc cleanup stays null-safe before and after nested value lifetimes" {
    const allocator = std.testing.allocator;
    const Value = struct {
        counts: [2]u16,
        nested: struct {
            flag: bool,
            level: u8,
        },
        maybe: ?*u8,
    };

    var bytes: ?[]u8 = null;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = null;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer if (bytes != null) zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer if (value != null) zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqualSlices(u16, &[_]u16{ 0, 0 }, &value.?.counts);
    try std.testing.expectEqual(false, value.?.nested.flag);
    try std.testing.expectEqual(@as(u8, 0), value.?.nested.level);
    try std.testing.expect(value.?.maybe == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
