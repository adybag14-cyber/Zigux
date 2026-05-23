const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 slab replay keeps counts balanced across reversed frees" {
    slab.kmalloc_nr_allocated = 0;

    var first: ?[]u8 = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer slab.kfree(first);
    try std.testing.expect(first != null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (first.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var second: ?[]u8 = slab.kmallocArray(2, 3, slab.GFP_KERNEL);
    defer slab.kfree(second);
    try std.testing.expect(second != null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(second);
    second = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(first);
    first = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(1, 0) == null);
}

test "lane10 strErrorR replay keeps offset windows self-contained" {
    var storage = [_]u8{0xaa} ** 20;

    const known_view = storage[4..10];
    const known = str_error_r.strErrorR(0, known_view);
    try std.testing.expectEqualStrings("Succe", known);
    try std.testing.expectEqual(@as(u8, 0), known_view[5]);
    for (storage[0..4]) |byte| {
        try std.testing.expectEqual(@as(u8, 0xaa), byte);
    }
    for (storage[10..]) |byte| {
        try std.testing.expectEqual(@as(u8, 0xaa), byte);
    }

    const tiny_view = storage[11..12];
    const tiny = str_error_r.strErrorR(13, tiny_view);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, 0), tiny_view[0]);

    const unknown_view = storage[12..17];
    const unknown = str_error_r.strErrorR(4096, unknown_view);
    var rendered: [96]u8 = undefined;
    const full = try std.fmt.bufPrint(
        &rendered,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 4096, unknown_view.len },
    );
    try std.testing.expectEqualStrings(full[0 .. unknown_view.len - 1], unknown);
    try std.testing.expectEqual(@as(u8, 0), unknown_view[unknown_view.len - 1]);
    try std.testing.expectEqual(@as(u8, 0xaa), storage[17]);
    try std.testing.expectEqual(@as(u8, 0xaa), storage[18]);
    try std.testing.expectEqual(@as(u8, 0xaa), storage[19]);
}

test "lane10 vsprintf replay resets padded and offset views cleanly" {
    var storage = [_]u8{'#'} ** 16;
    const view = storage[3..11];

    const padded = vsprintf.scnprintfPad(view, view.len - 1, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 6), padded);
    try std.testing.expectEqualStrings("ok     ", view[0 .. view.len - 1]);
    try std.testing.expectEqual(@as(u8, 0), view[view.len - 1]);

    const tail = view[1..6];
    const written = vsprintf.scnprintf(tail, "{d}", .{7});
    try std.testing.expectEqual(@as(usize, 1), written);
    try std.testing.expectEqualStrings("7", tail[0..written]);
    try std.testing.expectEqual(@as(u8, 0), tail[written]);
    try std.testing.expectEqual(@as(u8, 'o'), view[0]);
    try std.testing.expectEqual(@as(u8, '#'), storage[2]);
    try std.testing.expectEqual(@as(u8, '#'), storage[11]);

    const reset = vsprintf.scnprintfPad(view, 0, "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), reset);
    try std.testing.expectEqual(@as(u8, 0), view[0]);
}

test "lane10 zalloc replay re-zeroes bytes and values after reset" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        a: u16,
        b: [3]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(bytes.?, 0x7f);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expectEqual(@as(u16, 0), value.?.a);
    try std.testing.expectEqual(std.mem.zeroes([3]u8), value.?.b);

    value.?.a = 9;
    value.?.b = .{ 1, 2, 3 };
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), value.?.a);
    try std.testing.expectEqual(std.mem.zeroes([3]u8), value.?.b);
}
