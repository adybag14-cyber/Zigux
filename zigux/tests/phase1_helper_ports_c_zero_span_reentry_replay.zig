const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-span allocations keep counters balanced across reentry" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zero_array = slab.kmallocArray(0, 7, slab.GFP_KERNEL) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps one-slot and narrow fallback views fenced" {
    var single = [_]u8{ '!', '!', '!' };
    const empty_known = str_error_r.strErrorR(0, single[1..2]);
    try std.testing.expectEqual(@as(usize, 0), empty_known.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', 0, '!' }, &single);

    var fallback = [_]u8{ '@', '@', '@', '@', '@' };
    const rendered = str_error_r.strErrorR(4096, fallback[1..4]);
    try std.testing.expectEqualStrings("IN", rendered);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '@', 'I', 'N', 0, '@' }, &fallback);
}

test "vsprintf reuses zero-span and padded subviews without leaking past interior windows" {
    var backing = [_]u8{ '?', '?', '?', '?', '?', '?', '?', '?', '?' };
    const window = backing[1..7];

    const clipped = vsprintf.scnprintfPad(window, 2, "{s}", .{"wide"});
    try std.testing.expectEqual(@as(usize, 2), clipped);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ '?', 'w', 'i', 0, '?', '?', '?', '?', '?' },
        &backing,
    );

    const padded = vsprintf.scnprintfPad(window[1..], 4, "{s}", .{"q"});
    try std.testing.expectEqual(@as(usize, 3), padded);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ '?', 'w', 'q', ' ', ' ', ' ', 0, '?', '?' },
        &backing,
    );
}

test "zalloc zero-span bytes and typed values restart from zeroed ownership" {
    const allocator = std.testing.allocator;
    const State = extern struct {
        count: u8,
        armed: bool,
    };

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, bytes.?);
    bytes.?[0] = 0x7f;

    var state: ?*State = try zalloc.zallocValue(allocator, State);
    try std.testing.expectEqual(@as(u8, 0), state.?.count);
    try std.testing.expectEqual(false, state.?.armed);
    state.?.count = 9;
    state.?.armed = true;
    zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expect(state == null);

    state = try zalloc.zallocValue(allocator, State);
    defer zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expectEqual(@as(u8, 0), state.?.count);
    try std.testing.expectEqual(false, state.?.armed);
}
