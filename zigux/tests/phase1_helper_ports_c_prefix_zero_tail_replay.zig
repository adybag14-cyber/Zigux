const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectZeroes(bytes: []const u8) !void {
    for (bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "slab error prefix feeds zalloc-owned zero tail summary" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const scratch = slab.kmallocBytes(24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(scratch);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroes(scratch);

    var summary: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &summary);
    try expectZeroes(summary.?);

    const rendered = str_error_r.strErrorR(12, scratch[2..18]);
    try std.testing.expectEqualStrings("Cannot allocate", rendered);
    try expectZeroes(scratch[0..2]);
    try std.testing.expectEqual(@as(u8, 0), scratch[17]);
    try expectZeroes(scratch[18..24]);

    const written = vsprintf.scnprintf(summary.?[3..13], "err:{d}", .{rendered.len});
    try std.testing.expectEqual(@as(usize, 6), written);
    try expectZeroes(summary.?[0..3]);
    try std.testing.expectEqualStrings("err:15", summary.?[3 .. 3 + written]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[3 + written]);
    try expectZeroes(summary.?[3 + written + 1 ..]);

    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "padded slab window and fallback prefix survive zalloc value handoff" {
    const allocator = std.testing.allocator;
    const Record = struct {
        padded_len: usize,
        fallback_len: usize,
        bytes: [8]u8,
    };

    slab.kmalloc_nr_allocated = 0;
    const window = slab.kmallocArray(4, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(window);
    try std.testing.expectEqual(@as(usize, 32), window.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroes(window);

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expectEqual(@as(usize, 0), record.?.padded_len);
    try std.testing.expectEqual(@as(usize, 0), record.?.fallback_len);
    try expectZeroes(record.?.bytes[0..]);

    const padded = vsprintf.scnprintfPad(window[4..14], 8, "{s}", .{"zx"});
    try std.testing.expect(padded == 7 or padded == 8);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'x', ' ', ' ', ' ', ' ', ' ', ' ', 0, 0 }, window[4..14]);

    record.?.padded_len = padded;
    @memcpy(record.?.bytes[0..], window[4..12]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'x', ' ', ' ', ' ', ' ', ' ', ' ' }, record.?.bytes[0..]);

    const fallback = str_error_r.strErrorR(4097, window[16..23]);
    try std.testing.expectEqualStrings("INTERN", fallback);
    try std.testing.expectEqual(@as(u8, 0), window[22]);
    try std.testing.expectEqual(@as(u8, 0), window[23]);
    record.?.fallback_len = fallback.len;

    const note = vsprintf.vscnprintf(window[24..30], "p{d}f{d}", .{ record.?.padded_len, record.?.fallback_len });
    try std.testing.expect(note == 4);
    try std.testing.expectEqualSlices(u8, "p", window[24..25]);
    try std.testing.expect(window[25] == '7' or window[25] == '8');
    try std.testing.expectEqualSlices(u8, "f6", window[26..28]);
    try std.testing.expectEqual(@as(u8, 0), window[28]);
    try expectZeroes(window[29..32]);

    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
