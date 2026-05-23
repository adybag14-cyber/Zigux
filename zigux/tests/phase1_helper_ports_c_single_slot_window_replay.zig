const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab balances mixed zero-length and single-byte allocations" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocArray(4, 0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const single = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), single.len);
    try std.testing.expectEqual(@as(u8, 0), single[0]);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(single);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR uses terminator-only interior slices without touching neighbors" {
    var known = [_]u8{ 'K', 'K', 'K', 'K', 'K' };
    const known_text = str_error_r.strErrorR(2, known[2..3]);
    try std.testing.expectEqual(@as(usize, 0), known_text.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'K', 'K', 0, 'K', 'K' }, &known);

    var unknown = [_]u8{ 'U', 'U', 'U', 'U' };
    const unknown_text = str_error_r.strErrorR(4096, unknown[1..2]);
    try std.testing.expectEqual(@as(usize, 0), unknown_text.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'U', 0, 'U', 'U' }, &unknown);
}

test "vsprintf handles one-byte caller windows and one-character logical limits" {
    var terminator_only = [_]u8{ '!', '!', '!', '!', '!' };
    const empty_written = vsprintf.vscnprintf(terminator_only[2..3], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', 0, '!', '!' }, &terminator_only);

    var single_slot = [_]u8{ '?', '?', '?', '?', '?', '?' };
    const one_written = vsprintf.scnprintfPad(single_slot[1..4], 1, "{s}", .{"beta"});
    try std.testing.expectEqual(@as(usize, 1), one_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '?', 'b', 0, '?', '?', '?' }, &single_slot);
}

test "zalloc re-zeroes single-byte buffers and single-field values" {
    const allocator = std.testing.allocator;
    const Flag = struct {
        ready: bool,
    };

    var first_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expectEqual(@as(usize, 1), first_bytes.?.len);
    try std.testing.expectEqual(@as(u8, 0), first_bytes.?[0]);
    first_bytes.?[0] = 0x7f;
    zalloc.zfreeBytes(allocator, &first_bytes);
    try std.testing.expect(first_bytes == null);

    var second_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &second_bytes);
    try std.testing.expectEqual(@as(u8, 0), second_bytes.?[0]);

    var first_flag: ?*Flag = try zalloc.zallocValue(allocator, Flag);
    try std.testing.expectEqual(false, first_flag.?.ready);
    first_flag.?.ready = true;
    zalloc.zfreeValue(allocator, Flag, &first_flag);
    try std.testing.expect(first_flag == null);

    var second_flag: ?*Flag = try zalloc.zallocValue(allocator, Flag);
    defer zalloc.zfreeValue(allocator, Flag, &second_flag);
    try std.testing.expectEqual(false, second_flag.?.ready);
}
