const std = @import("std");

pub const max_errno: usize = 4095;
pub const err_floor: usize = @bitCast(-@as(isize, @intCast(max_errno)));

pub fn canRepresentErrorCode(code: isize) bool {
    return code <= -1 and code >= -@as(isize, @intCast(max_errno));
}

pub fn fromErrorCode(code: isize) usize {
    std.debug.assert(canRepresentErrorCode(code));
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
    std.debug.assert(canRepresentErrorCode(-1));
    std.debug.assert(canRepresentErrorCode(-@as(isize, @intCast(max_errno))));
    std.debug.assert(!canRepresentErrorCode(0));
    std.debug.assert(!canRepresentErrorCode(-@as(isize, @intCast(max_errno)) - 1));
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

test "err_ptr exposes the signed errno guard before encoding" {
    try std.testing.expect(canRepresentErrorCode(-1));
    try std.testing.expect(canRepresentErrorCode(-@as(isize, @intCast(max_errno))));

    try std.testing.expect(!canRepresentErrorCode(0));
    try std.testing.expect(!canRepresentErrorCode(1));
    try std.testing.expect(!canRepresentErrorCode(-@as(isize, @intCast(max_errno)) - 1));
}
