const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

test "leading rejected xa_value aliases stay paired with adjacent err_ptr neighbors" {
    inline for (0..4) |index| {
        const rejected_value = xa_value.safe_inline_limit + 1 + index;
        const odd_alias_raw = (rejected_value << 1) | xa_value.value_tag_mask;
        const even_neighbor_raw = odd_alias_raw + 1;
        const odd_code = err_ptr.toErrorCode(odd_alias_raw);
        const even_code = err_ptr.toErrorCode(even_neighbor_raw);
        const expected_odd_code = -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(index * 2));

        try testing.expect(!xa_value.canRepresent(rejected_value));
        try testing.expect(err_ptr.isErrValue(odd_alias_raw));
        try testing.expect(err_ptr.isErrValue(even_neighbor_raw));
        try testing.expect(!xa_value.isValue(odd_alias_raw));
        try testing.expect(!xa_value.isValue(even_neighbor_raw));
        try testing.expectEqual(err_ptr.err_floor + (index * 2), odd_alias_raw);
        try testing.expectEqual(odd_alias_raw + 1, even_neighbor_raw);
        try testing.expectEqual(expected_odd_code, odd_code);
        try testing.expectEqual(expected_odd_code + 1, even_code);
    }
}

test "rejected alias raws preserve the would-be xa_value payload bits" {
    inline for (0..4) |index| {
        const rejected_value = xa_value.safe_inline_limit + 1 + index;
        const odd_alias_raw = (rejected_value << 1) | xa_value.value_tag_mask;

        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
        try testing.expectEqual(rejected_value, odd_alias_raw >> 1);
        try testing.expectEqual(rejected_value, (odd_alias_raw - xa_value.value_tag_mask) >> 1);
        try testing.expectEqual(err_ptr.fromErrorCode(err_ptr.toErrorCode(odd_alias_raw)), odd_alias_raw);
    }
}

test "top err_ptr neighbor pair still keeps the odd raw closed to xa_value" {
    const top_even_raw = err_ptr.fromErrorCode(-2);
    const top_odd_raw = err_ptr.fromErrorCode(-1);
    const reconstructed_value = top_odd_raw >> 1;

    try testing.expectEqual(top_even_raw + 1, top_odd_raw);
    try testing.expect(err_ptr.isErrValue(top_even_raw));
    try testing.expect(err_ptr.isErrValue(top_odd_raw));
    try testing.expect(!xa_value.isValue(top_even_raw));
    try testing.expect(!xa_value.isValue(top_odd_raw));
    try testing.expect(!xa_value.canRepresent(reconstructed_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(reconstructed_value));
    try testing.expectEqual(@as(isize, -2), err_ptr.toErrorCode(top_even_raw));
    try testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(top_odd_raw));
}
