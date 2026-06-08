const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports c owner wave replay" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    var slab_owner: ?[]u8 = slab.kmallocArray(4, 32, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer slab.kfree(slab_owner);

    const block = slab_owner orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 128), block.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (block) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    @memset(block, 0xaa);

    const known_window = block[2..25];
    const known = str_error_r.strErrorR(12, known_window);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqual(@as(u8, 0xaa), block[1]);
    try std.testing.expectEqual(@as(u8, 0), block[24]);
    try std.testing.expectEqual(@as(u8, 0xaa), block[25]);

    const fallback_window = block[32..64];
    const fallback = str_error_r.strErrorR(31337, fallback_window);
    try std.testing.expectEqual(@as(usize, 31), fallback.len);
    try std.testing.expect(std.mem.startsWith(u8, fallback, "INTERNAL ERROR: strerror_r"));
    try std.testing.expectEqual(@as(u8, 0), block[63]);
    try std.testing.expectEqual(@as(u8, 0xaa), block[64]);

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    for (summary_owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const summary = summary_owner.?;
    const summary_written = vsprintf.scnprintf(summary, "known={d};fallback={d}", .{ known.len, fallback.len });
    try std.testing.expectEqualStrings("known=22;fallback=31", summary[0..summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary[summary_written]);

    const pad_window = block[67..79];
    const pad_written = vsprintf.scnprintfPad(pad_window, 9, "{s}", .{"ow"});
    try std.testing.expect(pad_written == 8 or pad_written == 9);
    try std.testing.expectEqual(@as(u8, 0xaa), block[66]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'w', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0 }, pad_window[0..10]);
    try std.testing.expectEqual(@as(u8, 0xaa), pad_window[10]);
    try std.testing.expectEqual(@as(u8, 0xaa), pad_window[11]);
    try std.testing.expectEqual(@as(u8, 0xaa), block[79]);

    const OwnerState = struct {
        known_len: usize,
        fallback_len: usize,
        padded_len: usize,
        allocation_count: isize,
        touched: bool,
    };
    var state_owner: ?*OwnerState = try zalloc.zallocValue(allocator, OwnerState);
    defer zalloc.zfreeValue(allocator, OwnerState, &state_owner);

    try std.testing.expectEqual(@as(usize, 0), state_owner.?.known_len);
    try std.testing.expectEqual(false, state_owner.?.touched);
    state_owner.?.* = .{
        .known_len = known.len,
        .fallback_len = fallback.len,
        .padded_len = pad_written,
        .allocation_count = slab.kmalloc_nr_allocated,
        .touched = true,
    };
    try std.testing.expectEqual(@as(usize, 22), state_owner.?.known_len);
    try std.testing.expectEqual(@as(usize, 31), state_owner.?.fallback_len);
    try std.testing.expect(state_owner.?.padded_len == 8 or state_owner.?.padded_len == 9);
    try std.testing.expectEqual(@as(isize, 1), state_owner.?.allocation_count);

    const direct_window = block[100..116];
    const direct_written = vsprintf.scnprintf(direct_window, "cnt={d};ok={}", .{ slab.kmalloc_nr_allocated, state_owner.?.touched });
    try std.testing.expectEqualStrings("cnt=1;ok=true", direct_window[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), direct_window[direct_written]);
    try std.testing.expectEqual(@as(u8, 0xaa), block[99]);
    try std.testing.expectEqual(@as(u8, 0xaa), block[116]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL | slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);
    zalloc.zfreeValue(allocator, OwnerState, &state_owner);
    try std.testing.expect(state_owner == null);

    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
