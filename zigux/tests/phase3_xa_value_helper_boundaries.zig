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

test "first rejected inline value would alias err_ptr floor if it were encoded" {
    const overflow = xa_value.safe_inline_limit + 1;
    const aliased_raw = (overflow << 1) | xa_value.value_tag_mask;

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overflow));
    try testing.expectEqual(err_ptr.err_floor, aliased_raw);
    try testing.expect(err_ptr.isErrValue(aliased_raw));
    try testing.expect(!xa_value.isValue(aliased_raw));
    try testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(aliased_raw));
}

test "gap before err_ptr floor stays pointer-like and never decodes as xa_value" {
    const raw = err_ptr.err_floor - 1;

    try testing.expect(!err_ptr.isErrValue(raw));
    try testing.expect(!xa_value.isValue(raw));
    try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
}
