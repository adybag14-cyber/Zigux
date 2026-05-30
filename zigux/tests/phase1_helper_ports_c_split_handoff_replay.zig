const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab caller windows hand off through strerror and padded formatting" {
    slab.kmalloc_nr_allocated = 0;

    const owner = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(owner, 0x7e);

    const strerror_view = owner[4..16];
    const rendered = str_error_r.strErrorR(22, strerror_view);
    try std.testing.expectEqualStrings("Invalid arg", rendered);
    try std.testing.expectEqual(@as(u8, 0x7e), owner[3]);
    try std.testing.expectEqual(@as(u8, 0), owner[15]);
    try std.testing.expectEqual(@as(u8, 0x7e), owner[16]);

    const padded_view = owner[18..28];
    const padded = vsprintf.scnprintfPad(padded_view, 8, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 7), padded);
    try std.testing.expectEqualSlices(u8, "ok      ", padded_view[0..8]);
    try std.testing.expectEqual(@as(u8, 0), padded_view[8]);
    try std.testing.expectEqual(@as(u8, 0x7e), owner[17]);
    try std.testing.expectEqual(@as(u8, 0x7e), owner[28]);

    slab.kfree(owner);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "zalloc fallback window can be reformatted and released twice" {
    const allocator = std.testing.allocator;

    var backing: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &backing);
    try std.testing.expect(backing != null);

    for (backing.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(backing.?, 0x40);
    const fallback = str_error_r.strErrorR(4096, backing.?[3..15]);
    try std.testing.expectEqualStrings("INTERNAL ER", fallback);
    try std.testing.expectEqual(@as(u8, 0x40), backing.?[2]);
    try std.testing.expectEqual(@as(u8, 0), backing.?[14]);
    try std.testing.expectEqual(@as(u8, 0x40), backing.?[15]);

    const written = vsprintf.vscnprintf(backing.?[15..23], "z:{d}", .{fallback.len});
    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualStrings("z:11", backing.?[15 .. 15 + written]);
    try std.testing.expectEqual(@as(u8, 0), backing.?[15 + written]);
    try std.testing.expectEqual(@as(u8, 0x40), backing.?[23]);

    zalloc.zfreeBytes(allocator, &backing);
    try std.testing.expect(backing == null);
    zalloc.zfreeBytes(allocator, &backing);
    try std.testing.expect(backing == null);
}

test "zalloc values can carry slab allocation totals through split views" {
    const allocator = std.testing.allocator;
    const Snapshot = struct {
        active_before: isize,
        rendered: [16]u8,
    };

    slab.kmalloc_nr_allocated = 0;
    var snapshot: ?*Snapshot = try zalloc.zallocValue(allocator, Snapshot);
    defer zalloc.zfreeValue(allocator, Snapshot, &snapshot);
    try std.testing.expect(snapshot != null);
    try std.testing.expectEqual(@as(isize, 0), snapshot.?.active_before);

    const slab_bytes = slab.kmallocArray(2, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    snapshot.?.active_before = slab.kmalloc_nr_allocated;
    @memset(&snapshot.?.rendered, 0x55);
    const view = snapshot.?.rendered[2..14];
    const count = vsprintf.scnprintf(view, "slab={d}", .{snapshot.?.active_before});
    try std.testing.expectEqual(@as(usize, 6), count);
    try std.testing.expectEqualStrings("slab=1", view[0..count]);
    try std.testing.expectEqual(@as(u8, 0x55), snapshot.?.rendered[1]);
    try std.testing.expectEqual(@as(u8, 0), view[count]);
    try std.testing.expectEqual(@as(u8, 0x55), snapshot.?.rendered[14]);
}
