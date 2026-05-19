const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

test "transition raws stay ordered as value, pointer gap, err floor, then next err" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const err_floor_raw = err_ptr.err_floor;
    const next_err_raw = err_ptr.err_floor + 1;

    try std.testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);
    try std.testing.expect(xa_value.isValue(inline_limit_raw));
    try std.testing.expectEqual(xa_value.safe_inline_limit, xa_value.toValue(inline_limit_raw));
    try std.testing.expect(!err_ptr.isErrValue(inline_limit_raw));

    try std.testing.expectEqual(inline_limit_raw + 1, gap_raw);
    try std.testing.expect(!xa_value.isValue(gap_raw));
    try std.testing.expect(!err_ptr.isErrValue(gap_raw));

    try std.testing.expectEqual(gap_raw + 1, err_floor_raw);
    try std.testing.expect(!xa_value.isValue(err_floor_raw));
    try std.testing.expect(err_ptr.isErrValue(err_floor_raw));
    try std.testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(err_floor_raw));

    try std.testing.expectEqual(err_floor_raw + 1, next_err_raw);
    try std.testing.expect(!xa_value.isValue(next_err_raw));
    try std.testing.expect(err_ptr.isErrValue(next_err_raw));
    try std.testing.expectEqual(@as(isize, -4094), err_ptr.toErrorCode(next_err_raw));
}

test "top of the err band keeps the even predecessor and tagged top raw distinct" {
    const penultimate_err_raw = err_ptr.fromErrorCode(-2);
    const top_err_raw = err_ptr.fromErrorCode(-1);

    try std.testing.expectEqual(top_err_raw - 1, penultimate_err_raw);
    try std.testing.expect((penultimate_err_raw & xa_value.value_tag_mask) == 0);
    try std.testing.expect((top_err_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);

    try std.testing.expect(!xa_value.isValue(penultimate_err_raw));
    try std.testing.expect(err_ptr.isErrValue(penultimate_err_raw));
    try std.testing.expectEqual(@as(isize, -2), err_ptr.toErrorCode(penultimate_err_raw));

    try std.testing.expect(!xa_value.isValue(top_err_raw));
    try std.testing.expect(err_ptr.isErrValue(top_err_raw));
    try std.testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(top_err_raw));
}

test "first and last rejected tagged xa_values land on the err band endpoints" {
    const first_rejected_value = xa_value.safe_inline_limit + 1;
    const first_rejected_raw = (first_rejected_value << 1) | xa_value.value_tag_mask;
    const tagged_err_count = (err_ptr.max_errno + 1) / 2;
    const last_rejected_value = xa_value.safe_inline_limit + tagged_err_count;
    const last_rejected_raw = (last_rejected_value << 1) | xa_value.value_tag_mask;

    try std.testing.expectEqual(err_ptr.err_floor, first_rejected_raw);
    try std.testing.expect(err_ptr.isErrValue(first_rejected_raw));
    try std.testing.expect(!xa_value.isValue(first_rejected_raw));

    try std.testing.expectEqual(err_ptr.fromErrorCode(-1), last_rejected_raw);
    try std.testing.expect(err_ptr.isErrValue(last_rejected_raw));
    try std.testing.expect(!xa_value.isValue(last_rejected_raw));
}
