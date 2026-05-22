const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps zero-length live allocations balanced across failed growth and peer frees" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const peer = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        slab.kfree(empty);
        return error.TestUnexpectedResult;
    };

    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (peer) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(peer);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR exact-fit generated windows preserve sentinels and terminator ownership" {
    var expected_buffer: [64]u8 = undefined;
    const probe = try std.fmt.bufPrint(
        &expected_buffer,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 77, 40 },
    );
    const needed = probe.len + 1;

    var backing = [_]u8{'~'} ** 64;
    const window = backing[3 .. 3 + needed];
    const rendered = str_error_r.strErrorR(77, window);
    const expected = try std.fmt.bufPrint(
        &expected_buffer,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 77, window.len },
    );

    try std.testing.expectEqualStrings(expected, rendered);
    try std.testing.expectEqual(@as(u8, 0), window[rendered.len]);
    try std.testing.expectEqual(@as(u8, '~'), backing[2]);
    try std.testing.expectEqual(@as(u8, '~'), backing[3 + needed]);
}

test "scnprintfPad clamps logical size to the caller window and zero-size rewrites stay local" {
    var backing = [_]u8{'!'} ** 12;
    const window = backing[3..8];

    const padded = vsprintf.scnprintfPad(window, 99, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 3), padded);
    try std.testing.expectEqualStrings("xy  ", window[0..4]);
    try std.testing.expectEqual(@as(u8, 0), window[4]);
    try std.testing.expectEqual(@as(u8, '!'), backing[2]);
    try std.testing.expectEqual(@as(u8, '!'), backing[8]);

    const reset = vsprintf.scnprintfPad(window, 0, "{s}", .{"later"});
    try std.testing.expectEqual(@as(usize, 0), reset);
    try std.testing.expectEqual(@as(u8, 0), window[0]);
    try std.testing.expectEqual(@as(u8, 'y'), window[1]);
    try std.testing.expectEqual(@as(u8, ' '), window[2]);
    try std.testing.expectEqual(@as(u8, ' '), window[3]);
    try std.testing.expectEqual(@as(u8, 0), window[4]);
    try std.testing.expectEqual(@as(u8, '!'), backing[2]);
    try std.testing.expectEqual(@as(u8, '!'), backing[8]);
}

test "zalloc zero-length byte ownership and value re-zeroing stay isolated from siblings" {
    const allocator = std.testing.allocator;

    const BytesHolder = struct {
        keep: u8,
        bytes: ?[]u8,
        tail: u8,
    };
    var holder = BytesHolder{
        .keep = 0x2a,
        .bytes = try zalloc.zallocBytes(allocator, 0),
        .tail = 0x5b,
    };
    try std.testing.expect(holder.bytes != null);
    try std.testing.expectEqual(@as(usize, 0), holder.bytes.?.len);
    zalloc.zfreeBytes(allocator, &holder.bytes);
    try std.testing.expect(holder.bytes == null);
    try std.testing.expectEqual(@as(u8, 0x2a), holder.keep);
    try std.testing.expectEqual(@as(u8, 0x5b), holder.tail);

    const Payload = struct {
        enabled: bool,
        maybe: ?u16,
        bytes: [2]u8,
    };
    var first: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    first.?.enabled = true;
    first.?.maybe = 9;
    first.?.bytes = .{ 0xaa, 0xbb };
    zalloc.zfreeValue(allocator, Payload, &first);
    try std.testing.expect(first == null);

    var second: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &second);
    try std.testing.expect(second != null);
    try std.testing.expectEqual(false, second.?.enabled);
    try std.testing.expect(second.?.maybe == null);
    try std.testing.expectEqual(@as(u8, 0), second.?.bytes[0]);
    try std.testing.expectEqual(@as(u8, 0), second.?.bytes[1]);
}
