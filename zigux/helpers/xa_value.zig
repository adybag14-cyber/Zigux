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
