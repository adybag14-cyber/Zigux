const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab payload transfers into zalloc owner while format windows stay bounded" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_payload = slab.kmallocArray(3, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_payload) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const slab_written = vsprintf.scnprintf(slab_payload[1..15], "slab:{d}", .{42});
    try std.testing.expectEqual(@as(usize, 7), slab_written);
    try std.testing.expectEqualStrings("slab:42", slab_payload[1 .. 1 + slab_written]);
    try std.testing.expectEqual(@as(u8, 0), slab_payload[1 + slab_written]);
    try std.testing.expectEqual(@as(u8, 0), slab_payload[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_payload[15]);

    var owned: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &owned);
    for (owned.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memcpy(owned.?[4 .. 4 + slab_written], slab_payload[1 .. 1 + slab_written]);
    try std.testing.expectEqualStrings("slab:42", owned.?[4 .. 4 + slab_written]);
    try std.testing.expectEqual(@as(u8, 0), owned.?[3]);
    try std.testing.expectEqual(@as(u8, 0), owned.?[11]);

    const padded = vsprintf.scnprintfPad(owned.?[12..21], 8, "e{d}", .{22});
    try std.testing.expectEqual(@as(usize, 8), padded);
    try std.testing.expectEqualStrings("e22     ", owned.?[12..20]);
    try std.testing.expectEqual(@as(u8, 0), owned.?[20]);
    try std.testing.expectEqual(@as(u8, 0), owned.?[21]);

    const error_text = str_error_r.strErrorR(12, owned.?[22..32]);
    try std.testing.expectEqualStrings("Cannot al", error_text);
    try std.testing.expectEqual(@as(u8, 0), owned.?[31]);

    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(slab_payload);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "failed slab allocation leaves existing zalloc owner and strerror window intact" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &owner);
    @memset(owner.?, 0x7e);

    const failed = slab.kmallocBytes(16, 0);
    try std.testing.expect(failed == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0x7e), owner.?[0]);
    try std.testing.expectEqual(@as(u8, 0x7e), owner.?[23]);

    const rendered = str_error_r.strErrorR(9999, owner.?[2..22]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: str", rendered);
    try std.testing.expectEqual(@as(u8, 0x7e), owner.?[1]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[21]);
    try std.testing.expectEqual(@as(u8, 0x7e), owner.?[22]);

    const zero_written = vsprintf.scnprintf(owner.?[5..5], "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), zero_written);
    try std.testing.expectEqual(@as(u8, 'E'), owner.?[5]);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
