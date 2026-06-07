const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectAllEqual(bytes: []const u8, value: u8) !void {
    for (bytes) |item| {
        try std.testing.expectEqual(value, item);
    }
}

test "checkpoint ring preserves slab records through strerror and formatter windows" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const ring = slab.kmallocArray(3, 32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(ring);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectAllEqual(ring, 0);

    @memset(ring, 0x91);
    const known_window = ring[4..28];
    const known = str_error_r.strErrorR(12, known_window);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try expectAllEqual(ring[0..4], 0x91);
    try std.testing.expectEqual(@as(u8, 0), ring[4 + known.len]);
    try expectAllEqual(ring[4 + known.len + 1 .. 32], 0x91);

    const padded_window = ring[36..50];
    const padded_len = vsprintf.scnprintfPad(padded_window, 11, "ck:{d}:{s}", .{ known.len, "a" });
    try std.testing.expect(padded_len == 10 or padded_len == 11);
    try std.testing.expectEqualStrings("ck:22:a    ", padded_window[0..11]);
    try std.testing.expectEqual(@as(u8, 0), padded_window[11]);
    try expectAllEqual(ring[32..36], 0x91);
    try expectAllEqual(ring[50..64], 0x91);

    var copy_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &copy_owner);
    try expectAllEqual(copy_owner.?, 0);

    const copied_len = vsprintf.scnprintf(copy_owner.?[6..36], "ring:{s}:{d}", .{ known[0..6], padded_len });
    try std.testing.expectEqualStrings("ring:Cannot:", copy_owner.?[6..18]);
    try std.testing.expectEqual(@as(u8, 0), copy_owner.?[6 + copied_len]);
    try expectAllEqual(copy_owner.?[0..6], 0);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &copy_owner);
    try std.testing.expect(copy_owner == null);

    copy_owner = try zalloc.zallocBytes(allocator, 16);
    defer zalloc.zfreeBytes(allocator, &copy_owner);
    try expectAllEqual(copy_owner.?, 0);
}

test "checkpoint ring resets zalloc values while slab fallback records stay balanced" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_record = slab.kmallocBytes(56, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_record);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectAllEqual(slab_record, 0);

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 64);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    try expectAllEqual(zbytes.?, 0);

    const fallback = str_error_r.strErrorR(7070, zbytes.?[5..42]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r", fallback[0..26]);
    try std.testing.expectEqual(@as(u8, 0), zbytes.?[5 + fallback.len]);
    try expectAllEqual(zbytes.?[0..5], 0);
    try expectAllEqual(zbytes.?[43..], 0);

    const Checkpoint = struct {
        id: u32,
        fallback_len: usize,
        ok: bool,
    };

    var value: ?*Checkpoint = try zalloc.zallocValue(allocator, Checkpoint);
    defer zalloc.zfreeValue(allocator, Checkpoint, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.id);
    try std.testing.expectEqual(@as(usize, 0), value.?.fallback_len);
    try std.testing.expectEqual(false, value.?.ok);

    value.?.id = 7;
    value.?.fallback_len = fallback.len;
    value.?.ok = true;

    const record_len = vsprintf.vscnprintf(slab_record[8..44], "cp:{d}:{d}:{any}", .{
        value.?.id,
        value.?.fallback_len,
        value.?.ok,
    });
    try std.testing.expectEqualStrings("cp:7:36:true", slab_record[8 .. 8 + record_len]);
    try std.testing.expectEqual(@as(u8, 0), slab_record[8 + record_len]);
    try expectAllEqual(slab_record[0..8], 0);

    zalloc.zfreeValue(allocator, Checkpoint, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Checkpoint);
    defer zalloc.zfreeValue(allocator, Checkpoint, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.id);
    try std.testing.expectEqual(@as(usize, 0), value.?.fallback_len);
    try std.testing.expectEqual(false, value.?.ok);

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
