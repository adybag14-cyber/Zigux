const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab null frees do not perturb tiny live allocations" {
    slab.kmalloc_nr_allocated = 0;
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const live = slab.kmallocBytes(1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(live);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    live[0] = 0x5a;
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0x5a), live[0]);
}

test "strErrorR seeds one-byte and exact-fit caller windows with a terminator" {
    var single = [_]u8{0xaa};
    const single_known = str_error_r.strErrorR(0, &single);
    try std.testing.expectEqual(@as(usize, 0), single_known.len);
    try std.testing.expectEqual(@as(u8, 0), single[0]);

    single[0] = 0xbb;
    const single_fallback = str_error_r.strErrorR(4096, &single);
    try std.testing.expectEqual(@as(usize, 0), single_fallback.len);
    try std.testing.expectEqual(@as(u8, 0), single[0]);

    var exact = [_]u8{ 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc };
    const exact_rendered = str_error_r.strErrorR(0, &exact);
    try std.testing.expectEqualStrings("Success", exact_rendered);
    try std.testing.expectEqual(@as(u8, 0), exact[7]);
}

test "vsprintf zero-seeds tiny caller views without touching neighbors" {
    var backing = [_]u8{ 0x31, 0x32, 0x33 };
    const tiny_written = vsprintf.scnprintf(backing[1..2], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), tiny_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x31, 0x00, 0x33 }, &backing);

    backing = [_]u8{ 0x41, 0x42, 0x43 };
    const tiny_pad_written = vsprintf.scnprintfPad(backing[1..2], 1, "{d}", .{7});
    try std.testing.expectEqual(@as(usize, 0), tiny_pad_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x41, 0x00, 0x43 }, &backing);

    const empty_written = vsprintf.vscnprintf(backing[0..0], "{s}", .{"noop"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x41, 0x00, 0x43 }, &backing);
}

test "zalloc re-seeds bytes and values after null-safe release" {
    const allocator = std.testing.allocator;
    var bytes: ?[]u8 = null;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 1);
    bytes.?[0] = 0x7f;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[0]);

    const Seeded = struct {
        count: u8,
        enabled: bool,
    };

    var value: ?*Seeded = null;
    zalloc.zfreeValue(allocator, Seeded, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Seeded);
    value.?.count = 9;
    value.?.enabled = true;
    zalloc.zfreeValue(allocator, Seeded, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Seeded);
    defer zalloc.zfreeValue(allocator, Seeded, &value);
    try std.testing.expectEqual(@as(u8, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);
}
