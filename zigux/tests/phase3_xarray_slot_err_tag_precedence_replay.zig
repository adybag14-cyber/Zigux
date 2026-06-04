const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "odd err_ptr values keep error precedence over xa_value tagging" {
    const cases = [_]struct {
        code: isize,
        raw: usize,
    }{
        .{ .code = -1, .raw = err_ptr.fromErrorCode(-1) },
        .{ .code = -3, .raw = err_ptr.fromErrorCode(-3) },
        .{ .code = -4095, .raw = err_ptr.err_floor },
    };

    for (cases) |case| {
        try testing.expect((case.raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(case.raw));
        try testing.expect(!xa_value.isValue(case.raw));

        const slot = xarray_slot_view.fromRaw(case.raw);
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, case.code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
    }
}

test "safe inline top and err floor stay adjacent but decode into different lanes" {
    const value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const value_slot = xarray_slot_view.fromRaw(value_raw);
    const err_slot = xarray_slot_view.fromRaw(err_ptr.err_floor);

    try testing.expectEqual(err_ptr.err_floor - 2, value_raw);
    try testing.expectEqual(err_ptr.err_floor, value_raw + 2);
    try testing.expect(value_raw < err_ptr.err_floor);
    try testing.expect(xa_value.isValue(value_raw));
    try testing.expect(!err_ptr.isErrValue(value_raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try testing.expectEqual(@as(?isize, null), value_slot.errorCode());

    try testing.expect(err_ptr.isErrValue(err_slot.rawValue()));
    try testing.expect(!xa_value.isValue(err_slot.rawValue()));
    try testing.expectEqual(xarray_slot_view.SlotKind.err, err_slot.kind());
    try testing.expectEqual(@as(?isize, -4095), err_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), err_slot.value());
}

test "pointer gap between safe inline top and err floor cannot become tagged" {
    const pointer_raw = err_ptr.err_floor - 1;
    const pointer_slot = xarray_slot_view.fromRaw(pointer_raw);

    try testing.expect((pointer_raw & xa_value.value_tag_mask) == 0);
    try testing.expect(!err_ptr.isErrValue(pointer_raw));
    try testing.expect(!xa_value.isValue(pointer_raw));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
    try testing.expectEqual(@as(?usize, pointer_raw), pointer_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), pointer_slot.value());
    try testing.expectEqual(@as(?isize, null), pointer_slot.errorCode());
}

test "rejected overlapping inline value projects exactly onto err floor" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const projected_raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(projected_raw);

    try testing.expect(!xa_value.canRepresent(overlapping_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(overlapping_value));
    try testing.expectEqual(err_ptr.err_floor, projected_raw);
    try testing.expect(!xa_value.isValue(projected_raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try testing.expectEqual(@as(?isize, -4095), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.value());
}
