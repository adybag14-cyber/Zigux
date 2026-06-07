const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const testing = std.testing;

fn expectPaddedWrite(written: usize, expected_current: usize, expected_legacy: usize) !void {
    try testing.expect(written == expected_current or written == expected_legacy);
}

test "bounce matrix keeps slab rows and zalloc summaries independent" {
    const allocator = testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var matrix = slab.kmallocBytes(72, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer {
        slab.kfree(matrix);
        slab.kmalloc_nr_allocated = 0;
    }
    try testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const row0 = matrix[0..24];
    const row1 = matrix[24..48];
    const row2 = matrix[48..72];

    @memset(row0, 0xa1);
    const known = str_error_r.strErrorR(22, row0[1..19]);
    try testing.expectEqualStrings("Invalid argument", known);
    try testing.expectEqual(@as(u8, 0xa1), row0[0]);
    try testing.expectEqual(@as(u8, 0), row0[17]);
    try testing.expectEqual(@as(u8, 0xa1), row0[18]);
    try testing.expectEqual(@as(u8, 0xa1), row0[19]);

    @memset(row1, 0xb2);
    const fallback = str_error_r.strErrorR(6006, row1[2..22]);
    try testing.expectEqualStrings("INTERNAL ERROR: str", fallback);
    try testing.expectEqual(@as(u8, 0xb2), row1[0]);
    try testing.expectEqual(@as(u8, 0xb2), row1[1]);
    try testing.expectEqual(@as(u8, 0), row1[21]);
    try testing.expectEqual(@as(u8, 0xb2), row1[22]);

    @memset(row2, 0xc3);
    const padded = vsprintf.scnprintfPad(row2[3..18], 12, "k={d}", .{known.len});
    try expectPaddedWrite(padded, 12, 11);
    try testing.expectEqual(@as(u8, 0xc3), row2[2]);
    try testing.expectEqualStrings("k=16        ", row2[3..15]);
    try testing.expectEqual(@as(u8, 0), row2[15]);
    try testing.expectEqual(@as(u8, 0xc3), row2[18]);

    var summary: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &summary);
    const summary_slice = summary.?;
    for (summary_slice) |value| {
        try testing.expectEqual(@as(u8, 0), value);
    }

    const written = vsprintf.scnprintf(summary_slice, "rows:{d}/{d}/{d}", .{ known.len, fallback.len, padded });
    try testing.expect(written == 12 or written == 13);
    try testing.expect(std.mem.startsWith(u8, summary_slice[0..written], "rows:16/19/"));

    zalloc.zfreeBytes(allocator, &summary);
    try testing.expect(summary == null);
    try testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "failed slab bounce preserves zalloc value owner and caller bytes" {
    const allocator = testing.allocator;
    const BounceState = struct {
        known_len: usize,
        fallback_len: usize,
        formatted_len: usize,
    };

    slab.kmalloc_nr_allocated = 0;
    var state: ?*BounceState = try zalloc.zallocValue(allocator, BounceState);
    defer zalloc.zfreeValue(allocator, BounceState, &state);
    try testing.expectEqual(@as(usize, 0), state.?.known_len);
    try testing.expectEqual(@as(usize, 0), state.?.fallback_len);
    try testing.expectEqual(@as(usize, 0), state.?.formatted_len);

    try testing.expect(slab.kmallocBytes(16, 0) == null);
    try testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var caller = [_]u8{ 0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8 };
    const known = str_error_r.strErrorR(0, caller[1..9]);
    try testing.expectEqualStrings("Success", known);
    try testing.expectEqual(@as(u8, 0xd0), caller[0]);
    try testing.expectEqual(@as(u8, 0), caller[8]);
    state.?.known_len = known.len;

    var fallback = [_]u8{ 0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea };
    const fallback_text = str_error_r.strErrorR(9009, fallback[2..10]);
    try testing.expectEqualStrings("INTERNA", fallback_text);
    try testing.expectEqual(@as(u8, 0xe0), fallback[0]);
    try testing.expectEqual(@as(u8, 0xe1), fallback[1]);
    try testing.expectEqual(@as(u8, 0), fallback[9]);
    state.?.fallback_len = fallback_text.len;

    var formatted = [_]u8{ 0xf0, 0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8 };
    state.?.formatted_len = vsprintf.vscnprintf(formatted[1..8], "{d}:{d}", .{ state.?.known_len, state.?.fallback_len });
    try testing.expectEqual(@as(usize, 3), state.?.formatted_len);
    try testing.expectEqual(@as(u8, 0xf0), formatted[0]);
    try testing.expectEqualStrings("7:7", formatted[1..4]);
    try testing.expectEqual(@as(u8, 0), formatted[4]);
    try testing.expectEqual(@as(u8, 0xf8), formatted[8]);

    zalloc.zfreeValue(allocator, BounceState, &state);
    try testing.expect(state == null);
    try testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
