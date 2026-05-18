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

test "phase3 err_ptr band starts with two contiguous error values" {
    const err_floor_raw = err_ptr.err_floor;
    const next_err_raw = err_floor_raw + 1;

    try std.testing.expectEqual(next_err_raw, err_ptr.fromErrorCode(-4094));
    try std.testing.expect(err_ptr.isErrValue(err_floor_raw));
    try std.testing.expect(err_ptr.isErrValue(next_err_raw));
    try std.testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(err_floor_raw));
    try std.testing.expectEqual(@as(isize, -4094), err_ptr.toErrorCode(next_err_raw));
    try std.testing.expect(!xa_value.isValue(err_floor_raw));
    try std.testing.expect(!xa_value.isValue(next_err_raw));
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

test "phase3 tagged cutoff order stays xa_value, gap, then err_ptr" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const err_floor_raw = err_ptr.err_floor;

    try std.testing.expectEqual(inline_limit_raw + 1, gap_raw);
    try std.testing.expectEqual(gap_raw + 1, err_floor_raw);

    try std.testing.expect(xa_value.isValue(inline_limit_raw));
    try std.testing.expect(!err_ptr.isErrValue(inline_limit_raw));

    try std.testing.expect(!xa_value.isValue(gap_raw));
    try std.testing.expect(err_ptr.isOkValue(gap_raw));

    try std.testing.expect(!xa_value.isValue(err_floor_raw));
    try std.testing.expect(err_ptr.isErrValue(err_floor_raw));
}

test "phase3 first rejected xa_value would alias the err_ptr floor" {
    const first_rejected = xa_value.safe_inline_limit + 1;
    const aliased_raw = (first_rejected << 1) | xa_value.value_tag_mask;

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(first_rejected));
    try std.testing.expectEqual(err_ptr.err_floor, aliased_raw);
    try std.testing.expect(err_ptr.isErrValue(aliased_raw));
    try std.testing.expect(!xa_value.isValue(aliased_raw));
}

test "phase3 err_ptr gap below floor stays pointer like" {
    const gap = err_ptr.err_floor - 1;
    try std.testing.expect(err_ptr.isOkValue(gap));
    try std.testing.expect(!err_ptr.isErrValue(gap));
}
