const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xarray_slot_view = @import("xarray_slot_view");

const ErrorCase = struct {
    code: isize,
    next_code: ?isize = null,
};

fn expectErrorCase(case: ErrorCase) !void {
    const slot = xarray_slot_view.fromErrorCode(case.code);
    const decoded = xarray_slot_view.fromRaw(slot.rawValue());
    const rebuilt = xarray_slot_view.fromErrorCode(decoded.errorCode().?);

    try testing.expect(slot.isErr());
    try testing.expect(!slot.isNull());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?isize, case.code), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(slot.rawValue()));
    try testing.expect(err_ptr.isErrValue(slot.rawValue()));

    try testing.expect(decoded.isErr());
    try testing.expectEqual(slot.rawValue(), decoded.rawValue());
    try testing.expectEqual(@as(?isize, case.code), decoded.errorCode());
    try testing.expectEqual(@as(?usize, null), decoded.value());
    try testing.expectEqual(@as(?usize, null), decoded.pointerValue());

    try testing.expect(rebuilt.isErr());
    try testing.expectEqual(slot.rawValue(), rebuilt.rawValue());
    try testing.expectEqual(@as(?isize, case.code), rebuilt.errorCode());

    if (case.next_code) |next_code| {
        const next_slot = xarray_slot_view.fromErrorCode(next_code);
        try testing.expectEqual(slot.rawValue() + 1, next_slot.rawValue());
        try testing.expectEqual(case.code + 1, next_code);
    }
}

test "error-band replay keeps representative err_ptr raws tagged and closed to other lanes" {
    const cases = [_]ErrorCase{
        .{ .code = -4095, .next_code = -4094 },
        .{ .code = -2048, .next_code = -2047 },
        .{ .code = -1024, .next_code = -1023 },
        .{ .code = -22, .next_code = -21 },
        .{ .code = -2, .next_code = -1 },
        .{ .code = -1 },
    };

    try testing.expectEqual(err_ptr.err_floor, xarray_slot_view.fromErrorCode(-4095).rawValue());

    for (cases) |case| {
        try expectErrorCase(case);
    }
}

test "full err_ptr endpoints stay monotonic across the whole encoded band" {
    const bottom = xarray_slot_view.fromErrorCode(-4095);
    const top = xarray_slot_view.fromErrorCode(-1);

    try testing.expect(bottom.isErr());
    try testing.expect(top.isErr());
    try testing.expectEqual(err_ptr.err_floor, bottom.rawValue());
    try testing.expectEqual(err_ptr.fromErrorCode(-1), top.rawValue());
    try testing.expectEqual(@as(usize, err_ptr.max_errno - 1), top.rawValue() - bottom.rawValue());
    try testing.expectEqual(@as(?isize, -4095), bottom.errorCode());
    try testing.expectEqual(@as(?isize, -1), top.errorCode());
}
