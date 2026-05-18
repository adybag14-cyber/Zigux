const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

test "err_ptr encodes the Linux error band as a tagged pointer-sized value" {
    const raw = err_ptr.fromErrorCode(-22);

    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expectEqual(@as(isize, -22), err_ptr.toErrorCode(raw));
    try testing.expectEqual(err_ptr.err_floor, err_ptr.fromErrorCode(-4095));
    try testing.expect(err_ptr.isOkValue(err_ptr.err_floor - 1));
}

test "top err_ptr encoding stays in the error band even with the xa_value tag bit set" {
    const raw = err_ptr.fromErrorCode(-1);

    try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(raw));
    try testing.expect(!xa_value.isValue(raw));
}

test "xa_value round-trips a bounded inline value without entering the err_ptr band" {
    const raw = try xa_value.makeValue(29);

    try testing.expect(xa_value.isValue(raw));
    try testing.expect(!err_ptr.isErrValue(raw));
    try testing.expectEqual(@as(usize, 29), xa_value.toValue(raw));
}

test "xa_value rejects inline values that would overlap err_ptr encodings" {
    try testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xa_value.makeValue(xa_value.safe_inline_limit + 1),
    );
}

test "safe inline limit stays the highest tagged value below the err_ptr floor" {
    const raw = try xa_value.makeValue(xa_value.safe_inline_limit);

    try testing.expect(xa_value.isValue(raw));
    try testing.expectEqual(xa_value.safe_inline_limit, xa_value.toValue(raw));
    try testing.expectEqual(err_ptr.err_floor, raw + 2);
}
