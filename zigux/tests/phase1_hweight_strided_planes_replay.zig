const std = @import("std");
const hweight = @import("hweight");

fn stridedMask32(comptime bits: usize, stride: usize, offset: usize) u32 {
    var mask: u32 = 0;
    var bit = offset;
    while (bit < bits) : (bit += stride) {
        mask |= @as(u32, 1) << @intCast(bit);
    }
    return mask;
}

fn stridedMask64(stride: usize, offset: usize) u64 {
    var mask: u64 = 0;
    var bit = offset;
    while (bit < 64) : (bit += stride) {
        mask |= @as(u64, 1) << @intCast(bit);
    }
    return mask;
}

fn stridedMaskLong(stride: usize, offset: usize) usize {
    var mask: usize = 0;
    var bit = offset;
    while (bit < @bitSizeOf(usize)) : (bit += stride) {
        mask |= @as(usize, 1) << @intCast(bit);
    }
    return mask;
}

test "phase 1 hweight strided bit planes partition fixed widths" {
    inline for ([_]usize{ 2, 3, 5 }) |stride| {
        var covered8: u32 = 0;
        var count8: u32 = 0;
        var offset: usize = 0;
        while (offset < stride) : (offset += 1) {
            const plane = stridedMask32(8, stride, offset);
            try std.testing.expectEqual(@popCount(plane), hweight.swHweight8(plane));
            covered8 |= plane;
            count8 += hweight.swHweight8(plane);
        }
        try std.testing.expectEqual(@as(u32, 0xff), covered8);
        try std.testing.expectEqual(@as(u32, 8), count8);

        var covered16: u32 = 0;
        var count16: u32 = 0;
        offset = 0;
        while (offset < stride) : (offset += 1) {
            const plane = stridedMask32(16, stride, offset);
            try std.testing.expectEqual(@popCount(plane), hweight.swHweight16(plane));
            covered16 |= plane;
            count16 += hweight.swHweight16(plane);
        }
        try std.testing.expectEqual(@as(u32, 0xffff), covered16);
        try std.testing.expectEqual(@as(u32, 16), count16);
    }
}

test "phase 1 hweight strided planes preserve 32 and 64 bit counts" {
    for ([_]usize{ 2, 4, 7 }) |stride| {
        var offset: usize = 0;
        while (offset < stride) : (offset += 1) {
            const plane32 = stridedMask32(32, stride, offset);
            const plane64 = stridedMask64(stride, offset);

            try std.testing.expectEqual(@popCount(plane32), hweight.swHweight32(plane32));
            try std.testing.expectEqual(@popCount(plane64), hweight.swHweight64(plane64));
            try std.testing.expectEqual(
                @as(u64, hweight.swHweight32(@truncate(plane64 >> 32))) + hweight.swHweight32(@truncate(plane64)),
                hweight.swHweight64(plane64),
            );
        }
    }
}

test "phase 1 hweight native long follows usize strided coverage" {
    const even_bits = stridedMaskLong(2, 0);
    const odd_bits = stridedMaskLong(2, 1);
    const all_bits = even_bits | odd_bits;

    try std.testing.expectEqual(@popCount(even_bits), hweight.hweightLong(even_bits));
    try std.testing.expectEqual(@popCount(odd_bits), hweight.hweightLong(odd_bits));
    try std.testing.expectEqual(@bitSizeOf(usize), hweight.hweightLong(all_bits));

    const every_third = stridedMaskLong(3, 0);
    try std.testing.expectEqual(@popCount(every_third), hweight.hweightLong(every_third));
}
