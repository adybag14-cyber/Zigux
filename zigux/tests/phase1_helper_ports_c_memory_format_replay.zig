const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 slab allocation flags stay explicit across zeroed and plain arrays" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocArray(3, 4, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const plain = slab.kmallocArray(3, 4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(plain, 0x5a);

    const zeroed = slab.kmallocArray(3, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{0} ** 12, zeroed);
    try std.testing.expect(slab.slabIsAvailable());
}

test "lane10 formatting helpers preserve terminators through truncation and padding" {
    var formatted: [8]u8 = @splat(0xaa);
    const written = vsprintf.scnprintf(&formatted, "err={d}", .{4096});
    try std.testing.expectEqual(@as(usize, 7), written);
    try std.testing.expectEqualStrings("err=409", formatted[0..written]);
    try std.testing.expectEqual(@as(u8, 0), formatted[written]);

    var known_error: [8]u8 = @splat(0xbb);
    const known = str_error_r.strErrorR(13, &known_error);
    try std.testing.expectEqualStrings("Permiss", known);
    try std.testing.expectEqual(@as(u8, 0), known_error[known.len]);

    var padded: [10]u8 = @splat(0xcc);
    const padded_len = vsprintf.scnprintfPad(&padded, 6, "{s}", .{known[0..4]});
    try std.testing.expectEqual(@as(usize, 5), padded_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'P', 'e', 'r', 'm', ' ', ' ', 0, 0xcc, 0xcc, 0xcc }, &padded);
}

test "lane10 zalloc buffers can carry rendered fallback errors and free idempotently" {
    const allocator = std.testing.allocator;

    var error_buffer: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    defer zalloc.zfreeBytes(allocator, &error_buffer);
    try std.testing.expectEqualSlices(u8, &[_]u8{0} ** 16, error_buffer.?);

    const fallback = str_error_r.strErrorR(4096, error_buffer.?);
    try std.testing.expectEqualStrings("INTERNAL ERROR:", fallback);
    try std.testing.expectEqual(@as(u8, 0), error_buffer.?[fallback.len]);

    var rendered: ?[]u8 = try zalloc.zallocBytes(allocator, 10);
    defer zalloc.zfreeBytes(allocator, &rendered);
    const written = vsprintf.vscnprintf(rendered.?, "{s}", .{fallback});
    try std.testing.expectEqual(@as(usize, 9), written);
    try std.testing.expectEqualStrings("INTERNAL ", rendered.?[0..written]);
    try std.testing.expectEqual(@as(u8, 0), rendered.?[written]);

    zalloc.zfreeBytes(allocator, &rendered);
    try std.testing.expect(rendered == null);
    zalloc.zfreeBytes(allocator, &rendered);
    try std.testing.expect(rendered == null);
}

test "lane10 zalloc value zeroing survives formatted status updates" {
    const allocator = std.testing.allocator;
    const Status = struct {
        count: usize,
        failed: bool,
        scratch: [12]u8,
    };

    var status: ?*Status = try zalloc.zallocValue(allocator, Status);
    defer zalloc.zfreeValue(allocator, Status, &status);
    try std.testing.expectEqual(@as(usize, 0), status.?.count);
    try std.testing.expectEqual(false, status.?.failed);
    try std.testing.expectEqualSlices(u8, &[_]u8{0} ** 12, &status.?.scratch);

    status.?.count = vsprintf.scnprintf(&status.?.scratch, "ok:{s}", .{"slab"});
    try std.testing.expectEqual(@as(usize, 7), status.?.count);
    try std.testing.expectEqualStrings("ok:slab", status.?.scratch[0..status.?.count]);

    zalloc.zfreeValue(allocator, Status, &status);
    try std.testing.expect(status == null);
}
