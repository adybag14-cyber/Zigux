const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "splice chain keeps slab windows and zalloc summaries isolated" {
    slab.kmalloc_nr_allocated = 0;

    var slab_owner: ?[]u8 = slab.kmallocBytes(64, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(slab_owner);

    @memset(slab_owner.?, 0xee);
    const window = slab_owner.?[5..37];
    const rendered = str_error_r.strErrorR(8123, window);

    try std.testing.expectEqual(@as(usize, window.len - 1), rendered.len);
    try std.testing.expect(std.mem.startsWith(u8, rendered, "INTERNAL ERROR: strerror_r(8123"));
    try std.testing.expectEqual(@as(u8, 0xee), slab_owner.?[4]);
    try std.testing.expectEqual(@as(u8, 0), window[rendered.len]);
    try std.testing.expectEqual(@as(u8, 0xee), slab_owner.?[37]);

    var copied: ?[]u8 = try zalloc.zallocBytes(std.testing.allocator, rendered.len + 1);
    defer zalloc.zfreeBytes(std.testing.allocator, &copied);
    @memcpy(copied.?[0..rendered.len], rendered);
    try std.testing.expectEqual(@as(u8, 0), copied.?[rendered.len]);

    var summary: [20]u8 = @splat(0xaa);
    const written = vsprintf.scnprintfPad(&summary, 12, "{s}:{d}", .{ copied.?[0..3], rendered.len });
    try std.testing.expect(written == 11 or written == 12);
    try std.testing.expectEqualStrings("INT:31      ", summary[0..12]);
    try std.testing.expectEqual(@as(u8, 0), summary[12]);
    try std.testing.expectEqual(@as(u8, 0xaa), summary[13]);

    zalloc.zfreeBytes(std.testing.allocator, &copied);
    try std.testing.expect(copied == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "known error splice preserves zeroed owners and failure accounting" {
    slab.kmalloc_nr_allocated = 0;

    const Value = struct {
        errno: i32,
        seen: bool,
        bytes: [3]u8,
    };

    var value: ?*Value = try zalloc.zallocValue(std.testing.allocator, Value);
    defer zalloc.zfreeValue(std.testing.allocator, Value, &value);
    try std.testing.expectEqual(@as(i32, 0), value.?.errno);
    try std.testing.expectEqual(false, value.?.seen);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);

    var known_owner: ?[]u8 = try zalloc.zallocBytes(std.testing.allocator, 18);
    defer zalloc.zfreeBytes(std.testing.allocator, &known_owner);
    const known = str_error_r.strErrorR(22, known_owner.?);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0), known_owner.?[known.len]);
    try std.testing.expectEqual(@as(u8, 0), known_owner.?[known.len + 1]);

    var slab_record: ?[]u8 = slab.kmallocArray(3, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(slab_record);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_record.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const record_len = vsprintf.scnprintf(slab_record.?, "{s}:{d}", .{ known[0..7], known.len });
    try std.testing.expectEqualStrings("Invalid:16", slab_record.?[0..record_len]);
    try std.testing.expectEqual(@as(u8, 0), slab_record.?[record_len]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(slab_record);
    slab_record = null;
    zalloc.zfreeBytes(std.testing.allocator, &known_owner);
    zalloc.zfreeValue(std.testing.allocator, Value, &value);

    try std.testing.expect(known_owner == null);
    try std.testing.expect(value == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
