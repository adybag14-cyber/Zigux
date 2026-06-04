const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const Payload = struct {
    len: u16,
    ready: bool,
    tag: [4]u8,
};

test "helper ports C preserve caller windows across reentrant reuse" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.slabIsAvailable());

    var owner: ?[]u8 = slab.kzallocBytes(16, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(owner.?, 0xa5);
    slab.kfree(owner);
    owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var reacquired = slab.kcallocBytes(5, 4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(reacquired);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (reacquired) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var formatted = [_]u8{
        0xd0, 0xd1, 0xd2, 0xd3,
        0xd4, 0xd5, 0xd6, 0xd7,
        0xd8, 0xd9, 0xda, 0xdb,
    };
    const written = vsprintf.scnprintfPad(formatted[2..10], 6, "rc={d}", .{22});
    try std.testing.expectEqual(@as(usize, 6), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xd0, 0xd1 }, formatted[0..2]);
    try std.testing.expectEqualSlices(u8, "rc=22 ", formatted[2..8]);
    try std.testing.expectEqual(@as(u8, 0), formatted[8]);
    try std.testing.expectEqual(@as(u8, 0xd9), formatted[9]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xda, 0xdb }, formatted[10..12]);

    const rendered_error = str_error_r.strErrorR(22, reacquired[3..]);
    try std.testing.expectEqualStrings("Invalid argument", rendered_error);
    try std.testing.expectEqual(@as(u8, 0), reacquired[0]);
    try std.testing.expectEqual(@as(u8, 0), reacquired[1]);
    try std.testing.expectEqual(@as(u8, 0), reacquired[2]);
    try std.testing.expectEqual(@as(u8, 0), reacquired[3 + rendered_error.len]);

    var fallback = [_]u8{ 0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7 };
    const fallback_error = str_error_r.strErrorR(12345, fallback[1..7]);
    try std.testing.expectEqualStrings("INTER", fallback_error);
    try std.testing.expectEqual(@as(u8, 0xe0), fallback[0]);
    try std.testing.expectEqual(@as(u8, 0), fallback[6]);
    try std.testing.expectEqual(@as(u8, 0xe7), fallback[7]);
}

test "zalloc owners can hand formatted state to slab buffers and reset cleanly" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 8);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const wrote = vsprintf.scnprintf(bytes.?, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 5), wrote);
    try std.testing.expectEqualStrings("zigux", bytes.?[0..wrote]);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[wrote]);

    var payload: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expectEqual(@as(u16, 0), payload.?.len);
    try std.testing.expectEqual(false, payload.?.ready);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, payload.?.tag[0..]);

    payload.?.len = @intCast(wrote);
    payload.?.ready = true;
    @memcpy(payload.?.tag[0..], "fmt!");

    const slab_copy = slab.kmallocBytes(bytes.?.len, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_copy);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memcpy(slab_copy, bytes.?);
    try std.testing.expectEqualSlices(u8, bytes.?, slab_copy);

    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(bytes == null);
    try std.testing.expect(payload == null);

    var reacquired: ?[]u8 = try zalloc.zallocBytes(allocator, 8);
    defer zalloc.zfreeBytes(allocator, &reacquired);
    for (reacquired.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}
