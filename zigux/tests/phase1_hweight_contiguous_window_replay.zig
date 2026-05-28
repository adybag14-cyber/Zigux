const std = @import("std");
const hweight = @import("hweight");

fn contiguousMaskU32(comptime width: u6, start: u6, len: u6) u32 {
    if (len == 0) return 0;
    if (len == width) return std.math.maxInt(u32) >> (32 - width);

    const shift_len: std.math.Log2Int(u32) = @intCast(len);
    const shift_start: std.math.Log2Int(u32) = @intCast(start);
    const ones = (@as(u32, 1) << shift_len) - 1;
    return ones << shift_start;
}

fn contiguousMaskU64(comptime width: u7, start: u7, len: u7) u64 {
    if (len == 0) return 0;
    if (len == width) return std.math.maxInt(u64) >> (64 - width);

    const shift_len: std.math.Log2Int(u64) = @intCast(len);
    const shift_start: std.math.Log2Int(u64) = @intCast(start);
    const ones = (@as(u64, 1) << shift_len) - 1;
    return ones << shift_start;
}

fn contiguousMaskUsize(start: usize, len: usize) usize {
    const width = @bitSizeOf(usize);
    if (len == 0) return 0;
    if (len == width) return std.math.maxInt(usize);

    const ones = (@as(usize, 1) << @intCast(len)) - 1;
    return ones << @intCast(start);
}

test "hweight helpers keep contiguous one-bit windows aligned across fixed widths" {
    for (0..9) |len| {
        for (0..(9 - len)) |start| {
            const value = contiguousMaskU32(8, @intCast(start), @intCast(len));
            try std.testing.expectEqual(@as(u32, @intCast(len)), hweight.swHweight8(value));
        }
    }

    for (0..17) |len| {
        for (0..(17 - len)) |start| {
            const value = contiguousMaskU32(16, @intCast(start), @intCast(len));
            try std.testing.expectEqual(@as(u32, @intCast(len)), hweight.swHweight16(value));
        }
    }

    for (0..33) |len| {
        for (0..(33 - len)) |start| {
            const value = contiguousMaskU32(32, @intCast(start), @intCast(len));
            try std.testing.expectEqual(@as(u32, @intCast(len)), hweight.swHweight32(value));
        }
    }

    for (0..65) |len| {
        for (0..(65 - len)) |start| {
            const value = contiguousMaskU64(64, @intCast(start), @intCast(len));
            try std.testing.expectEqual(@as(u64, @intCast(len)), hweight.swHweight64(value));
        }
    }
}

test "hweight_long matches contiguous one-bit windows across the native word width" {
    const width = @bitSizeOf(usize);

    for (0..(width + 1)) |len| {
        for (0..(width + 1 - len)) |start| {
            const value = contiguousMaskUsize(start, len);
            try std.testing.expectEqual(len, hweight.hweightLong(value));
        }
    }
}
