const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab empty and failed paths preserve live allocation count" {
    slab.kmalloc_nr_allocated = 0;

    var live: ?[]u8 = slab.kmallocArray(0, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(live);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(live);
    live = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR empty and tiny caller windows keep neighbors untouched" {
    var known_storage = [_]u8{0xaa} ** 5;
    const known = str_error_r.strErrorR(2, known_storage[2..2]);
    try std.testing.expectEqual(@as(usize, 0), known.len);
    try std.testing.expectEqual(@as(u8, 0xaa), known_storage[1]);
    try std.testing.expectEqual(@as(u8, 0xaa), known_storage[2]);
    try std.testing.expectEqual(@as(u8, 0xaa), known_storage[3]);

    var generated_storage = [_]u8{0xbb} ** 5;
    const generated = str_error_r.strErrorR(4096, generated_storage[2..3]);
    try std.testing.expectEqual(@as(usize, 0), generated.len);
    try std.testing.expectEqual(@as(u8, 0xbb), generated_storage[1]);
    try std.testing.expectEqual(@as(u8, 0), generated_storage[2]);
    try std.testing.expectEqual(@as(u8, 0xbb), generated_storage[3]);
}

test "vsprintf empty logical windows clear only the active caller byte" {
    var single_byte = [_]u8{0xcc} ** 5;
    const written = vsprintf.scnprintf(single_byte[2..3], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqual(@as(u8, 0xcc), single_byte[1]);
    try std.testing.expectEqual(@as(u8, 0), single_byte[2]);
    try std.testing.expectEqual(@as(u8, 0xcc), single_byte[3]);

    var padded = [_]u8{0xdd} ** 6;
    const padded_written = vsprintf.scnprintfPad(padded[1..5], 0, "{d}", .{7});
    try std.testing.expectEqual(@as(usize, 0), padded_written);
    try std.testing.expectEqual(@as(u8, 0), padded[1]);
    try std.testing.expectEqual(@as(u8, 0xdd), padded[2]);
    try std.testing.expectEqual(@as(u8, 0xdd), padded[3]);
    try std.testing.expectEqual(@as(u8, 0xdd), padded[4]);
}

test "zalloc zero-sized bytes and repeated frees settle to null" {
    const allocator = std.testing.allocator;
    const Value = extern struct {
        a: u16,
        b: u8,
        c: u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = null;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u16, 0), value.?.a);
    try std.testing.expectEqual(@as(u8, 0), value.?.b);
    try std.testing.expectEqual(@as(u8, 0), value.?.c);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
