const std = @import("std");

pub const max_errno: usize = 4095;
pub const err_floor: usize = @bitCast(-@as(isize, @intCast(max_errno)));
pub const value_tag_mask: usize = 0x1;
pub const safe_inline_limit: usize = (err_floor >> 1) - 1;

pub const EntryKind = enum {
    null,
    value,
    err,
    pointer,
};

pub const MakeValueError = error{
    ValueWouldOverlapErrPtr,
};

pub fn fromErrorCode(code: isize) usize {
    std.debug.assert(code <= -1);
    std.debug.assert(code >= -@as(isize, @intCast(max_errno)));
    return @bitCast(code);
}

pub fn isErrValue(raw: usize) bool {
    return raw >= err_floor;
}

pub fn toErrorCode(raw: usize) isize {
    std.debug.assert(isErrValue(raw));
    return @bitCast(raw);
}

pub fn canRepresentValue(value: usize) bool {
    return value <= safe_inline_limit;
}

pub fn makeValue(value: usize) MakeValueError!usize {
    if (!canRepresentValue(value)) {
        return error.ValueWouldOverlapErrPtr;
    }
    return (value << 1) | value_tag_mask;
}

pub fn isValue(raw: usize) bool {
    return (raw & value_tag_mask) == value_tag_mask and !isErrValue(raw);
}

pub fn toValue(raw: usize) usize {
    std.debug.assert(isValue(raw));
    return raw >> 1;
}

pub fn isTaggedInternalEntry(raw: usize) bool {
    return isErrValue(raw) or isValue(raw);
}

pub fn classify(raw: usize) EntryKind {
    if (raw == 0) {
        return .null;
    }
    if (isErrValue(raw)) {
        return .err;
    }
    if (isValue(raw)) {
        return .value;
    }
    return .pointer;
}

pub fn isPointerLike(raw: usize) bool {
    return classify(raw) == .pointer;
}

comptime {
    std.debug.assert(max_errno == 4095);
    std.debug.assert(isErrValue(err_floor));
    std.debug.assert(!isValue(err_floor));
    std.debug.assert(canRepresentValue(safe_inline_limit));
    std.debug.assert(!canRepresentValue(safe_inline_limit + 1));
}

test "uapi err_ptr/xarray helpers keep the tagged boundary explicit" {
    const err_raw = fromErrorCode(-22);
    const value_raw = try makeValue(29);

    try std.testing.expect(isErrValue(err_raw));
    try std.testing.expectEqual(@as(isize, -22), toErrorCode(err_raw));
    try std.testing.expectEqual(EntryKind.err, classify(err_raw));

    try std.testing.expect(isValue(value_raw));
    try std.testing.expectEqual(@as(usize, 29), toValue(value_raw));
    try std.testing.expectEqual(EntryKind.value, classify(value_raw));

    try std.testing.expectEqual(EntryKind.null, classify(0));
    try std.testing.expectEqual(EntryKind.pointer, classify(err_floor - 1));
    try std.testing.expect(isPointerLike(err_floor - 1));
    try std.testing.expect(!isTaggedInternalEntry(err_floor - 1));
}

test "uapi err_ptr/xarray helpers keep the top boundaries stable" {
    const err_top = fromErrorCode(-1);
    const inline_limit = try makeValue(safe_inline_limit);

    try std.testing.expect(isErrValue(err_top));
    try std.testing.expectEqual(@as(isize, -1), toErrorCode(err_top));
    try std.testing.expectEqual(EntryKind.err, classify(err_floor));
    try std.testing.expectEqual(EntryKind.value, classify(inline_limit));
    try std.testing.expectEqual(safe_inline_limit, toValue(inline_limit));
    try std.testing.expectEqual(err_floor, inline_limit + 2);
    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        makeValue(safe_inline_limit + 1),
    );
}
