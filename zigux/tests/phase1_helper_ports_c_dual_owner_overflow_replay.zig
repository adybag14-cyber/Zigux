const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectZeroed(bytes: []const u8) !void {
    for (bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

fn expectPadWritten(written: usize, old_count: usize, current_count: usize) !void {
    try std.testing.expect(written == old_count or written == current_count);
}

test "overflowed slab array leaves dual owner error windows stable" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    try expectZeroed(zbytes.?);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try expectZeroed(zbytes.?);

    const slab_window = slab.kmallocBytes(16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_window);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(slab_window);

    const error_view = zbytes.?[2..15];
    const rendered = str_error_r.strErrorR(7777, error_view);
    try std.testing.expectEqualStrings("INTERNAL ERR", rendered);
    try std.testing.expectEqual(@as(u8, 0), zbytes.?[0]);
    try std.testing.expectEqual(@as(u8, 0), zbytes.?[1]);
    try std.testing.expectEqual(@as(u8, 0), zbytes.?[14]);
    try expectZeroed(zbytes.?[15..]);

    const padded = vsprintf.scnprintfPad(slab_window[1..14], 11, "err={s}", .{rendered[0..3]});
    try expectPadWritten(padded, 10, 11);
    try std.testing.expectEqual(@as(u8, 0), slab_window[0]);
    try std.testing.expectEqualSlices(u8, "err=INT    ", slab_window[1..12]);
    try std.testing.expectEqual(@as(u8, 0), slab_window[12]);
    try expectZeroed(slab_window[13..]);

    zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes == null);
    zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc value drives bounded slab and byte owner formatting" {
    const allocator = std.testing.allocator;
    const Request = struct {
        errnum: i32,
        logical: usize,
    };

    slab.kmalloc_nr_allocated = 0;

    var request: ?*Request = try zalloc.zallocValue(allocator, Request);
    defer zalloc.zfreeValue(allocator, Request, &request);
    try std.testing.expectEqual(@as(i32, 0), request.?.errnum);
    try std.testing.expectEqual(@as(usize, 0), request.?.logical);

    request.?.errnum = 22;
    request.?.logical = 9;

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 14);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    const slab_window = slab.kmallocBytes(18, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_window);

    const known = str_error_r.strErrorR(request.?.errnum, slab_window[2..12]);
    try std.testing.expectEqualStrings("Invalid a", known);
    try expectZeroed(slab_window[0..2]);
    try std.testing.expectEqual(@as(u8, 0), slab_window[11]);
    try expectZeroed(slab_window[12..]);

    const direct = vsprintf.scnprintf(zbytes.?[1..10], "tag:{s}", .{known[0..3]});
    try std.testing.expectEqual(@as(usize, 7), direct);
    try std.testing.expectEqual(@as(u8, 0), zbytes.?[0]);
    try std.testing.expectEqualSlices(u8, "tag:Inv", zbytes.?[1..8]);
    try std.testing.expectEqual(@as(u8, 0), zbytes.?[8]);
    try expectZeroed(zbytes.?[9..]);

    try std.testing.expect(slab.kmallocBytes(8, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeValue(allocator, Request, &request);
    try std.testing.expect(request == null);
    zalloc.zfreeValue(allocator, Request, &request);
    try std.testing.expect(request == null);
}
