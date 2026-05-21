const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 slab staggered zero and nonzero allocations stay balanced" {
    slab.kmalloc_nr_allocated = 0;

    var zero_live: ?[]u8 = slab.kmallocBytes(0, slab.GFP_KERNEL);
    defer slab.kfree(zero_live);
    try std.testing.expect(zero_live != null);
    try std.testing.expectEqual(@as(usize, 0), zero_live.?.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const array_live = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer slab.kfree(array_live);
    try std.testing.expect(array_live != null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (array_live.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(zero_live);
    zero_live = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "lane10 strErrorR keeps sibling views independent across known and generated writes" {
    var backing = [_]u8{0xaa} ** 48;

    const known_view = backing[2..10];
    const known = str_error_r.strErrorR(0, known_view);
    try std.testing.expectEqual(@intFromPtr(known_view.ptr), @intFromPtr(known.ptr));
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0), known_view[known.len]);

    const generated_view = backing[20..38];
    const generated = str_error_r.strErrorR(4096, generated_view);
    try std.testing.expectEqual(@intFromPtr(generated_view.ptr), @intFromPtr(generated.ptr));
    try std.testing.expect(std.mem.startsWith(u8, generated, "INTERNAL ERROR: "));
    try std.testing.expectEqual(@as(u8, 0), generated_view[generated.len]);

    try std.testing.expectEqual(@as(u8, 0xaa), backing[1]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[10]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[19]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[38]);
    try std.testing.expectEqualStrings("Success", known_view[0..known.len]);
}

test "lane10 vsprintf staggered caller views stay reusable and bounded" {
    var backing = [_]u8{0xcc} ** 24;

    const left_view = backing[1..8];
    const left_written = vsprintf.scnprintf(left_view, "{s}", .{"abcdefghi"});
    try std.testing.expectEqual(@as(usize, 6), left_written);
    try std.testing.expectEqualStrings("abcdef", left_view[0..left_written]);
    try std.testing.expectEqual(@as(u8, 0), left_view[left_written]);

    const right_view = backing[12..20];
    _ = vsprintf.scnprintfPad(right_view, 5, "{s}", .{"xy"});
    try std.testing.expectEqualStrings("xy   ", right_view[0..5]);
    try std.testing.expectEqual(@as(u8, 0), right_view[5]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[8]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[11]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[20]);

    const reused = vsprintf.vscnprintf(right_view, "{d}", .{42});
    try std.testing.expectEqual(@as(usize, 2), reused);
    try std.testing.expectEqualStrings("42", right_view[0..reused]);
    try std.testing.expectEqual(@as(u8, 0), right_view[reused]);
}

test "lane10 zalloc alternates byte and extern-union zeroing after dirty frees" {
    const allocator = std.testing.allocator;

    const Payload = extern union {
        word: u32,
        bytes: [4]u8,
    };
    const Cell = extern struct {
        tag: u8,
        payload: Payload,
        tail: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    @memset(bytes.?, 0x5a);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var cell: ?*Cell = try zalloc.zallocValue(allocator, Cell);
    defer zalloc.zfreeValue(allocator, Cell, &cell);
    try std.testing.expect(cell != null);
    try std.testing.expectEqual(@as(u8, 0), cell.?.tag);
    try std.testing.expectEqual(@as(u32, 0), cell.?.payload.word);
    try std.testing.expectEqual(@as(u16, 0), cell.?.tail);
    cell.?.tag = 7;
    cell.?.payload.bytes = .{ 1, 2, 3, 4 };
    cell.?.tail = 9;
    zalloc.zfreeValue(allocator, Cell, &cell);
    try std.testing.expect(cell == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    cell = try zalloc.zallocValue(allocator, Cell);
    try std.testing.expect(cell != null);
    try std.testing.expectEqual(@as(u8, 0), cell.?.tag);
    try std.testing.expectEqual(@as(u32, 0), cell.?.payload.word);
    try std.testing.expectEqual(@as(u16, 0), cell.?.tail);
}
