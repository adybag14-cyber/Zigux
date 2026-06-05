const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn rejectedValueRaw(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

fn expectErrOkComplement(raw: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(err_ptr.isErrValue(raw), slot.isErr());
    try std.testing.expectEqual(!slot.isErr(), err_ptr.isOkValue(raw));
    try std.testing.expectEqual(err_ptr.isOkValue(raw), slot.errorCode() == null);
}

test "err_ptr ok complement matches every non-error xarray slot lane" {
    const cases = [_]usize{
        xarray_slot_view.nullSlot().rawValue(),
        (try xarray_slot_view.fromValue(0)).rawValue(),
        (try xarray_slot_view.fromValue(42)).rawValue(),
        (try xarray_slot_view.fromValue(xa_value.safe_inline_limit)).rawValue(),
        err_ptr.err_floor - 1,
        xarray_slot_view.fromPointer(0x1000).rawValue(),
        xarray_slot_view.fromPointer(0x2000).rawValue(),
    };

    for (cases) |raw| {
        try expectErrOkComplement(raw);
        try std.testing.expect(err_ptr.isOkValue(raw));
        try std.testing.expect(!xarray_slot_view.fromRaw(raw).isErr());
    }
}

test "err_ptr ok complement closes across direct error slots" {
    const cases = [_]usize{
        err_ptr.err_floor,
        err_ptr.err_floor + 1,
        err_ptr.fromErrorCode(-4094),
        err_ptr.fromErrorCode(-256),
        err_ptr.fromErrorCode(-22),
        err_ptr.fromErrorCode(-1),
    };

    for (cases) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);

        try expectErrOkComplement(raw);
        try std.testing.expect(!err_ptr.isOkValue(raw));
        try std.testing.expect(slot.isErr());
        try std.testing.expectEqual(err_ptr.toErrorCode(raw), slot.errorCode().?);
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "rejected xa_value aliases inherit the err_ptr ok complement" {
    const aliases = [_]struct {
        rejected_value: usize,
        code: isize,
    }{
        .{ .rejected_value = xa_value.safe_inline_limit + 1, .code = -4095 },
        .{ .rejected_value = xa_value.safe_inline_limit + 2, .code = -4093 },
        .{ .rejected_value = xa_value.safe_inline_limit + 65, .code = -3967 },
        .{ .rejected_value = xa_value.safe_inline_limit + 2048, .code = -1 },
    };

    for (aliases) |case| {
        const raw = rejectedValueRaw(case.rejected_value);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expect(!xa_value.canRepresent(case.rejected_value));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(case.rejected_value));
        try std.testing.expectEqual(err_ptr.fromErrorCode(case.code), raw);
        try expectErrOkComplement(raw);
        try std.testing.expect(!err_ptr.isOkValue(raw));
        try std.testing.expect(slot.isErr());
        try std.testing.expectEqual(@as(?isize, case.code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}
