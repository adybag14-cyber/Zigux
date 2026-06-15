const std = @import("std");

pub const max_errno: usize = 4095;
pub const err_floor: usize = @bitCast(-@as(isize, @intCast(max_errno)));

pub const ToErrorCodeError = error{
    NotErrPtr,
};

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

pub fn tryToErrorCode(raw: usize) ToErrorCodeError!isize {
    if (!isErrValue(raw)) {
        return error.NotErrPtr;
    }
    return @bitCast(raw);
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

test "checked error-code decoder rejects non-error values without decoding" {
    try std.testing.expectError(error.NotErrPtr, tryToErrorCode(0));
    try std.testing.expectError(error.NotErrPtr, tryToErrorCode(1));
    try std.testing.expectError(error.NotErrPtr, tryToErrorCode(err_floor - 1));
}

test "checked error-code decoder matches assert-backed decoder for err_ptr values" {
    const cases = [_]isize{
        -@as(isize, @intCast(max_errno)),
        -4094,
        -512,
        -22,
        -1,
    };

    for (cases) |code| {
        const raw = fromErrorCode(code);

        try std.testing.expectEqual(toErrorCode(raw), try tryToErrorCode(raw));
        try std.testing.expectEqual(code, try tryToErrorCode(raw));
    }
}
