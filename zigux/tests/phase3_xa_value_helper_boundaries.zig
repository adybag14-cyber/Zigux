const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

test "safe inline limit stays the last tagged xa_value before err_ptr floor" {
    const raw = try xa_value.makeValue(xa_value.safe_inline_limit);

    try testing.expect(xa_value.isValue(raw));
    try testing.expect(!err_ptr.isErrValue(raw));
    try testing.expectEqual(xa_value.safe_inline_limit, xa_value.toValue(raw));
    try testing.expectEqual(err_ptr.err_floor - 2, raw);
}

test "highest two tagged xa_values stay packed below the pointer gap" {
    const near_limit = xa_value.safe_inline_limit - 1;
    const near_limit_raw = try xa_value.makeValue(near_limit);
    const limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;

    try testing.expect(xa_value.isValue(near_limit_raw));
    try testing.expectEqual(near_limit, xa_value.toValue(near_limit_raw));
    try testing.expectEqual(near_limit_raw + 2, limit_raw);
    try testing.expectEqual(limit_raw + 1, gap_raw);
    try testing.expect(!xa_value.isValue(gap_raw));
    try testing.expect(err_ptr.isOkValue(gap_raw));
}

test "first rejected inline value would alias err_ptr floor if it were encoded" {
    const overflow = xa_value.safe_inline_limit + 1;
    const aliased_raw = (overflow << 1) | xa_value.value_tag_mask;

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overflow));
    try testing.expectEqual(err_ptr.err_floor, aliased_raw);
    try testing.expect(err_ptr.isErrValue(aliased_raw));
    try testing.expect(!xa_value.isValue(aliased_raw));
    try testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(aliased_raw));
}

test "second rejected inline value skips the first in-band neighbor and lands on the next tagged err_ptr raw" {
    const first_rejected = xa_value.safe_inline_limit + 1;
    const second_rejected = first_rejected + 1;
    const first_err_raw = err_ptr.err_floor;
    const skipped_err_raw = first_err_raw + 1;
    const aliased_raw = (second_rejected << 1) | xa_value.value_tag_mask;

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(second_rejected));
    try testing.expectEqual(first_err_raw + 2, aliased_raw);
    try testing.expectEqual(@as(isize, -4094), err_ptr.toErrorCode(skipped_err_raw));
    try testing.expectEqual(@as(isize, -4093), err_ptr.toErrorCode(aliased_raw));
    try testing.expect(err_ptr.isErrValue(skipped_err_raw));
    try testing.expect(err_ptr.isErrValue(aliased_raw));
    try testing.expect(!xa_value.isValue(skipped_err_raw));
    try testing.expect(!xa_value.isValue(aliased_raw));
    try testing.expectEqual(@as(usize, 0), skipped_err_raw & xa_value.value_tag_mask);
    try testing.expectEqual(xa_value.value_tag_mask, aliased_raw & xa_value.value_tag_mask);
}

test "cutoff sequence keeps xa_value, gap, and first two err_ptr raws in distinct lanes" {
    const highest_xa_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const first_err_raw = err_ptr.err_floor;
    const second_err_raw = first_err_raw + 1;

    try testing.expectEqual(highest_xa_raw + 1, gap_raw);
    try testing.expectEqual(gap_raw + 1, first_err_raw);
    try testing.expectEqual(first_err_raw + 1, second_err_raw);

    try testing.expect(xa_value.isValue(highest_xa_raw));
    try testing.expect(!xa_value.isValue(gap_raw));
    try testing.expect(!xa_value.isValue(first_err_raw));
    try testing.expect(!xa_value.isValue(second_err_raw));

    try testing.expect(!err_ptr.isErrValue(highest_xa_raw));
    try testing.expect(!err_ptr.isErrValue(gap_raw));
    try testing.expect(err_ptr.isErrValue(first_err_raw));
    try testing.expect(err_ptr.isErrValue(second_err_raw));

    try testing.expectEqual(xa_value.value_tag_mask, highest_xa_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), gap_raw & xa_value.value_tag_mask);
    try testing.expectEqual(xa_value.value_tag_mask, first_err_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), second_err_raw & xa_value.value_tag_mask);

    try testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(first_err_raw));
    try testing.expectEqual(@as(isize, -4094), err_ptr.toErrorCode(second_err_raw));
}

test "last rejected inline value aliases the top tagged err_ptr raw" {
    const rejected_value_count = (err_ptr.max_errno + 1) / 2;
    const last_rejected = xa_value.safe_inline_limit + rejected_value_count;
    const previous_rejected = last_rejected - 1;
    const previous_aliased_raw = (previous_rejected << 1) | xa_value.value_tag_mask;
    const aliased_raw = (last_rejected << 1) | xa_value.value_tag_mask;
    const top_raw = err_ptr.fromErrorCode(-1);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(last_rejected));
    try testing.expectEqual(top_raw - 2, previous_aliased_raw);
    try testing.expectEqual(top_raw, aliased_raw);
    try testing.expect(err_ptr.isErrValue(previous_aliased_raw));
    try testing.expect(err_ptr.isErrValue(aliased_raw));
    try testing.expect(!xa_value.isValue(previous_aliased_raw));
    try testing.expect(!xa_value.isValue(aliased_raw));
    try testing.expectEqual(@as(isize, -3), err_ptr.toErrorCode(previous_aliased_raw));
    try testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(aliased_raw));
}

test "top of err_ptr band stays contiguous and never reenters xa_value lane" {
    const next_to_top_raw = err_ptr.fromErrorCode(-2);
    const top_raw = err_ptr.fromErrorCode(-1);

    try testing.expectEqual(next_to_top_raw + 1, top_raw);
    try testing.expect(err_ptr.isErrValue(next_to_top_raw));
    try testing.expect(err_ptr.isErrValue(top_raw));
    try testing.expect(!xa_value.isValue(next_to_top_raw));
    try testing.expect(!xa_value.isValue(top_raw));
    try testing.expectEqual(@as(isize, -2), err_ptr.toErrorCode(next_to_top_raw));
    try testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(top_raw));
    try testing.expectEqual(@as(usize, 0), next_to_top_raw & xa_value.value_tag_mask);
    try testing.expectEqual(xa_value.value_tag_mask, top_raw & xa_value.value_tag_mask);
}

test "gap before err_ptr floor stays pointer-like and never decodes as xa_value" {
    const raw = err_ptr.err_floor - 1;

    try testing.expect(!err_ptr.isErrValue(raw));
    try testing.expect(!xa_value.isValue(raw));
    try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
}
