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

test "err_ptr helper round-trips both ends of the Linux error band" {
    const floor_raw = fromErrorCode(-@as(isize, @intCast(max_errno)));
    const top_raw = fromErrorCode(-1);

    try std.testing.expectEqual(err_floor, floor_raw);
    try std.testing.expectEqual(std.math.maxInt(usize), top_raw);
    try std.testing.expect(isErrValue(floor_raw));
    try std.testing.expect(isErrValue(top_raw));
    try std.testing.expectEqual(-@as(isize, @intCast(max_errno)), toErrorCode(floor_raw));
    try std.testing.expectEqual(@as(isize, -1), toErrorCode(top_raw));
}

test "raw value just below err_floor stays outside the error lane" {
    const raw = err_floor - 1;

    try std.testing.expect(isOkValue(raw));
    try std.testing.expect(!isErrValue(raw));
}
