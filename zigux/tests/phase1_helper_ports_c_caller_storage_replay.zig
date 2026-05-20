const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab-backed caller storage can move from strerror to padded formatting and back to zeroed state" {
    slab.kmalloc_nr_allocated = 0;

    const storage = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (storage) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const message = str_error_r.strErrorR(2, storage);
    try std.testing.expectEqualStrings("No such file or directory", message);
    try std.testing.expectEqual(@as(u8, 0), storage[message.len]);

    const written = vsprintf.scnprintfPad(storage, 8, "id={d}", .{7});
    try std.testing.expectEqual(@as(usize, 7), written);
    try std.testing.expectEqualStrings("id=7    ", storage[0..8]);
    try std.testing.expectEqual(@as(u8, 0), storage[8]);

    @memset(storage, 0xaa);
    slab.kfree(storage);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const fresh = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(fresh);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (fresh) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "strErrorR reuses borrowed caller views cleanly after a tiny diagnostic render" {
    var storage: [48]u8 = undefined;
    @memset(&storage, 0xaa);

    const tiny = str_error_r.strErrorR(4096, storage[0..8]);
    try std.testing.expectEqualStrings("INTERNA", tiny);
    try std.testing.expectEqual(@as(u8, 0), storage[7]);

    const recovered = str_error_r.strErrorR(13, storage[0..32]);
    try std.testing.expectEqualStrings("Permission denied", recovered);
    try std.testing.expectEqual(@as(u8, 0), storage[recovered.len]);
}

test "vsprintf keeps padded and non-padded caller reuse aligned" {
    var buffer: [10]u8 = undefined;

    const full = vsprintf.vscnprintf(&buffer, "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 6), full);
    try std.testing.expectEqualStrings("abcdef", buffer[0..full]);
    try std.testing.expectEqual(@as(u8, 0), buffer[full]);

    const padded = vsprintf.scnprintfPad(&buffer, 5, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 4), padded);
    try std.testing.expectEqualStrings("xy   ", buffer[0..5]);
    try std.testing.expectEqual(@as(u8, 0), buffer[5]);

    const short = vsprintf.scnprintf(&buffer, "{d}", .{9});
    try std.testing.expectEqual(@as(usize, 1), short);
    try std.testing.expectEqualStrings("9", buffer[0..short]);
    try std.testing.expectEqual(@as(u8, 0), buffer[short]);
}

test "zalloc restores caller-owned bytes and values after dirty frees" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u32,
        ready: bool,
        bytes: [3]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0x5a);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expect(value != null);
    value.?.count = 99;
    value.?.ready = true;
    @memset(&value.?.bytes, 0xff);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.ready);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);
}
