const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps allocation counts balanced across back-to-back reclaim cycles" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 3), first.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (first) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const second = slab.kmallocArray(2, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 4), second.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const third = slab.kmallocBytes(1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), third.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(third);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR can rewrite nested caller windows without touching outer sentinels" {
    var known = [_]u8{ 0xa0, 0xa1, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xb0, 0xb1 };
    const outer_known = str_error_r.strErrorR(0, known[2..10]);
    try std.testing.expectEqualStrings("Success", outer_known);
    try std.testing.expectEqual(@as(u8, 0xa0), known[0]);
    try std.testing.expectEqual(@as(u8, 0xa1), known[1]);
    try std.testing.expectEqual(@as(u8, 0), known[9]);
    try std.testing.expectEqual(@as(u8, 0xb0), known[10]);
    try std.testing.expectEqual(@as(u8, 0xb1), known[11]);

    const inner_known = str_error_r.strErrorR(22, known[4..8]);
    try std.testing.expectEqualStrings("Inv", inner_known);
    try std.testing.expectEqual(@as(u8, 'S'), known[2]);
    try std.testing.expectEqual(@as(u8, 'u'), known[3]);
    try std.testing.expectEqual(@as(u8, 0), known[7]);
    try std.testing.expectEqual(@as(u8, 's'), known[8]);
    try std.testing.expectEqual(@as(u8, 0), known[9]);

    var fallback = [_]u8{ 0xc0, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xd0 };
    const outer_fallback = str_error_r.strErrorR(4096, fallback[1..9]);
    try std.testing.expectEqualStrings("INTERNA", outer_fallback);
    try std.testing.expectEqual(@as(u8, 0xc0), fallback[0]);
    try std.testing.expectEqual(@as(u8, 0), fallback[8]);
    try std.testing.expectEqual(@as(u8, 0xd0), fallback[9]);
}

test "vsprintf shifted caller windows stay fenced across direct and padded rewrites" {
    var buffer = [_]u8{ 0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9 };

    const left = buffer[1..6];
    const left_written = vsprintf.scnprintf(left, "{s}", .{"west"});
    try std.testing.expectEqual(@as(usize, 4), left_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xe0, 'w', 'e', 's', 't', 0x00, 0xe6, 0xe7, 0xe8, 0xe9 }, &buffer);

    const right = buffer[4..9];
    const right_written = vsprintf.scnprintfPad(right, 4, "{s}", .{"x"});
    try std.testing.expectEqual(@as(usize, 3), right_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xe0, 'w', 'e', 's', 'x', ' ', ' ', ' ', 0x00, 0xe9 }, &buffer);

    const mirrored_written = vsprintf.vscnprintf(right, "{s}", .{"yz"});
    try std.testing.expectEqual(@as(usize, 2), mirrored_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xe0, 'w', 'e', 's', 'y', 'z', 0x00, ' ', 0x00, 0xe9 }, &buffer);
}

test "zalloc resets bytes and values across release-and-reacquire cycles" {
    const allocator = std.testing.allocator;
    const Owner = struct {
        count: u16,
        enabled: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    @memset(bytes.?, 0xab);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var owner: ?*Owner = try zalloc.zallocValue(allocator, Owner);
    try std.testing.expectEqual(@as(u16, 0), owner.?.count);
    try std.testing.expectEqual(false, owner.?.enabled);
    owner.?.count = 99;
    owner.?.enabled = true;
    zalloc.zfreeValue(allocator, Owner, &owner);
    try std.testing.expect(owner == null);

    owner = try zalloc.zallocValue(allocator, Owner);
    defer zalloc.zfreeValue(allocator, Owner, &owner);
    try std.testing.expectEqual(@as(u16, 0), owner.?.count);
    try std.testing.expectEqual(false, owner.?.enabled);
}
