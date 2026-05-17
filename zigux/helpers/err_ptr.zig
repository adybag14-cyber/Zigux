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
