const std = @import("std");
const hweight = @import("hweight");

fn bytePopcountSum32(value: u32) u32 {
    var sum: u32 = 0;
    var shift: usize = 0;
    while (shift < 32) : (shift += 8) {
        sum += hweight.swHweight8((value >> @intCast(shift)) & 0xff);
    }
    return sum;
}

fn bytePopcountSum64(value: u64) u64 {
    var sum: u64 = 0;
    var shift: usize = 0;
    while (shift < 64) : (shift += 8) {
        sum += hweight.swHweight8(@intCast((value >> @intCast(shift)) & 0xff));
    }
    return sum;
}

test "hweight32 equals the sum of independent byte partitions" {
    const samples = [_]u32{
        0x0000_0000,
        0x0000_00ff,
        0xff00_0000,
        0x0f0f_f0f0,
        0x1357_9bdf,
        0x8000_0001,
        0xffff_ffff,
    };

    for (samples) |sample| {
        const expected = bytePopcountSum32(sample);
        try std.testing.expectEqual(expected, hweight.swHweight32(sample));
    }
}

test "hweight64 and hweightLong preserve byte partition totals" {
    const samples = [_]u64{
        0x0000_0000_0000_0000,
        0x0000_0000_0000_00ff,
        0xff00_0000_0000_0000,
        0x0123_4567_89ab_cdef,
        0x8181_4242_2424_1818,
        0xffff_ffff_ffff_ffff,
    };

    for (samples) |sample| {
        const expected = bytePopcountSum64(sample);
        try std.testing.expectEqual(expected, hweight.swHweight64(sample));

        const native_sample: usize = @truncate(sample);
        const native_expected: usize = if (@sizeOf(usize) == 4)
            bytePopcountSum32(@truncate(sample))
        else
            @intCast(expected);
        try std.testing.expectEqual(native_expected, hweight.hweightLong(native_sample));
    }
}
