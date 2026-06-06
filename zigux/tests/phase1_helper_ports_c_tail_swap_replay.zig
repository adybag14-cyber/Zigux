const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab and zalloc tail windows swap formatted strerror ownership" {
    slab.kmalloc_nr_allocated = 0;
    const allocator = std.testing.allocator;

    var slab_owner = slab.kzallocBytes(48, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_owner);

    var plain_owner = slab.kmallocBytes(32, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(plain_owner);
    @memset(plain_owner, 0x7e);

    var scratch_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &scratch_owner);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[0]);
    try std.testing.expectEqual(@as(u8, 0), scratch_owner.?[0]);

    const slab_tail = slab_owner[16..40];
    const fallback = str_error_r.strErrorR(5150, slab_tail);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerro", fallback);
    try std.testing.expectEqual(@as(u8, 0), slab_tail[fallback.len]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[15]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[40]);

    const summary_len = vsprintf.scnprintf(scratch_owner.?[2..35], "tail:{s}", .{fallback});
    try std.testing.expectEqual(@as(usize, 28), summary_len);
    try std.testing.expectEqual(@as(u8, 0), scratch_owner.?[0]);
    try std.testing.expectEqual(@as(u8, 0), scratch_owner.?[1]);
    try std.testing.expectEqualStrings("tail:INTERNAL ERROR: strerro", scratch_owner.?[2 .. 2 + summary_len]);
    try std.testing.expectEqual(@as(u8, 0), scratch_owner.?[2 + summary_len]);

    const shorter = str_error_r.strErrorR(0, slab_tail);
    try std.testing.expectEqualStrings("Success", shorter);
    try std.testing.expectEqual(@as(u8, 0), slab_tail[shorter.len]);
    try std.testing.expectEqual(@as(u8, 0), scratch_owner.?[0]);
    try std.testing.expectEqual(@as(u8, ' '), slab_tail[shorter.len + 1]);
    try std.testing.expectEqual(@as(u8, 'E'), slab_tail[shorter.len + 2]);

    const padded_len = vsprintf.scnprintfPad(plain_owner[5..20], 10, "{s}:{d}", .{ shorter, summary_len });
    try std.testing.expectEqual(@as(usize, 10), padded_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x7e, 0x7e, 0x7e, 0x7e, 0x7e }, plain_owner[0..5]);
    try std.testing.expectEqualStrings("Success:28", plain_owner[5 .. 5 + padded_len]);
    try std.testing.expectEqual(@as(u8, 0), plain_owner[5 + padded_len]);
    try std.testing.expectEqual(@as(u8, 0x7e), plain_owner[20]);
}

test "failed slab requests and zalloc releases preserve live tail-swap owners" {
    slab.kmalloc_nr_allocated = 0;
    const allocator = std.testing.allocator;

    var live = slab.kzallocBytes(12, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(live);

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 8);
    defer zalloc.zfreeBytes(allocator, &bytes);

    const State = struct {
        rendered: usize,
        released: bool,
    };
    var state: ?*State = try zalloc.zallocValue(allocator, State);
    defer zalloc.zfreeValue(allocator, State, &state);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const rendered = vsprintf.scnprintf(live[1..10], "oom:{d}", .{bytes.?.len});
    try std.testing.expectEqual(@as(usize, 5), rendered);
    state.?.rendered = rendered;
    try std.testing.expectEqual(@as(usize, 5), state.?.rendered);
    try std.testing.expectEqualStrings("oom:8", live[1 .. 1 + rendered]);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    state.?.released = true;
    try std.testing.expectEqual(true, state.?.released);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
