const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectZeroed(bytes: []const u8) !void {
    for (bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "slab windows pivot from fallback errors to padded summaries" {
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kzallocBytes(48, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(slab_bytes);

    const fallback = str_error_r.strErrorR(7007, slab_bytes[4..36]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(7007", fallback);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[35]);
    try expectZeroed(slab_bytes[0..4]);
    try expectZeroed(slab_bytes[36..48]);

    const known = str_error_r.strErrorR(22, slab_bytes[8..25]);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[24]);

    const padded_written = vsprintf.scnprintfPad(slab_bytes[26..39], 11, "piv={d}", .{known.len});
    try std.testing.expect(padded_written == 11 or padded_written == 10);
    try std.testing.expectEqualStrings("piv=16     ", slab_bytes[26..37]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[37]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[38]);

    try std.testing.expect(slab.kmallocBytes(16, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 4, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc owners relay formatted text into slab arrays and reacquire zeroed" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 56);
    defer zalloc.zfreeBytes(allocator, &owner);
    try expectZeroed(owner.?);

    const fallback = str_error_r.strErrorR(9009, owner.?[6..45]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(9009, [buf]", fallback);
    try std.testing.expectEqual(@as(u8, 0), owner.?[44]);
    try expectZeroed(owner.?[0..6]);
    try expectZeroed(owner.?[45..56]);

    const compact_written = vsprintf.scnprintf(owner.?[10..28], "relay:{d}:{d}", .{ fallback.len, owner.?.len });
    try std.testing.expectEqual(@as(usize, 11), compact_written);
    try std.testing.expectEqualStrings("relay:38:56", owner.?[10 .. 10 + compact_written]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[21]);

    const slab_array = slab.kcallocBytes(4, 12, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(slab_array);

    const summary_written = vsprintf.scnprintf(slab_array[12..24], "z:{d}", .{compact_written});
    try std.testing.expectEqual(@as(usize, 4), summary_written);
    try std.testing.expectEqualStrings("z:11", slab_array[12 .. 12 + summary_written]);
    try std.testing.expectEqual(@as(u8, 0), slab_array[16]);

    const known = str_error_r.strErrorR(0, slab_array[24..32]);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0), slab_array[31]);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);

    owner = try zalloc.zallocBytes(allocator, 16);
    try expectZeroed(owner.?);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
