const std = @import("std");

pub const max_errno: usize = 4095;
pub const err_floor: usize = @bitCast(-@as(isize, @intCast(max_errno)));

pub fn fromErrorCode(code: isize) usize {
    std.debug.assert(code <= -1);
    std.debug.assert(code >= -@as(isize, @intCast(max_errno)));
    return @bitCast(code);
}

pub fn isErrValue(raw: usize) bool {
    return raw >= err_floor;
}

pub fn toErrorCode(raw: usize) isize {
    std.debug.assert(isErrValue(raw));
    return @bitCast(raw);
}

pub fn isOkValue(raw: usize) bool {
    return !isErrValue(raw);
}

comptime {
    std.debug.assert(max_errno == 4095);
    std.debug.assert(isErrValue(err_floor));
    std.debug.assert(isOkValue(err_floor - 1));
}

test "err_ptr encodes the Linux error band as a tagged pointer-sized value" {
    const low = fromErrorCode(-@as(isize, @intCast(max_errno)));
    const high = fromErrorCode(-1);

    try std.testing.expectEqual(err_floor, low);
    try std.testing.expectEqual(@as(isize, -@as(isize, @intCast(max_errno))), toErrorCode(low));
    try std.testing.expectEqual(@as(isize, -1), toErrorCode(high));
    try std.testing.expect(isErrValue(low));
    try std.testing.expect(isErrValue(high));
}

test "err_ptr keeps the floor boundary explicit" {
    try std.testing.expect(isErrValue(err_floor));
    try std.testing.expect(!isErrValue(err_floor - 1));
    try std.testing.expect(isOkValue(err_floor - 1));
}

test "non-error values stay outside the err_ptr band" {
    try std.testing.expect(isOkValue(0));
    try std.testing.expect(isOkValue(1));
    try std.testing.expect(!isErrValue(0));
    try std.testing.expect(!isErrValue(1));
}

test "adjacent Linux errno encodings keep raw monotonic spacing" {
    const samples = [_]isize{
        -1,
        -2,
        -12,
        -13,
        -22,
        -23,
        -4094,
        -4095,
    };

    for (samples[0 .. samples.len - 1], samples[1..]) |previous_code, current_code| {
        const previous_raw = fromErrorCode(previous_code);
        const current_raw = fromErrorCode(current_code);

        try std.testing.expect(previous_code > current_code);
        try std.testing.expect(previous_raw > current_raw);
        try std.testing.expectEqual(previous_code, toErrorCode(previous_raw));
        try std.testing.expectEqual(current_code, toErrorCode(current_raw));
        try std.testing.expect(isErrValue(previous_raw));
        try std.testing.expect(isErrValue(current_raw));

        if (previous_code - current_code == 1) {
            try std.testing.expectEqual(@as(usize, 1), previous_raw - current_raw);
        }
    }
}
