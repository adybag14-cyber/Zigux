const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps independent live allocations balanced across null frees" {
    slab.kmalloc_nr_allocated = 0;

    const plain = slab.kmallocBytes(3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    const zeroed = slab.kmallocArray(2, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        slab.kfree(plain);
        return error.TestUnexpectedResult;
    };

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(plain, 0x7a);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "str_error_r offset windows keep neighboring bytes untouched" {
    var known_backing = [_]u8{'#'} ** 32;
    const known_window = known_backing[4..22];
    const known = str_error_r.strErrorR(13, known_window);

    try std.testing.expectEqualStrings("Permission denied", known);
    try std.testing.expectEqual(@as(u8, 0), known_window[known.len]);
    try std.testing.expectEqual(@as(u8, '#'), known_backing[3]);
    try std.testing.expectEqual(@as(u8, '#'), known_backing[22]);

    var generated_backing = [_]u8{'!'} ** 64;
    const generated_window = generated_backing[5..53];
    const generated = str_error_r.strErrorR(123, generated_window);

    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(123, [buf], 48)=22", generated);
    try std.testing.expectEqual(@as(u8, 0), generated_window[generated.len]);
    try std.testing.expectEqual(@as(u8, '!'), generated_backing[4]);
    try std.testing.expectEqual(@as(u8, '!'), generated_backing[53]);
}

test "vsprintf offset padding uses current logical-width return behavior" {
    var backing = [_]u8{'?'} ** 10;
    const window = backing[2..8];
    const written = vsprintf.scnprintfPad(window, 5, "{s}", .{"xy"});

    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualStrings("xy   ", window[0..5]);
    try std.testing.expectEqual(@as(u8, 0), window[5]);
    try std.testing.expectEqual(@as(u8, '?'), backing[1]);
    try std.testing.expectEqual(@as(u8, '?'), backing[8]);
}

test "zalloc value zeroes fresh array fields after a dirty free" {
    const allocator = std.testing.allocator;
    const Payload = struct {
        tag: u16,
        bytes: [4]u8,
    };

    var first: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    first.?.tag = 99;
    @memset(first.?.bytes[0..], 0xaa);
    zalloc.zfreeValue(allocator, Payload, &first);
    try std.testing.expect(first == null);

    var second: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &second);

    try std.testing.expectEqual(@as(u16, 0), second.?.tag);
    for (second.?.bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}
