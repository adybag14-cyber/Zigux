const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 growth replay keeps slab and strerror growth state honest" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const grown = slab.kmallocArray(3, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(grown);
    try std.testing.expectEqual(@as(usize, 6), grown.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (grown) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var known_buffer = [_]u8{0xaa} ** 8;
    const known_tiny = str_error_r.strErrorR(0, known_buffer[0..1]);
    try std.testing.expectEqual(@as(usize, 0), known_tiny.len);
    try std.testing.expectEqual(@as(u8, 0), known_buffer[0]);

    const known_full = str_error_r.strErrorR(0, known_buffer[0..]);
    try std.testing.expectEqualStrings("Success", known_full);
    try std.testing.expectEqual(@as(u8, 0), known_buffer[known_full.len]);
    try std.testing.expectEqual(@intFromPtr(&known_buffer[0]), @intFromPtr(known_full.ptr));

    var unknown_buffer = [_]u8{0xbb} ** 48;
    const unknown_tiny = str_error_r.strErrorR(4096, unknown_buffer[0..1]);
    try std.testing.expectEqual(@as(usize, 0), unknown_tiny.len);
    try std.testing.expectEqual(@as(u8, 0), unknown_buffer[0]);

    const unknown_full = str_error_r.strErrorR(4096, unknown_buffer[0..]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 48)=22", unknown_full);
    try std.testing.expectEqual(@as(u8, 0), unknown_buffer[unknown_full.len]);
    try std.testing.expectEqual(@intFromPtr(&unknown_buffer[0]), @intFromPtr(unknown_full.ptr));
}

test "lane10 growth replay keeps vsprintf growth and padding routes aligned" {
    var shared = [_]u8{0xcc} ** 12;

    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(shared[0..1], "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, 0), shared[0]);

    const grown = vsprintf.scnprintf(shared[0..], "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(@as(usize, 7), grown);
    try std.testing.expectEqualStrings("zigux:7", shared[0..grown]);
    try std.testing.expectEqual(@as(u8, 0), shared[grown]);

    shared = [_]u8{0xdd} ** 12;
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(shared[0..1], "{s}:{d}", .{ "zigux", 7 }));
    try std.testing.expectEqual(@as(u8, 0), shared[0]);

    const parity = vsprintf.vscnprintf(shared[0..], "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(grown, parity);
    try std.testing.expectEqualStrings("zigux:7", shared[0..parity]);
    try std.testing.expectEqual(@as(u8, 0), shared[parity]);

    shared = [_]u8{0xee} ** 12;
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintfPad(shared[0..1], 6, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, 0), shared[0]);

    const padded = vsprintf.scnprintfPad(shared[0..], 10, "id={d}", .{7});
    try std.testing.expectEqual(@as(usize, 9), padded);
    try std.testing.expectEqualStrings("id=7      ", shared[0..10]);
    try std.testing.expectEqual(@as(u8, 0), shared[10]);
}

test "lane10 growth replay keeps zalloc fresh-state contracts after dirty frees" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 6), bytes.?.len);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const ReplayValue = struct {
        active: bool,
        tag: u8,
        maybe_ptr: ?*const u8,
        maybe_text: ?[]const u8,
        nested: struct {
            count: ?usize,
            enabled: bool,
        },
    };

    var sentinel: u8 = 0xaa;
    var value: ?*ReplayValue = try zalloc.zallocValue(allocator, ReplayValue);
    try std.testing.expect(value != null);
    value.?.active = true;
    value.?.tag = 7;
    value.?.maybe_ptr = &sentinel;
    value.?.maybe_text = "zigux";
    value.?.nested.count = 9;
    value.?.nested.enabled = true;
    zalloc.zfreeValue(allocator, ReplayValue, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, ReplayValue);
    defer zalloc.zfreeValue(allocator, ReplayValue, &value);
    try std.testing.expect(value != null);
    try std.testing.expect(!value.?.active);
    try std.testing.expectEqual(@as(u8, 0), value.?.tag);
    try std.testing.expect(value.?.maybe_ptr == null);
    try std.testing.expect(value.?.maybe_text == null);
    try std.testing.expect(value.?.nested.count == null);
    try std.testing.expect(!value.?.nested.enabled);
}
