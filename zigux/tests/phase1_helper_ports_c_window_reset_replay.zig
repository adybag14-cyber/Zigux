const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports c window reset replay" {
    slab.kmalloc_nr_allocated = 0;

    var plain: ?[]u8 = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memset(plain.?, 0xaa);

    const zeroed = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(plain);
    plain = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var known_storage = [_]u8{'#'} ** 12;
    const known = str_error_r.strErrorR(0, known_storage[3..9]);
    try std.testing.expectEqualStrings("Succe", known);
    try std.testing.expectEqualSlices(u8, "###Succe", known_storage[0..8]);
    try std.testing.expectEqual(@as(u8, 0), known_storage[8]);
    try std.testing.expectEqual(@as(u8, '#'), known_storage[9]);

    var unknown_storage = [_]u8{'!'} ** 16;
    const unknown = str_error_r.strErrorR(4096, unknown_storage[2..12]);
    try std.testing.expectEqualStrings("INTERNAL ", unknown);
    try std.testing.expectEqualSlices(u8, "!!INTERNAL ", unknown_storage[0..11]);
    try std.testing.expectEqual(@as(u8, 0), unknown_storage[11]);
    try std.testing.expectEqual(@as(u8, '!'), unknown_storage[12]);

    var terminator_only: [1]u8 = .{0xaa};
    const terminator_only_written = vsprintf.scnprintf(&terminator_only, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), terminator_only_written);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);

    var padded: [7]u8 = undefined;
    const padded_written = vsprintf.scnprintfPad(&padded, 5, "{d}", .{42});
    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualSlices(u8, "42   ", padded[0..5]);
    try std.testing.expectEqual(@as(u8, 0), padded[5]);

    const reused_written = vsprintf.scnprintf(&padded, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 2), reused_written);
    try std.testing.expectEqualStrings("xy", padded[0..reused_written]);
    try std.testing.expectEqual(@as(u8, 0), padded[2]);

    const allocator = std.testing.allocator;
    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    @memset(bytes.?, 0xcc);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const Nested = struct {
        count: usize,
        flag: bool,
        maybe: ?u8,
    };
    var value: ?*Nested = try zalloc.zallocValue(allocator, Nested);
    try std.testing.expect(value != null);
    try std.testing.expectEqual(@as(usize, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.flag);
    try std.testing.expectEqual(@as(?u8, null), value.?.maybe);
    zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expect(value == null);
}
