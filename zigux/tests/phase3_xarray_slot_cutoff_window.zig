const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "cutoff window keeps last value, pointer gap, and first err entries disjoint" {
    const last_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const first_err_raw = err_ptr.err_floor;
    const second_err_raw = err_ptr.err_floor + 1;

    const last_value_slot = xarray_slot_view.fromRaw(last_value_raw);
    const pointer_gap_slot = xarray_slot_view.fromRaw(pointer_gap_raw);
    const first_err_slot = xarray_slot_view.fromRaw(first_err_raw);
    const second_err_slot = xarray_slot_view.fromRaw(second_err_raw);

    try testing.expectEqual(err_ptr.err_floor - 2, last_value_raw);
    try testing.expectEqual(xarray_slot_view.SlotKind.value, last_value_slot.kind());
    try testing.expect(last_value_slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), last_value_slot.value());
    try testing.expectEqual(@as(?isize, null), last_value_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), last_value_slot.pointerValue());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(last_value_raw));

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap_slot.kind());
    try testing.expect(pointer_gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), pointer_gap_slot.value());
    try testing.expectEqual(@as(?isize, null), pointer_gap_slot.errorCode());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));

    try testing.expectEqual(xarray_slot_view.SlotKind.err, first_err_slot.kind());
    try testing.expect(first_err_slot.isErr());
    try testing.expectEqual(@as(?isize, -4095), first_err_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), first_err_slot.value());
    try testing.expectEqual(@as(?usize, null), first_err_slot.pointerValue());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(first_err_raw));

    try testing.expectEqual(xarray_slot_view.SlotKind.err, second_err_slot.kind());
    try testing.expect(second_err_slot.isErr());
    try testing.expectEqual(@as(?isize, -4094), second_err_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), second_err_slot.value());
    try testing.expectEqual(@as(?usize, null), second_err_slot.pointerValue());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(second_err_raw));
}

test "low-bit parity flips classification only when the err floor is crossed" {
    const last_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const first_err_raw = err_ptr.err_floor;
    const second_err_raw = err_ptr.err_floor + 1;

    try testing.expectEqual(@as(usize, 1), last_value_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), pointer_gap_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 1), first_err_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), second_err_raw & xa_value.value_tag_mask);

    try testing.expect(xa_value.isValue(last_value_raw));
    try testing.expect(!err_ptr.isErrValue(last_value_raw));

    try testing.expect(!xa_value.isValue(pointer_gap_raw));
    try testing.expect(!err_ptr.isErrValue(pointer_gap_raw));

    try testing.expect(!xa_value.isValue(first_err_raw));
    try testing.expect(err_ptr.isErrValue(first_err_raw));

    try testing.expect(!xa_value.isValue(second_err_raw));
    try testing.expect(err_ptr.isErrValue(second_err_raw));
}

test "first overlapping xa_value candidate aliases the err floor exactly" {
    const first_rejected_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (first_rejected_value << 1) | xa_value.value_tag_mask;
    const overlapping_slot = xarray_slot_view.fromRaw(overlapping_raw);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(first_rejected_value));
    try testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try testing.expectEqual(xarray_slot_view.SlotKind.err, overlapping_slot.kind());
    try testing.expectEqual(@as(?isize, -4095), overlapping_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), overlapping_slot.value());
    try testing.expectEqual(@as(?usize, null), overlapping_slot.pointerValue());
}
