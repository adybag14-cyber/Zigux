const std = @import("std");
const err_ptr_abi = @import("err_ptr_abi.zig");

pub const value_tag_mask: usize = 0x1;
pub const safe_inline_limit: usize = (err_ptr_abi.err_floor >> 1) - 1;

pub const MakeValueError = error{
    ValueWouldOverlapErrPtr,
};

pub fn canRepresent(value: usize) bool {
    return value <= safe_inline_limit;
}

pub fn makeValue(value: usize) MakeValueError!usize {
    if (!canRepresent(value)) {
        return error.ValueWouldOverlapErrPtr;
    }
    return (value << 1) | value_tag_mask;
}

pub fn isValue(raw: usize) bool {
    return (raw & value_tag_mask) == value_tag_mask and !err_ptr_abi.isErrValue(raw);
}

pub fn toValue(raw: usize) usize {
    std.debug.assert(isValue(raw));
    return raw >> 1;
}

test "xa_value ABI stays below the err_ptr floor" {
    const zero = try makeValue(0);
    const top = try makeValue(safe_inline_limit);
    const overlap = safe_inline_limit + 1;

    try std.testing.expectEqual(value_tag_mask, zero);
    try std.testing.expect(isValue(zero));
    try std.testing.expectEqual(@as(usize, 0), toValue(zero));

    try std.testing.expect(canRepresent(safe_inline_limit));
    try std.testing.expect(isValue(top));
    try std.testing.expectEqual(safe_inline_limit, toValue(top));
    try std.testing.expectEqual(err_ptr_abi.err_floor - 2, top);

    try std.testing.expect(!canRepresent(overlap));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, makeValue(overlap));
    try std.testing.expect(!isValue(err_ptr_abi.err_floor));
}
