const std = @import("std");
const err_ptr = @import("err_ptr");

pub const value_tag_mask: usize = 0x1;
pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;

pub const MakeValueError = error{
    ValueWouldOverlapErrPtr,
};

pub const RejectedEncoding = enum {
    alias_err_ptr,
    wrap_low_value,
};

fn uncheckedRaw(value: usize) usize {
    return (value *% 2) | value_tag_mask;
}

pub fn canRepresent(value: usize) bool {
    return value <= safe_inline_limit;
}

pub fn classifyRejectedEncoding(value: usize) ?RejectedEncoding {
    if (canRepresent(value)) {
        return null;
    }
    return if (err_ptr.isErrValue(uncheckedRaw(value))) .alias_err_ptr else .wrap_low_value;
}

pub fn makeValue(value: usize) MakeValueError!usize {
    if (!canRepresent(value)) {
        return error.ValueWouldOverlapErrPtr;
    }
    return uncheckedRaw(value);
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

test "first rejected inline value aliases the err_ptr floor" {
    const overlapping_value = safe_inline_limit + 1;
    const raw = uncheckedRaw(overlapping_value);

    try std.testing.expect(!canRepresent(overlapping_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, makeValue(overlapping_value));
    try std.testing.expectEqual(err_ptr.err_floor, raw);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!isValue(raw));
}

test "rejected inline values distinguish err-band aliases from wrapped low values" {
    const first_alias_value = safe_inline_limit + 1;
    const last_alias_value = std.math.maxInt(usize) >> 1;
    const first_wrap_value = last_alias_value + 1;
    const second_wrap_value = last_alias_value + 2;

    try std.testing.expectEqual(
        RejectedEncoding.alias_err_ptr,
        classifyRejectedEncoding(first_alias_value).?,
    );
    try std.testing.expectEqual(
        RejectedEncoding.alias_err_ptr,
        classifyRejectedEncoding(last_alias_value).?,
    );
    try std.testing.expectEqual(err_ptr.fromErrorCode(-1), uncheckedRaw(last_alias_value));

    try std.testing.expectEqual(
        RejectedEncoding.wrap_low_value,
        classifyRejectedEncoding(first_wrap_value).?,
    );
    try std.testing.expectEqual(
        RejectedEncoding.wrap_low_value,
        classifyRejectedEncoding(second_wrap_value).?,
    );
    try std.testing.expectEqual(@as(usize, 1), uncheckedRaw(first_wrap_value));
    try std.testing.expectEqual(@as(usize, 3), uncheckedRaw(second_wrap_value));
    try std.testing.expect(isValue(uncheckedRaw(first_wrap_value)));
    try std.testing.expect(isValue(uncheckedRaw(second_wrap_value)));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, makeValue(first_wrap_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, makeValue(second_wrap_value));
}

test "representable values do not classify as rejected encodings" {
    try std.testing.expectEqual(@as(?RejectedEncoding, null), classifyRejectedEncoding(0));
    try std.testing.expectEqual(
        @as(?RejectedEncoding, null),
        classifyRejectedEncoding(safe_inline_limit),
    );
}
