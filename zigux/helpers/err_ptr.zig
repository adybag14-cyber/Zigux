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

test "error band boundaries round-trip through err_ptr encoding" {
    const highest = fromErrorCode(-1);
    const lowest = fromErrorCode(-@as(isize, @intCast(max_errno)));

    try std.testing.expect(isErrValue(highest));
    try std.testing.expect(isErrValue(lowest));
    try std.testing.expectEqual(@as(isize, -1), toErrorCode(highest));
    try std.testing.expectEqual(-@as(isize, @intCast(max_errno)), toErrorCode(lowest));
    try std.testing.expectEqual(err_floor, lowest);
}

test "values below the err_ptr floor stay classified as ok pointers" {
    const gap_before_floor = err_floor - 1;

    try std.testing.expect(isOkValue(0));
    try std.testing.expect(isOkValue(gap_before_floor));
    try std.testing.expect(!isErrValue(gap_before_floor));
}
