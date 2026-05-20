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

test "highest representable inline value stays below the err_ptr floor" {
    const raw = try makeValue(safe_inline_limit);

    try std.testing.expect(canRepresent(safe_inline_limit));
    try std.testing.expect(isValue(raw));
    try std.testing.expectEqual(safe_inline_limit, toValue(raw));
    try std.testing.expect(raw < err_ptr.err_floor);
    try std.testing.expectEqual(err_ptr.err_floor - 2, raw);
}

test "highest two tagged xa_values stay contiguous below the pointer gap" {
    const next_highest_value = safe_inline_limit - 1;
    const next_highest_raw = try makeValue(next_highest_value);
    const highest_raw = try makeValue(safe_inline_limit);

    try std.testing.expect(canRepresent(next_highest_value));
    try std.testing.expect(isValue(next_highest_raw));
    try std.testing.expectEqual(next_highest_value, toValue(next_highest_raw));
    try std.testing.expectEqual(err_ptr.err_floor - 4, next_highest_raw);
    try std.testing.expectEqual(next_highest_raw + 2, highest_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, highest_raw + 1);
    try std.testing.expect(!err_ptr.isErrValue(next_highest_raw));
}

test "first rejected inline value aliases the err_ptr floor" {
    const overlapping_value = safe_inline_limit + 1;
    const raw = (overlapping_value << 1) | value_tag_mask;

    try std.testing.expect(!canRepresent(overlapping_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, makeValue(overlapping_value));
    try std.testing.expectEqual(err_ptr.err_floor, raw);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!isValue(raw));
}

test "second rejected inline value skips the first err_ptr raw and lands on the next tagged error" {
    const overlapping_value = safe_inline_limit + 2;
    const raw = (overlapping_value << 1) | value_tag_mask;

    try std.testing.expect(!canRepresent(overlapping_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, makeValue(overlapping_value));
    try std.testing.expectEqual(err_ptr.err_floor + 2, raw);
    try std.testing.expectEqual(err_ptr.fromErrorCode(-4093), raw);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!isValue(raw));
}
