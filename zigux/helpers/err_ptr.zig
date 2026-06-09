const std = @import("std");

pub const max_errno: usize = 4095;
pub const err_floor: usize = @bitCast(-@as(isize, @intCast(max_errno)));

pub const FromErrorCodeError = error{
    ErrorCodeMustBeNegative,
    ErrorCodeExceedsMaxErrno,
};

pub fn tryFromErrorCode(code: isize) FromErrorCodeError!usize {
    if (code > -1) {
        return error.ErrorCodeMustBeNegative;
    }
    if (code < -@as(isize, @intCast(max_errno))) {
        return error.ErrorCodeExceedsMaxErrno;
    }
    return @bitCast(code);
}

pub fn fromErrorCode(code: isize) usize {
    std.debug.assert(code <= -1);
    std.debug.assert(code >= -@as(isize, @intCast(max_errno)));
    return tryFromErrorCode(code) catch unreachable;
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

test "fallible err_ptr constructor reports invalid signed error codes" {
    try std.testing.expectError(error.ErrorCodeMustBeNegative, tryFromErrorCode(0));
    try std.testing.expectError(error.ErrorCodeMustBeNegative, tryFromErrorCode(1));
    try std.testing.expectError(
        error.ErrorCodeExceedsMaxErrno,
        tryFromErrorCode(-@as(isize, @intCast(max_errno)) - 1),
    );
}

test "fallible err_ptr constructor matches the assert-backed constructor" {
    const codes = [_]isize{
        -1,
        -2,
        -22,
        -@as(isize, @intCast(max_errno - 1)),
        -@as(isize, @intCast(max_errno)),
    };

    for (codes) |code| {
        const raw = try tryFromErrorCode(code);

        try std.testing.expectEqual(fromErrorCode(code), raw);
        try std.testing.expect(isErrValue(raw));
        try std.testing.expectEqual(code, toErrorCode(raw));
    }
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
