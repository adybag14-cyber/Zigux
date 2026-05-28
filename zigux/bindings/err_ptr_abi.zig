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

test "err_ptr ABI keeps the Linux error band explicit" {
    const low = fromErrorCode(-@as(isize, @intCast(max_errno)));
    const high = fromErrorCode(-1);

    try std.testing.expectEqual(err_floor, low);
    try std.testing.expectEqual(@as(isize, -@as(isize, @intCast(max_errno))), toErrorCode(low));
    try std.testing.expectEqual(@as(isize, -1), toErrorCode(high));
    try std.testing.expect(isErrValue(low));
    try std.testing.expect(isErrValue(high));
    try std.testing.expect(isOkValue(err_floor - 1));
    try std.testing.expect(!isErrValue(0));
}
