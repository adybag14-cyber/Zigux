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

test "fromErrorCode and toErrorCode round-trip the err_ptr range" {
    const cases = [_]isize{ -1, -12, -4095 };

    for (cases) |code| {
        const raw = fromErrorCode(code);

        try std.testing.expect(isErrValue(raw));
        try std.testing.expect(!isOkValue(raw));
        try std.testing.expectEqual(code, toErrorCode(raw));
    }
}

test "err floor is the first err_ptr value" {
    try std.testing.expect(isErrValue(err_floor));
    try std.testing.expectEqual(@as(isize, -4095), toErrorCode(err_floor));
}

test "value immediately below err floor stays pointer-like" {
    const raw = err_floor - 1;

    try std.testing.expect(isOkValue(raw));
    try std.testing.expect(!isErrValue(raw));
}
