const std = @import("std");
const hweight = @import("hweight");

fn grayCode(comptime T: type, value: T) T {
    return value ^ (value >> 1);
}

fn expectGrayStep8(prev_index: u32, next_index: u32) !void {
    const prev = grayCode(u32, prev_index);
    const next = grayCode(u32, next_index);
    const delta = prev ^ next;

    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight8(delta));
    try std.testing.expectEqual(@as(u32, 1), hweight.__sw_hweight8(delta));
    try std.testing.expectEqual(@as(u32, @popCount(next)), hweight.swHweight8(next));
    try std.testing.expectEqual(@as(u32, @popCount(next)), hweight.__sw_hweight8(next));
}

fn expectGrayStep16(prev_index: u32, next_index: u32) !void {
    const prev = grayCode(u32, prev_index);
    const next = grayCode(u32, next_index);
    const delta = prev ^ next;

    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight16(delta));
    try std.testing.expectEqual(@as(u32, 1), hweight.__sw_hweight16(delta));
    try std.testing.expectEqual(@as(u32, @popCount(next)), hweight.swHweight16(next));
    try std.testing.expectEqual(@as(u32, @popCount(next)), hweight.__sw_hweight16(next));
}

fn expectGrayStep32(prev_index: u32, next_index: u32) !void {
    const prev = grayCode(u32, prev_index);
    const next = grayCode(u32, next_index);
    const delta = prev ^ next;

    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight32(delta));
    try std.testing.expectEqual(@as(u32, 1), hweight.__sw_hweight32(delta));
    try std.testing.expectEqual(@as(u32, @popCount(next)), hweight.swHweight32(next));
    try std.testing.expectEqual(@as(u32, @popCount(next)), hweight.__sw_hweight32(next));
}

fn expectGrayStep64(prev_index: u64, next_index: u64) !void {
    const prev = grayCode(u64, prev_index);
    const next = grayCode(u64, next_index);
    const delta = prev ^ next;

    try std.testing.expectEqual(@as(u64, 1), hweight.swHweight64(delta));
    try std.testing.expectEqual(@as(u64, 1), hweight.__sw_hweight64(delta));
    try std.testing.expectEqual(@as(u64, @popCount(next)), hweight.swHweight64(next));
    try std.testing.expectEqual(@as(u64, @popCount(next)), hweight.__sw_hweight64(next));
}

fn expectGrayStepLong(prev_index: usize, next_index: usize) !void {
    const prev = grayCode(usize, prev_index);
    const next = grayCode(usize, next_index);
    const delta = prev ^ next;

    try std.testing.expectEqual(@as(usize, 1), hweight.hweightLong(delta));
    try std.testing.expectEqual(@as(usize, 1), hweight.hweight_long(delta));
    try std.testing.expectEqual(@as(usize, @popCount(next)), hweight.hweightLong(next));
    try std.testing.expectEqual(@as(usize, @popCount(next)), hweight.hweight_long(next));
}

test "hweight gray-step replay exhaustively keeps 8-bit transitions onehot" {
    var index: u32 = 1;
    while (index < 0x100) : (index += 1) {
        try expectGrayStep8(index - 1, index);
    }
}

test "hweight gray-step replay keeps wider fixed-width transitions onehot" {
    for ([_]u32{ 1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 128, 255, 256, 511, 512, 1023, 1024, 4095, 4096, 16383, 16384, 32767, 32768, 65535 }) |index| {
        try expectGrayStep16(index - 1, index);
    }

    for ([_]u32{ 1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 128, 255, 256, 511, 512, 1023, 1024, 4095, 4096, 65535, 65536, 131071, 131072, 524287, 524288, 1_048_575, 1_048_576, 16_777_215, 16_777_216, 268_435_455, 268_435_456, 2_147_483_647, 2_147_483_648, 4_294_967_295 }) |index| {
        try expectGrayStep32(index - 1, index);
    }

    for ([_]u64{ 1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 128, 255, 256, 511, 512, 1023, 1024, 4095, 4096, 65_535, 65_536, 1_048_575, 1_048_576, 16_777_215, 16_777_216, 268_435_455, 268_435_456, 4_294_967_295, 4_294_967_296, 68_719_476_735, 68_719_476_736, 1_099_511_627_775, 1_099_511_627_776, 17_592_186_044_415, 17_592_186_044_416, 281_474_976_710_655, 281_474_976_710_656, 4_611_686_018_427_387_903, 4_611_686_018_427_387_904, 9_223_372_036_854_775_807, 9_223_372_036_854_775_808 }) |index| {
        try expectGrayStep64(index - 1, index);
    }
}

test "hweight gray-step replay stays aligned through native-word routing" {
    if (@sizeOf(usize) == 4) {
        for ([_]usize{ 1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 128, 255, 256, 4095, 4096, 65_535, 65_536, 1_048_575, 1_048_576, 16_777_215, 16_777_216, 2_147_483_647, 2_147_483_648, 4_294_967_295 }) |index| {
            try expectGrayStepLong(index - 1, index);
        }
    } else {
        for ([_]usize{ 1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 128, 255, 256, 4095, 4096, 65_535, 65_536, 1_048_575, 1_048_576, 16_777_215, 16_777_216, 4_294_967_295, 4_294_967_296, 68_719_476_735, 68_719_476_736, 1_099_511_627_775, 1_099_511_627_776, 17_592_186_044_415, 17_592_186_044_416, 281_474_976_710_655, 281_474_976_710_656, 4_611_686_018_427_387_903, 4_611_686_018_427_387_904, 9_223_372_036_854_775_807, 9_223_372_036_854_775_808 }) |index| {
            try expectGrayStepLong(index - 1, index);
        }
    }
}
