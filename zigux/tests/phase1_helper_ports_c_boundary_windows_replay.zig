const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab and zalloc boundary windows preserve sentinels across helper rewrites" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memset(slab_bytes, 0xa5);
    const left = slab_bytes[3..13];
    const left_written = vsprintf.scnprintfPad(left, 7, "{s}:{d}", .{ "slab", 9 });
    try std.testing.expectEqual(@as(usize, 6), left_written);
    try std.testing.expectEqualStrings("slab:9", left[0..6]);
    try std.testing.expectEqual(@as(u8, 0), left[7]);
    try std.testing.expectEqual(@as(u8, 0xa5), left[8]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_bytes[2]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_bytes[13]);

    const right = slab_bytes[17..24];
    const rendered = str_error_r.strErrorR(22, right);
    try std.testing.expectEqualStrings("Invali", rendered);
    try std.testing.expectEqual(@as(u8, 0), right[6]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_bytes[16]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_bytes[24]);

    var scratch: ?[]u8 = try zalloc.zallocBytes(allocator, 20);
    defer zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch != null);

    const zbytes = scratch.?;
    for (zbytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    @memset(zbytes, 0xcc);

    const middle = zbytes[4..15];
    const middle_written = vsprintf.vscnprintf(middle, "{s}:{d}", .{ rendered, left_written });
    try std.testing.expectEqual(@as(usize, 8), middle_written);
    try std.testing.expectEqualStrings("Invali:6", middle[0..middle_written]);
    try std.testing.expectEqual(@as(u8, 0), middle[middle_written]);
    try std.testing.expectEqual(@as(u8, 0xcc), zbytes[3]);
    try std.testing.expectEqual(@as(u8, 0xcc), zbytes[15]);

    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "failed slab allocation leaves formatted zalloc fallback windows stable" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var fallback: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &fallback);
    const bytes = fallback.?;
    @memset(bytes, 0x7e);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const errno_window = bytes[2..12];
    const message = str_error_r.strErrorR(12, errno_window);
    try std.testing.expectEqualStrings("Cannot al", message);
    try std.testing.expectEqual(@as(u8, 0), errno_window[9]);
    try std.testing.expectEqual(@as(u8, 0x7e), bytes[1]);
    try std.testing.expectEqual(@as(u8, 0x7e), bytes[12]);

    const summary_window = bytes[13..23];
    const summary_written = vsprintf.scnprintf(summary_window, "{s}:{d}", .{ message[0..6], slab.kmalloc_nr_allocated });
    try std.testing.expectEqual(@as(usize, 8), summary_written);
    try std.testing.expectEqualStrings("Cannot:0", summary_window[0..summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary_window[summary_written]);
    try std.testing.expectEqual(@as(u8, 0x7e), bytes[12]);
    try std.testing.expectEqual(@as(u8, 0x7e), bytes[23]);

    zalloc.zfreeBytes(allocator, &fallback);
    try std.testing.expect(fallback == null);
}
