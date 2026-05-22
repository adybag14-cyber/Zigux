const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

test "accepted inline raw, pointer-like gap, and err floor stay contiguous" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = inline_limit_raw + 1;
    const floor_raw = gap_raw + 1;

    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);
    try testing.expect(xa_value.isValue(inline_limit_raw));
    try testing.expectEqual(xa_value.safe_inline_limit, xa_value.toValue(inline_limit_raw));
    try testing.expect(!err_ptr.isErrValue(inline_limit_raw));

    try testing.expectEqual(err_ptr.err_floor - 1, gap_raw);
    try testing.expect(!xa_value.isValue(gap_raw));
    try testing.expect(!err_ptr.isErrValue(gap_raw));
    try testing.expect(err_ptr.isOkValue(gap_raw));

    try testing.expectEqual(err_ptr.err_floor, floor_raw);
    try testing.expect(!xa_value.isValue(floor_raw));
    try testing.expect(err_ptr.isErrValue(floor_raw));
    try testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(floor_raw));
}

test "err_ptr codes stay contiguous above the floor" {
    const cases = [_]isize{ -4095, -4094, -4093, -22, -2, -1 };

    inline for (cases) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const offset: usize = @intCast(code + @as(isize, @intCast(err_ptr.max_errno)));

        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expectEqual(err_ptr.err_floor + offset, raw);
        try testing.expectEqual(code, err_ptr.toErrorCode(raw));
        try testing.expect(!xa_value.isValue(raw));
    }
}

test "first rejected xa_values alias every other leading err_ptr raw" {
    inline for (0..3) |index| {
        const rejected_value = xa_value.safe_inline_limit + 1 + index;
        const rejected_raw = (rejected_value << 1) | xa_value.value_tag_mask;
        const expected_code = -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(index * 2));

        try testing.expect(!xa_value.canRepresent(rejected_value));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
        try testing.expect(err_ptr.isErrValue(rejected_raw));
        try testing.expectEqual(err_ptr.fromErrorCode(expected_code), rejected_raw);
        try testing.expectEqual(expected_code, err_ptr.toErrorCode(rejected_raw));
    }
}
