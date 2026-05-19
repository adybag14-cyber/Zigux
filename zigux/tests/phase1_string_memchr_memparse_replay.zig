const std = @import("std");
const string = @import("string");

test "phase1 string replay keeps memchrInv stable across the fast-path cutoff" {
    const word_bytes = @sizeOf(usize);
    const cutoff = word_bytes * 2;

    var non_zero_backing = [_]u8{0xaa} ** (word_bytes * 2);
    for (0..2) |extra| {
        const len = (cutoff - 1) + extra;
        const slice = non_zero_backing[0..len];

        @memset(non_zero_backing[0..], 0xaa);
        try std.testing.expectEqual(@as(?usize, null), string.memchrInv(slice, 0xaa));

        @memset(non_zero_backing[0..], 0xaa);
        slice[len - 1] = 0x33;
        try std.testing.expectEqual(@as(?usize, len - 1), string.memchrInv(slice, 0xaa));
    }

    var zero_backing = [_]u8{0} ** (word_bytes * 2);
    for (0..2) |extra| {
        const len = (cutoff - 1) + extra;
        const slice = zero_backing[0..len];

        @memset(zero_backing[0..], 0);
        try std.testing.expectEqual(@as(?usize, null), string.memchrInv(slice, 0));

        @memset(zero_backing[0..], 0);
        slice[len - 1] = 0x7f;
        try std.testing.expectEqual(@as(?usize, len - 1), string.memchrInv(slice, 0));
    }
}

test "phase1 string replay keeps memparse signed overflow and suffix rest aligned" {
    const positive = string.memparse("+9223372036854775808Ktail");
    try std.testing.expectEqual(@as(u64, std.math.maxInt(i64)), positive.value);
    try std.testing.expectEqualStrings("tail", positive.rest);

    const negative = string.memparse("-2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const octal = string.memparse("+010Mmore");
    try std.testing.expectEqual(@as(u64, 8 << 20), octal.value);
    try std.testing.expectEqualStrings("more", octal.rest);
}
