const std = @import("std");
const err_ptr = @import("err_ptr");

pub const value_tag_mask: usize = 0x1;
pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;

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
    return (raw & value_tag_mask) == value_tag_mask and !err_ptr.isErrValue(raw);
}

pub fn toValue(raw: usize) usize {
    std.debug.assert(isValue(raw));
    return raw >> 1;
}

comptime {
    std.debug.assert(isValue(1));
    std.debug.assert(!isValue(err_ptr.err_floor));
    std.debug.assert(canRepresent(safe_inline_limit));
    std.debug.assert(!canRepresent(safe_inline_limit + 1));
}

test "inline zero is representable and round-trips as an xa_value" {
    const raw = try makeValue(0);

    try std.testing.expectEqual(value_tag_mask, raw);
    try std.testing.expect(isValue(raw));
    try std.testing.expectEqual(@as(usize, 0), toValue(raw));
}

test "err_ptr encodings with the low tag bit set never classify as xa_values" {
    const raw = err_ptr.fromErrorCode(-1);

    try std.testing.expect((raw & value_tag_mask) == value_tag_mask);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!isValue(raw));
}

test "xa_value cutoff stays ordered as inline value, pointer gap, then err_ptr" {
    const inline_raw = try makeValue(safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const err_raw = err_ptr.err_floor;

    try std.testing.expectEqual(err_ptr.err_floor - 2, inline_raw);
    try std.testing.expect(isValue(inline_raw));
    try std.testing.expectEqual(safe_inline_limit, toValue(inline_raw));

    try std.testing.expect(!isValue(pointer_gap_raw));
    try std.testing.expect(err_ptr.isOkValue(pointer_gap_raw));
    try std.testing.expect((pointer_gap_raw & value_tag_mask) == 0);

    try std.testing.expect(!isValue(err_raw));
    try std.testing.expect(err_ptr.isErrValue(err_raw));
    try std.testing.expect((err_raw & value_tag_mask) == value_tag_mask);
}

test "first rejected inline value would alias err_ptr floor" {
    const rejected_value = safe_inline_limit + 1;
    const overlapping_raw = (rejected_value << 1) | value_tag_mask;

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, makeValue(rejected_value));
    try std.testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try std.testing.expect(err_ptr.isErrValue(overlapping_raw));
    try std.testing.expect(!isValue(overlapping_raw));
}
