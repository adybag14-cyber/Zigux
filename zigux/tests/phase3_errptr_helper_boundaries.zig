const std = @import("std");
const err_ptr = @import("../helpers/err_ptr.zig");

test "phase3 err_ptr floor and top remain error values" {
    try std.testing.expect(err_ptr.isErrValue(err_ptr.err_floor));
    try std.testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(err_ptr.err_floor));

    const err_top = err_ptr.fromErrorCode(-1);
    try std.testing.expect(err_ptr.isErrValue(err_top));
    try std.testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(err_top));
}

test "phase3 err_ptr gap below floor stays pointer like" {
    const gap = err_ptr.err_floor - 1;
    try std.testing.expect(err_ptr.isOkValue(gap));
    try std.testing.expect(!err_ptr.isErrValue(gap));
}
