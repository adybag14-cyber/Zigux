const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab-backed split views isolate strErrorR writes" {
    slab.kmalloc_nr_allocated = 0;

    const backing = slab.kmallocBytes(96, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    defer slab.kfree(backing);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const left = backing[4..24];
    const right = backing[40..88];

    try std.testing.expectEqualStrings("Permission denied", str_error_r.strErrorR(13, left));
    try std.testing.expectEqualStrings(
        "INTERNAL ERROR: strerror_r(4096, [buf], 48)=22",
        str_error_r.strErrorR(4096, right),
    );

    for (backing[0..4]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    for (backing[24..40]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    for (backing[88..]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "vsprintf reuses offset caller slices without disturbing neighbors" {
    var backing = [_]u8{'#'} ** 24;
    const view = backing[5..15];

    const first = vsprintf.scnprintf(view, "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 6), first);
    try std.testing.expectEqualStrings("abcdef", view[0..first]);
    try std.testing.expectEqual(@as(u8, 0), view[first]);

    const second = vsprintf.vscnprintf(view, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 2), second);
    try std.testing.expectEqualStrings("xy", view[0..second]);
    try std.testing.expectEqual(@as(u8, 0), view[second]);

    for (backing[0..5]) |byte| {
        try std.testing.expectEqual(@as(u8, '#'), byte);
    }
    for (backing[15..]) |byte| {
        try std.testing.expectEqual(@as(u8, '#'), byte);
    }
}

test "zallocValue zeroes nested extern union storage after an earlier dirty free" {
    const allocator = std.testing.allocator;

    const Inner = extern union {
        word: u32,
        bytes: [4]u8,
    };

    const Outer = extern struct {
        tag: u8,
        inner: Inner,
        tail: u16,
    };

    var first: ?*Outer = try zalloc.zallocValue(allocator, Outer);
    defer zalloc.zfreeValue(allocator, Outer, &first);

    first.?.tag = 0x7f;
    first.?.inner.bytes = .{ 1, 2, 3, 4 };
    first.?.tail = 0xa5a5;

    zalloc.zfreeValue(allocator, Outer, &first);
    try std.testing.expect(first == null);

    var second: ?*Outer = try zalloc.zallocValue(allocator, Outer);
    defer zalloc.zfreeValue(allocator, Outer, &second);

    try std.testing.expect(second != null);
    for (std.mem.asBytes(second.?)) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "slab and zalloc mixed frees keep their local state balanced" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slab_bytes: ?[]u8 = slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    defer slab.kfree(slab_bytes);

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 8);
    defer zalloc.zfreeBytes(allocator, &zbytes);

    const Value = struct {
        count: u32,
        ready: bool,
    };

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(slab_bytes.?, 0x5a);
    @memset(zbytes.?, 0x6b);
    value.?.count = 99;
    value.?.ready = true;

    zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(slab_bytes);
    slab_bytes = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
