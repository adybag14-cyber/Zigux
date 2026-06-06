const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "release ring preserves helper windows while owners recycle" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var primary_owner: ?[]u8 = slab.kmallocBytes(48, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(primary_owner);
    const primary = primary_owner.?;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var scratch: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &scratch);

    const known_window = primary[5..22];
    const known = str_error_r.strErrorR(22, known_window);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0), primary[21]);
    try std.testing.expectEqual(@as(u8, 0), primary[4]);
    try std.testing.expectEqual(@as(u8, 0), primary[22]);

    const summary = scratch.?;
    const written = vsprintf.scnprintf(summary[3..20], "err={s}", .{known});
    try std.testing.expectEqual(@as(usize, 16), written);
    try std.testing.expectEqualStrings("err=Invalid argu", summary[3 .. 3 + written]);
    try std.testing.expectEqual(@as(u8, 0), summary[3 + written]);
    try std.testing.expectEqual(@as(u8, 0), summary[2]);
    try std.testing.expectEqual(@as(u8, 0), summary[20]);

    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
    scratch = try zalloc.zallocBytes(allocator, 32);
    for (scratch.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const fallback_window = primary[24..45];
    const fallback = str_error_r.strErrorR(4096, fallback_window);
    try std.testing.expectEqualStrings("INTERNAL ERROR: stre", fallback);
    try std.testing.expectEqual(@as(u8, 0), primary[44]);
    try std.testing.expectEqual(@as(u8, 0), primary[23]);
    try std.testing.expectEqual(@as(u8, 0), primary[45]);

    slab.kfree(primary);
    primary_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "padded zalloc summaries survive slab failure and reverse release" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocArray(2, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(first);
    const second = slab.kmallocBytes(16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    var ring: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &ring);

    const padded = vsprintf.scnprintfPad(ring.?[2..18], 12, "slab={d}", .{slab.kmalloc_nr_allocated});
    try std.testing.expect(padded == 11 or padded == 12);
    try std.testing.expectEqualSlices(u8, "slab=2      ", ring.?[2..14]);
    try std.testing.expectEqual(@as(u8, 0), ring.?[14]);
    try std.testing.expectEqual(@as(u8, 0), ring.?[1]);
    try std.testing.expectEqual(@as(u8, 0), ring.?[18]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    const Value = struct {
        count: usize,
        seen: bool,
        payload: [3]u16,
    };
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(usize, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.seen);
    try std.testing.expectEqualSlices(u16, &[_]u16{ 0, 0, 0 }, &value.?.payload);
    value.?.count = 17;
    value.?.seen = true;
    value.?.payload = .{ 1, 2, 3 };
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    zalloc.zfreeBytes(allocator, &ring);
    try std.testing.expect(ring == null);
    ring = try zalloc.zallocBytes(allocator, 24);
    for (ring.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}
