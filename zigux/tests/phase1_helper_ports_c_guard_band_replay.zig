const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab preserves counters across zero-length guard-band allocations" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zero_array = slab.kmallocArray(0, 9, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps caller guard bands intact" {
    var backing = [_]u8{0xa5} ** 14;

    const empty = str_error_r.strErrorR(0, backing[2..2]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqualSlices(u8, &([_]u8{0xa5} ** 14), &backing);

    const tiny = str_error_r.strErrorR(22, backing[3..4]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xa5, 0xa5, 0xa5, 0, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5 },
        &backing,
    );

    const generated = str_error_r.strErrorR(4096, backing[8..10]);
    try std.testing.expectEqualStrings("I", generated);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xa5, 0xa5, 0xa5, 0, 0xa5, 0xa5, 0xa5, 0xa5, 'I', 0, 0xa5, 0xa5, 0xa5, 0xa5 },
        &backing,
    );
}

test "vsprintf confines writes to interior caller windows" {
    var backing = [_]u8{0xc3} ** 14;

    const padded = vsprintf.scnprintfPad(backing[2..7], 4, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 3), padded);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xc3, 0xc3, 'x', 'y', ' ', ' ', 0, 0xc3, 0xc3, 0xc3, 0xc3, 0xc3, 0xc3, 0xc3 },
        &backing,
    );

    const rendered = vsprintf.vscnprintf(backing[8..12], "{d}", .{42});
    try std.testing.expectEqual(@as(usize, 2), rendered);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xc3, 0xc3, 'x', 'y', ' ', ' ', 0, 0xc3, '4', '2', 0, 0xc3, 0xc3, 0xc3 },
        &backing,
    );
}

test "zalloc keeps zeroed byte slices and values independent" {
    const allocator = std.testing.allocator;
    const Record = struct {
        left: u8,
        right: u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    try std.testing.expectEqualDeep(std.mem.zeroes(Record), record.?.*);

    record.?.left = 7;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u8, 7), record.?.left);

    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);

    var rebound: ?[]u8 = try zalloc.zallocBytes(allocator, 2);
    defer zalloc.zfreeBytes(allocator, &rebound);
    try std.testing.expect(rebound != null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, rebound.?);
}
