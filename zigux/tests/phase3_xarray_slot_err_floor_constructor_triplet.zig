const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "constructors meet on the three raw values around err_floor" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try std.testing.expectEqual(err_ptr.err_floor - 2, value_slot.rawValue());
    try std.testing.expectEqual(err_ptr.err_floor - 1, pointer_slot.rawValue());
    try std.testing.expectEqual(err_ptr.err_floor, err_slot.rawValue());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, err_slot.kind());
}

test "err_floor triplet keeps decoded payloads lane-specific" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try std.testing.expectEqual(@as(?usize, null), value_slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, null), value_slot.errorCode());

    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), pointer_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), pointer_slot.value());
    try std.testing.expectEqual(@as(?isize, null), pointer_slot.errorCode());

    try std.testing.expectEqual(@as(?isize, -4095), err_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), err_slot.value());
    try std.testing.expectEqual(@as(?usize, null), err_slot.pointerValue());
}

test "tagged classification flips only at the pointer gap" {
    const value_raw = (try xarray_slot_view.fromValue(xa_value.safe_inline_limit)).rawValue();
    const pointer_raw = (xarray_slot_view.fromPointer(err_ptr.err_floor - 1)).rawValue();
    const err_raw = (xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)))).rawValue();

    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(value_raw));
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(err_raw));

    try std.testing.expectEqual(value_raw + 1, pointer_raw);
    try std.testing.expectEqual(pointer_raw + 1, err_raw);
}
