const std = @import("std");
const abi = @import("abi_bindings");

pub const max_errno: u32 = 4095;

pub fn fromErrno(errno_code: i32) usize {
    const signed: isize = @intCast(errno_code);
    return @bitCast(signed);
}

pub fn isErr(raw_addr: usize) bool {
    return raw_addr >= fromErrno(-@as(i32, @intCast(max_errno)));
}

pub fn isNull(raw_addr: usize) bool {
    return raw_addr == 0;
}

pub fn isNullOrErr(raw_addr: usize) bool {
    return isNull(raw_addr) or isErr(raw_addr);
}

pub fn toErrno(raw_addr: usize) i32 {
    const signed: isize = @bitCast(raw_addr);
    return @intCast(signed);
}

pub fn summarize(raw_addr: usize) abi.ErrPtrSummary {
    var summary = abi.ErrPtrSummary{
        .errno_code = 0,
        .flags = 0,
        .reserved = 0,
    };
    if (isErr(raw_addr)) {
        summary.errno_code = toErrno(raw_addr);
        summary.flags |= abi.ERR_PTR_FLAG_ERROR;
    }
    if (isNull(raw_addr)) {
        summary.flags |= abi.ERR_PTR_FLAG_NULL;
    }
    return summary;
}

test "phase3 err_ptr helpers stay bounded and predictable" {
    const err_addr = fromErrno(-22);
    const summary = summarize(err_addr);
    try std.testing.expect(isErr(err_addr));
    try std.testing.expect(!isNull(err_addr));
    try std.testing.expect(isNullOrErr(err_addr));
    try std.testing.expectEqual(@as(i32, -22), toErrno(err_addr));
    try std.testing.expectEqual(@as(i32, -22), summary.errno_code);
    try std.testing.expectEqual(@as(u16, abi.ERR_PTR_FLAG_ERROR), summary.flags);
}

test "phase3 err_ptr null sentinel stays explicit" {
    const summary = summarize(0);
    try std.testing.expect(!isErr(0));
    try std.testing.expect(isNull(0));
    try std.testing.expect(isNullOrErr(0));
    try std.testing.expectEqual(@as(u16, abi.ERR_PTR_FLAG_NULL), summary.flags);
}