const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab and zalloc cursor windows recycle through strerror summaries" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;

    var slab_owner = slab.kzallocBytes(48, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_owner) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const fallback_window = slab_owner[5..38];
    const fallback = str_error_r.strErrorR(9001, fallback_window);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(9001,", fallback);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[37]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[38]);

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    for (summary_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const padded = vsprintf.scnprintfPad(summary_owner.?, 24, "fallback:{s}", .{fallback[0..8]});
    try std.testing.expectEqual(@as(usize, 24), padded);
    try std.testing.expectEqualStrings("fallback:INTERNAL       ", summary_owner.?[0..padded]);
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[padded]);
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[padded + 1]);

    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);

    summary_owner = try zalloc.zallocBytes(allocator, 18);
    for (summary_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const known = str_error_r.strErrorR(22, slab_owner[9..26]);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[25]);

    const rewritten = vsprintf.scnprintf(summary_owner.?, "known:{s}", .{known});
    try std.testing.expectEqual(@as(usize, 17), rewritten);
    try std.testing.expectEqualStrings("known:Invalid arg", summary_owner.?[0..rewritten]);
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[rewritten]);
}

test "array cursors feed formatted value owners and rebalance counters" {
    const allocator = std.testing.allocator;
    const Snapshot = struct {
        label: [32]u8,
        fallback_len: usize,
        known_len: usize,
    };

    slab.kmalloc_nr_allocated = 0;

    var array_owner: ?[]u8 = slab.kcallocBytes(3, 18, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(array_owner);
    const array = array_owner.?;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const first = str_error_r.strErrorR(13, array[0..18]);
    const second = str_error_r.strErrorR(7100, array[18..36]);
    const third = str_error_r.strErrorR(0, array[36..54]);

    try std.testing.expectEqualStrings("Permission denied", first);
    try std.testing.expectEqualStrings("INTERNAL ERROR: s", second);
    try std.testing.expectEqualStrings("Success", third);
    try std.testing.expectEqual(@as(u8, 0), array[17]);
    try std.testing.expectEqual(@as(u8, 0), array[35]);
    try std.testing.expectEqual(@as(u8, 0), array[43]);

    var snapshot: ?*Snapshot = try zalloc.zallocValue(allocator, Snapshot);
    defer zalloc.zfreeValue(allocator, Snapshot, &snapshot);
    try std.testing.expectEqual(@as(usize, 0), snapshot.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 0), snapshot.?.known_len);
    for (&snapshot.?.label) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    snapshot.?.fallback_len = second.len;
    snapshot.?.known_len = first.len + third.len;
    const label_len = vsprintf.scnprintf(&snapshot.?.label, "{s}/{s}:{d}", .{
        first[0..4],
        third,
        snapshot.?.fallback_len,
    });
    try std.testing.expectEqual(@as(usize, 15), label_len);
    try std.testing.expectEqualStrings("Perm/Success:17", snapshot.?.label[0..label_len]);
    try std.testing.expectEqual(@as(u8, 0), snapshot.?.label[label_len]);

    zalloc.zfreeValue(allocator, Snapshot, &snapshot);
    try std.testing.expect(snapshot == null);

    snapshot = try zalloc.zallocValue(allocator, Snapshot);
    for (&snapshot.?.label) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try std.testing.expectEqual(@as(usize, 0), snapshot.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 0), snapshot.?.known_len);

    slab.kfree(array_owner);
    array_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
