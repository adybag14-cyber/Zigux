const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectFallback(errnum: i32, window: []u8, rendered: []const u8) !void {
    var expected_storage: [64]u8 = undefined;
    const expected = std.fmt.bufPrint(
        &expected_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ errnum, window.len },
    ) catch unreachable;
    const expected_len = @min(expected.len, window.len - 1);

    try std.testing.expectEqualStrings(expected[0..expected_len], rendered);
    try std.testing.expectEqual(@as(u8, 0), window[expected_len]);
}

test "slab caller storage rotates through strerror and formatted zalloc copies" {
    slab.kmalloc_nr_allocated = 0;

    var slab_owner: ?[]u8 = slab.kmallocBytes(96, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer {
        slab.kfree(slab_owner);
        slab_owner = null;
    }
    const storage = slab_owner orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const known_window = storage[8..26];
    const known = str_error_r.strErrorR(22, known_window);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0), storage[7]);
    try std.testing.expectEqual(@as(u8, 0), storage[25]);
    try std.testing.expectEqual(@as(u8, 0), storage[26]);

    const fallback_window = storage[32..74];
    const fallback = str_error_r.strErrorR(9107, fallback_window);
    try expectFallback(9107, fallback_window, fallback);
    try std.testing.expectEqual(@as(u8, 0), storage[31]);
    try std.testing.expectEqual(@as(u8, 0), storage[74]);

    const allocator = std.testing.allocator;
    var copy_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 80);
    defer zalloc.zfreeBytes(allocator, &copy_owner);
    const copy = copy_owner.?;
    for (copy) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memcpy(copy[0..known.len], known);
    @memcpy(copy[24 .. 24 + fallback.len], fallback);

    const summary_window = storage[76..92];
    const summary_len = vsprintf.scnprintfPad(summary_window, 15, "rot:{d}/{d}", .{ known.len, fallback.len });
    try std.testing.expect(summary_len == 15 or summary_len == 14);
    try std.testing.expectEqualStrings("rot:16/41      ", summary_window[0..15]);
    try std.testing.expectEqual(@as(u8, 0), summary_window[15]);
    try std.testing.expectEqual(@as(u8, 0), storage[75]);
    try std.testing.expectEqual(@as(u8, 0), storage[92]);

    zalloc.zfreeBytes(allocator, &copy_owner);
    try std.testing.expect(copy_owner == null);

    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "array windows carry owner metadata through zalloc value reset" {
    slab.kmalloc_nr_allocated = 0;

    var array_owner: ?[]u8 = slab.kmallocArray(4, 24, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer {
        slab.kfree(array_owner);
        array_owner = null;
    }
    const array = array_owner orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 96), array.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (array) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const header_len = vsprintf.scnprintf(array[3..19], "slot-{d}", .{3});
    try std.testing.expectEqual(@as(usize, 6), header_len);
    try std.testing.expectEqualStrings("slot-3", array[3 .. 3 + header_len]);
    try std.testing.expectEqual(@as(u8, 0), array[2]);
    try std.testing.expectEqual(@as(u8, 0), array[9]);
    try std.testing.expectEqual(@as(u8, 0), array[19]);

    const fallback = str_error_r.strErrorR(9905, array[28..67]);
    try expectFallback(9905, array[28..67], fallback);
    try std.testing.expectEqual(@as(u8, 0), array[27]);
    try std.testing.expectEqual(@as(u8, 0), array[67]);

    const padded_len = vsprintf.scnprintfPad(array[72..90], 17, "fall:{d}", .{fallback.len});
    try std.testing.expect(padded_len == 17 or padded_len == 16);
    try std.testing.expectEqualStrings("fall:38          ", array[72..89]);
    try std.testing.expectEqual(@as(u8, 0), array[89]);
    try std.testing.expectEqual(@as(u8, 0), array[71]);
    try std.testing.expectEqual(@as(u8, 0), array[90]);

    const allocator = std.testing.allocator;
    const Rotation = struct {
        header_len: usize,
        fallback_len: usize,
        padded_len: usize,
    };
    var rotation_owner: ?*Rotation = try zalloc.zallocValue(allocator, Rotation);
    defer zalloc.zfreeValue(allocator, Rotation, &rotation_owner);

    try std.testing.expectEqual(@as(usize, 0), rotation_owner.?.header_len);
    try std.testing.expectEqual(@as(usize, 0), rotation_owner.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 0), rotation_owner.?.padded_len);

    rotation_owner.?.* = .{
        .header_len = header_len,
        .fallback_len = fallback.len,
        .padded_len = padded_len,
    };
    try std.testing.expectEqual(@as(usize, 6), rotation_owner.?.header_len);
    try std.testing.expectEqual(@as(usize, 38), rotation_owner.?.fallback_len);
    try std.testing.expect(rotation_owner.?.padded_len == 17 or rotation_owner.?.padded_len == 16);

    zalloc.zfreeValue(allocator, Rotation, &rotation_owner);
    try std.testing.expect(rotation_owner == null);

    slab.kfree(array_owner);
    array_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
