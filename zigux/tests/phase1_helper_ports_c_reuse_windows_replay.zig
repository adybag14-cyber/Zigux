const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-length arrays stay balanced while peer allocations churn" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocArray(0, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const peer = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        slab.kfree(empty);
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (peer) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(peer);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR can reuse one caller window from generated text to a shorter known message" {
    var backing = [_]u8{'%'} ** 64;
    const window = backing[3..43];

    const generated = str_error_r.strErrorR(4096, window);
    try std.testing.expect(std.mem.startsWith(u8, generated, "INTERNAL ERROR: strerror_r("));
    try std.testing.expectEqual(@as(u8, 0), window[generated.len]);

    const known = str_error_r.strErrorR(0, window);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0), window[known.len]);
    try std.testing.expectEqual(@as(u8, '%'), backing[2]);
    try std.testing.expectEqual(@as(u8, '%'), backing[43]);
}

test "vscnprintf can rewrite a shared caller window down to an empty string" {
    var backing = [_]u8{'?'} ** 12;
    const window = backing[2..8];

    const first = vsprintf.vscnprintf(window, "{s}", .{"abcde"});
    try std.testing.expectEqual(@as(usize, 5), first);
    try std.testing.expectEqualStrings("abcde", window[0..first]);
    try std.testing.expectEqual(@as(u8, 0), window[first]);

    const second = vsprintf.vscnprintf(window, "{s}", .{""});
    try std.testing.expectEqual(@as(usize, 0), second);
    try std.testing.expectEqual(@as(u8, 0), window[0]);
    try std.testing.expectEqual(@as(u8, 'b'), window[1]);
    try std.testing.expectEqual(@as(u8, '?'), backing[1]);
    try std.testing.expectEqual(@as(u8, '?'), backing[8]);
}

test "zalloc null-safe frees and reallocation keep reused storage zeroed" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = null;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const Payload = struct {
        count: u16,
        flag: bool,
        bytes: [2]u8,
    };

    var value: ?*Payload = null;
    zalloc.zfreeValue(allocator, Payload, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expect(value != null);
    value.?.count = 19;
    value.?.flag = true;
    value.?.bytes = .{ 0xbb, 0xcc };
    zalloc.zfreeValue(allocator, Payload, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &value);
    try std.testing.expect(value != null);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.flag);
    try std.testing.expectEqual(@as(u8, 0), value.?.bytes[0]);
    try std.testing.expectEqual(@as(u8, 0), value.?.bytes[1]);
}
