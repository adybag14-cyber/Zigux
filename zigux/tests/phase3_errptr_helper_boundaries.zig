const std = @import("std");
const err_ptr = @import("../helpers/err_ptr.zig");
const xa_value = @import("../helpers/xa_value.zig");

test "phase3 err_ptr floor and top remain error values" {
    try std.testing.expect(err_ptr.isErrValue(err_ptr.err_floor));
    try std.testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(err_ptr.err_floor));

    const err_top = err_ptr.fromErrorCode(-1);
    try std.testing.expect(err_ptr.isErrValue(err_top));
    try std.testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(err_top));
}

test "phase3 err_ptr tagged endpoints stay out of the xa_value lane" {
    const err_floor_raw = err_ptr.err_floor;
    const err_top_raw = err_ptr.fromErrorCode(-1);

    try std.testing.expect((err_floor_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expect((err_top_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expect(!xa_value.isValue(err_floor_raw));
    try std.testing.expect(!xa_value.isValue(err_top_raw));
}

test "phase3 highest xa_value stays below the err_ptr floor" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);

    try std.testing.expect(xa_value.isValue(inline_limit_raw));
    try std.testing.expectEqual(xa_value.safe_inline_limit, xa_value.toValue(inline_limit_raw));
    try std.testing.expect(!err_ptr.isErrValue(inline_limit_raw));
    try std.testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);
}

test "phase3 err_ptr gap below floor stays pointer like" {
    const gap = err_ptr.err_floor - 1;
    try std.testing.expect(err_ptr.isOkValue(gap));
    try std.testing.expect(!err_ptr.isErrValue(gap));
}
