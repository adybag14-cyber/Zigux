const std = @import("std");
const uapi = @import("uapi_err_ptr_xarray");

pub const max_errno = uapi.max_errno;
pub const err_floor = uapi.err_floor;
pub const value_tag_mask = uapi.value_tag_mask;
pub const safe_inline_limit = uapi.safe_inline_limit;

pub const EntryKind = uapi.EntryKind;
pub const MakeValueError = uapi.MakeValueError;

pub fn fromErrorCode(code: isize) usize {
    return uapi.fromErrorCode(code);
}

pub fn isErrValue(raw: usize) bool {
    return uapi.isErrValue(raw);
}

pub fn toErrorCode(raw: usize) isize {
    return uapi.toErrorCode(raw);
}

pub fn canRepresentValue(value: usize) bool {
    return uapi.canRepresentValue(value);
}

pub fn makeValue(value: usize) MakeValueError!usize {
    return uapi.makeValue(value);
}

pub fn isValue(raw: usize) bool {
    return uapi.isValue(raw);
}

pub fn toValue(raw: usize) usize {
    return uapi.toValue(raw);
}

pub fn isTaggedInternalEntry(raw: usize) bool {
    return uapi.isTaggedInternalEntry(raw);
}

pub fn classify(raw: usize) EntryKind {
    return uapi.classify(raw);
}

pub fn isPointerLike(raw: usize) bool {
    return uapi.isPointerLike(raw);
}

comptime {
    std.debug.assert(max_errno == uapi.max_errno);
    std.debug.assert(err_floor == uapi.err_floor);
    std.debug.assert(value_tag_mask == uapi.value_tag_mask);
    std.debug.assert(safe_inline_limit == uapi.safe_inline_limit);
}

test "binding stays aligned with the published uapi constants" {
    try std.testing.expectEqual(uapi.max_errno, max_errno);
    try std.testing.expectEqual(uapi.err_floor, err_floor);
    try std.testing.expectEqual(uapi.value_tag_mask, value_tag_mask);
    try std.testing.expectEqual(uapi.safe_inline_limit, safe_inline_limit);
    try std.testing.expectEqual(uapi.fromErrorCode(-22), fromErrorCode(-22));
    try std.testing.expectEqual(uapi.fromErrorCode(-1), fromErrorCode(-1));
}

test "binding mirrors the published value tagging behavior" {
    const zero_raw = try makeValue(0);
    const sample_raw = try makeValue(29);
    const limit_raw = try makeValue(safe_inline_limit);

    try std.testing.expectEqual(try uapi.makeValue(0), zero_raw);
    try std.testing.expectEqual(try uapi.makeValue(29), sample_raw);
    try std.testing.expectEqual(try uapi.makeValue(uapi.safe_inline_limit), limit_raw);
    try std.testing.expectEqual(uapi.toValue(sample_raw), toValue(sample_raw));
    try std.testing.expect(isValue(zero_raw));
    try std.testing.expectEqual(EntryKind.value, classify(sample_raw));
    try std.testing.expectEqual(err_floor, limit_raw + 2);
    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        makeValue(safe_inline_limit + 1),
    );
}

test "binding classification keeps null, err, value, and pointer-like lanes explicit" {
    try std.testing.expectEqual(EntryKind.null, classify(0));
    try std.testing.expectEqual(EntryKind.pointer, classify(err_floor - 1));
    try std.testing.expect(isPointerLike(err_floor - 1));
    try std.testing.expect(!isTaggedInternalEntry(err_floor - 1));

    const err_raw = fromErrorCode(-4095);
    const value_raw = try makeValue(7);

    try std.testing.expectEqual(EntryKind.err, classify(err_raw));
    try std.testing.expectEqual(@as(isize, -4095), toErrorCode(err_raw));
    try std.testing.expectEqual(EntryKind.value, classify(value_raw));
    try std.testing.expectEqual(@as(usize, 7), toValue(value_raw));
    try std.testing.expect(isTaggedInternalEntry(err_raw));
    try std.testing.expect(isTaggedInternalEntry(value_raw));
}
