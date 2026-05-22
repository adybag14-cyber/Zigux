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
    std.debug.assert(canRepresentErrorCode(-4095));
    std.debug.assert(!canRepresentErrorCode(0));
    std.debug.assert(!canRepresentErrorCode(-4096));
    std.debug.assert(isErrValue(err_floor));
    std.debug.assert(isOkValue(err_floor - 1));
}

test "err_ptr accepts exactly the Linux errno window" {
    try std.testing.expect(canRepresentErrorCode(-1));
    try std.testing.expect(canRepresentErrorCode(-22));
    try std.testing.expect(canRepresentErrorCode(-4095));
    try std.testing.expect(!canRepresentErrorCode(0));
    try std.testing.expect(!canRepresentErrorCode(1));
    try std.testing.expect(!canRepresentErrorCode(-4096));
}

test "err_ptr boundary encodings round-trip at both ends of the window" {
    const floor_raw = fromErrorCode(-4095);
    const top_raw = fromErrorCode(-1);

    try std.testing.expectEqual(err_floor, floor_raw);
    try std.testing.expect(isErrValue(floor_raw));
    try std.testing.expectEqual(@as(isize, -4095), toErrorCode(floor_raw));

    try std.testing.expect(isErrValue(top_raw));
    try std.testing.expectEqual(@as(isize, -1), toErrorCode(top_raw));
    try std.testing.expect(top_raw > floor_raw);
}

test "raw value below err floor stays outside the err_ptr band" {
    const raw = err_floor - 1;

    try std.testing.expect(isOkValue(raw));
    try std.testing.expect(!isErrValue(raw));
}
