const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "first rejected xa_value constructor raw is decoded as the err floor" {
    const legal_value = xa_value.safe_inline_limit;
    const overlapping_value = legal_value + 1;

    const legal_slot = try xarray_slot_view.fromValue(legal_value);
    const legal_raw = legal_slot.rawValue();
    try std.testing.expectEqual(err_ptr.err_floor - 2, legal_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, legal_slot.kind());
    try std.testing.expectEqual(@as(?usize, legal_value), legal_slot.value());
    try std.testing.expectEqual(@as(?isize, null), legal_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), legal_slot.pointerValue());

    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    try std.testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(overlapping_value));

    const floor_slot = xarray_slot_view.fromRaw(overlapping_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, floor_slot.kind());
    try std.testing.expect(floor_slot.isTaggedEntry());
    try std.testing.expect(!floor_slot.isValue());
    try std.testing.expect(floor_slot.isErr());
    try std.testing.expect(!floor_slot.isPointer());
    try std.testing.expectEqual(@as(?isize, -4095), floor_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), floor_slot.value());
    try std.testing.expectEqual(@as(?usize, null), floor_slot.pointerValue());
}

test "raw neighbors around the rejected constructor remain in separate lanes" {
    const last_value_raw = err_ptr.err_floor - 2;
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const err_floor_raw = err_ptr.err_floor;
    const top_err_raw = err_ptr.fromErrorCode(-1);

    const last_value = xarray_slot_view.fromRaw(last_value_raw);
    const pointer_gap = xarray_slot_view.fromRaw(pointer_gap_raw);
    const err_floor = xarray_slot_view.fromRaw(err_floor_raw);
    const top_err = xarray_slot_view.fromRaw(top_err_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, last_value.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), last_value.value());
    try std.testing.expect(last_value.isTaggedEntry());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap.kind());
    try std.testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap.pointerValue());
    try std.testing.expect(!pointer_gap.isTaggedEntry());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, err_floor.kind());
    try std.testing.expectEqual(@as(?isize, -4095), err_floor.errorCode());
    try std.testing.expect(err_floor.isTaggedEntry());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, top_err.kind());
    try std.testing.expectEqual(@as(?isize, -1), top_err.errorCode());
    try std.testing.expect(top_err.isTaggedEntry());
}
