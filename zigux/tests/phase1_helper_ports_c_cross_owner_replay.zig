const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectPaddedReturn(actual: usize, logical: usize) !void {
    try std.testing.expect(actual == logical or actual == logical -| 1);
}

test "slab error window can be summarized through zalloc and rewritten in place" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    var slab_window = slab.kmallocBytes(48, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_window);
    @memset(slab_window, 0x5a);

    const error_view = slab_window[4..36];
    const rendered = str_error_r.strErrorR(31337, error_view);
    try std.testing.expectEqual(@as(usize, 31), rendered.len);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(3133", rendered);
    try std.testing.expectEqual(@as(u8, 0x5a), slab_window[3]);
    try std.testing.expectEqual(@as(u8, 0), slab_window[35]);
    try std.testing.expectEqual(@as(u8, 0x5a), slab_window[36]);

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 64);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    const summary = summary_owner.?;
    const summary_len = vsprintf.scnprintf(summary, "err[{d}]={s}", .{ rendered.len, rendered });
    try std.testing.expectEqual(@as(usize, 39), summary_len);
    try std.testing.expectEqualStrings("err[31]=INTERNAL ERROR: strerror_r(3133", summary[0..summary_len]);
    try std.testing.expectEqual(@as(u8, 0), summary[summary_len]);

    const rewrite_len = vsprintf.scnprintfPad(error_view, 18, "sum:{d}", .{summary_len});
    try expectPaddedReturn(rewrite_len, 18);
    try std.testing.expectEqualStrings("sum:39            ", error_view[0..18]);
    try std.testing.expectEqual(@as(u8, 0), error_view[18]);
    try std.testing.expectEqual(@as(u8, 0x5a), slab_window[3]);
    try std.testing.expectEqual(@as(u8, 0x5a), slab_window[36]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "failed slab handoff preserves zalloc owners and final slab accounting" {
    const allocator = std.testing.allocator;
    const OwnerState = struct {
        code: u32,
        seen: bool,
        count: usize,
    };

    slab.kmalloc_nr_allocated = 0;

    var zbytes_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &zbytes_owner);
    const zbytes = zbytes_owner.?;
    const known = str_error_r.strErrorR(22, zbytes[3..22]);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0), zbytes[19]);
    try std.testing.expectEqual(@as(u8, 0), zbytes[0]);
    try std.testing.expectEqual(@as(u8, 0), zbytes[22]);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL | slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualStrings("Invalid argument", zbytes[3 .. 3 + known.len]);

    var state_owner: ?*OwnerState = try zalloc.zallocValue(allocator, OwnerState);
    defer zalloc.zfreeValue(allocator, OwnerState, &state_owner);
    try std.testing.expectEqual(@as(u32, 0), state_owner.?.code);
    try std.testing.expectEqual(false, state_owner.?.seen);
    try std.testing.expectEqual(@as(usize, 0), state_owner.?.count);

    const slab_array = slab.kmallocArray(2, 16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const padded = vsprintf.scnprintfPad(slab_array[1..15], 12, "{s}:{d}", .{ known, known.len });
    try expectPaddedReturn(padded, 12);
    try std.testing.expectEqualStrings("Invalid argu", slab_array[1..13]);
    try std.testing.expectEqual(@as(u8, 0), slab_array[13]);
    try std.testing.expectEqual(@as(u8, 0), slab_array[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_array[15]);

    zalloc.zfreeBytes(allocator, &zbytes_owner);
    zalloc.zfreeBytes(allocator, &zbytes_owner);
    try std.testing.expect(zbytes_owner == null);
    zalloc.zfreeValue(allocator, OwnerState, &state_owner);
    zalloc.zfreeValue(allocator, OwnerState, &state_owner);
    try std.testing.expect(state_owner == null);
}
