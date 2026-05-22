const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps zero-sized and zeroed live allocations balanced across partial frees" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    const zeroed = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        slab.kfree(empty);
        return error.TestUnexpectedResult;
    };

    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR reuses one offset window from a generated message to a shorter known one" {
    var backing = [_]u8{'~'} ** 16;
    const window = backing[3..12];

    const generated = str_error_r.strErrorR(4096, window);
    try std.testing.expectEqualStrings("INTERNAL", generated);
    try std.testing.expectEqual(@as(u8, 0), window[generated.len]);

    const known = str_error_r.strErrorR(0, window);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0), window[known.len]);
    try std.testing.expectEqual(@as(u8, '~'), backing[2]);
    try std.testing.expectEqual(@as(u8, '~'), backing[12]);
}

test "vsprintf rewrites a padded offset window to an exact-fit string" {
    var backing = [_]u8{'!'} ** 10;
    const window = backing[2..8];

    const padded = vsprintf.scnprintfPad(window, 5, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 4), padded);
    try std.testing.expectEqualStrings("ab   ", window[0..5]);
    try std.testing.expectEqual(@as(u8, 0), window[5]);

    const exact = vsprintf.scnprintf(window, "{s}", .{"wxyzq"});
    try std.testing.expectEqual(@as(usize, 5), exact);
    try std.testing.expectEqualStrings("wxyzq", window[0..exact]);
    try std.testing.expectEqual(@as(u8, 0), window[exact]);
    try std.testing.expectEqual(@as(u8, '!'), backing[1]);
    try std.testing.expectEqual(@as(u8, '!'), backing[8]);
}

test "zalloc re-zeroes nested array entries after a dirty free" {
    const allocator = std.testing.allocator;

    const Entry = struct {
        flag: bool,
        code: ?u16,
        bytes: [2]u8,
    };

    const Value = struct {
        entries: [2]Entry,
        tag: u8,
    };

    var first: ?*Value = try zalloc.zallocValue(allocator, Value);
    first.?.entries[0].flag = true;
    first.?.entries[0].code = 9;
    first.?.entries[0].bytes = .{ 0xaa, 0xbb };
    first.?.entries[1].flag = true;
    first.?.entries[1].code = 3;
    first.?.entries[1].bytes = .{ 0xcc, 0xdd };
    first.?.tag = 7;
    zalloc.zfreeValue(allocator, Value, &first);
    try std.testing.expect(first == null);

    var second: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &second);

    try std.testing.expectEqual(@as(u8, 0), second.?.tag);
    for (second.?.entries) |entry| {
        try std.testing.expectEqual(false, entry.flag);
        try std.testing.expect(entry.code == null);
        for (entry.bytes) |byte| {
            try std.testing.expectEqual(@as(u8, 0), byte);
        }
    }
}
