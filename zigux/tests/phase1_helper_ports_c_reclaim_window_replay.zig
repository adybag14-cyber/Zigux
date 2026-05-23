const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab reclaim-gated failures keep live allocation accounting stable" {
    slab.kmalloc_nr_allocated = 0;

    const live = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer {
        slab.kfree(live);
        slab.kmalloc_nr_allocated = 0;
    }

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(4, slab.__GFP_ZERO) == null);
    try std.testing.expect(slab.kmallocArray(2, 8, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (live) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "strErrorR renders the caller window length inside interior slices" {
    var backing = [_]u8{'#'} ** 56;
    const rendered = str_error_r.strErrorR(4096, backing[4..52]);

    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 48)=22", rendered);
    try std.testing.expectEqual(@as(u8, '#'), backing[3]);
    try std.testing.expectEqual(@as(u8, 0), backing[50]);
    try std.testing.expectEqual(@as(u8, '#'), backing[51]);
    try std.testing.expectEqual(@as(u8, '#'), backing[52]);
}

test "vsprintf reuses offset windows across padded and exact truncating writes" {
    var backing = [_]u8{'!'} ** 11;
    const padded = vsprintf.scnprintfPad(backing[2..9], 5, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 4), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', 0, '!' }, backing[2..9]);
    try std.testing.expectEqual(@as(u8, '!'), backing[1]);
    try std.testing.expectEqual(@as(u8, '!'), backing[9]);

    const rewritten = vsprintf.vscnprintf(backing[3..8], "{s}", .{"planet"});
    try std.testing.expectEqual(@as(usize, 4), rewritten);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'p', 'l', 'a', 'n', 0, '!', '!' }, backing[2..10]);
}

test "zalloc resets split byte and value optionals after dirty frees" {
    const allocator = std.testing.allocator;
    const State = struct {
        id: u16,
        ready: bool,
        tail: [3]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0x7c);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var state: ?*State = try zalloc.zallocValue(allocator, State);
    try std.testing.expect(state != null);
    state.?.* = .{ .id = 9, .ready = true, .tail = .{ 1, 2, 3 } };
    zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expect(state == null);

    state = try zalloc.zallocValue(allocator, State);
    defer zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expectEqual(@as(u16, 0), state.?.id);
    try std.testing.expectEqual(false, state.?.ready);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &state.?.tail);
}
