const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "null, inline zero, and first pointer gap stay disjoint" {
    const null_slot = xarray_slot_view.nullSlot();
    const inline_zero_raw = try xa_value.makeValue(0);
    const inline_zero = xarray_slot_view.fromRaw(inline_zero_raw);
    const pointer_gap_raw = inline_zero_raw + 1;
    const pointer_gap = xarray_slot_view.fromRaw(pointer_gap_raw);

    try std.testing.expectEqual(@as(usize, 0), null_slot.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.null, null_slot.kind());
    try std.testing.expect(!null_slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?usize, null), null_slot.value());
    try std.testing.expectEqual(@as(?isize, null), null_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), null_slot.pointerValue());

    try std.testing.expectEqual(@as(usize, 1), inline_zero_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, inline_zero.kind());
    try std.testing.expect(inline_zero.isTaggedEntry());
    try std.testing.expectEqual(@as(?usize, 0), inline_zero.value());
    try std.testing.expectEqual(@as(?isize, null), inline_zero.errorCode());
    try std.testing.expectEqual(@as(?usize, null), inline_zero.pointerValue());

    try std.testing.expectEqual(@as(usize, 2), pointer_gap_raw);
    try std.testing.expect(!err_ptr.isErrValue(pointer_gap_raw));
    try std.testing.expect(!xa_value.isValue(pointer_gap_raw));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap.kind());
    try std.testing.expect(!pointer_gap.isTaggedEntry());
    try std.testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), pointer_gap.value());
    try std.testing.expectEqual(@as(?isize, null), pointer_gap.errorCode());
}

test "low inline value ladder keeps pointer gaps and err boundary closed" {
    const inline_zero = try xarray_slot_view.fromValue(0);
    const first_gap = xarray_slot_view.fromPointer(inline_zero.rawValue() + 1);
    const inline_one = try xarray_slot_view.fromValue(1);
    const second_gap = xarray_slot_view.fromPointer(inline_one.rawValue() + 1);
    const err_floor = xarray_slot_view.fromRaw(err_ptr.err_floor);
    const before_err_floor = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);

    try std.testing.expectEqual(@as(?usize, 0), inline_zero.value());
    try std.testing.expectEqual(@as(?usize, inline_zero.rawValue() + 1), first_gap.pointerValue());
    try std.testing.expectEqual(@as(?usize, 1), inline_one.value());
    try std.testing.expectEqual(@as(?usize, inline_one.rawValue() + 1), second_gap.pointerValue());

    try std.testing.expectEqual(inline_zero.rawValue() + 2, inline_one.rawValue());
    try std.testing.expectEqual(first_gap.rawValue() + 2, second_gap.rawValue());
    try std.testing.expect(!first_gap.isTaggedEntry());
    try std.testing.expect(!second_gap.isTaggedEntry());
    try std.testing.expectEqual(@as(?usize, null), first_gap.value());
    try std.testing.expectEqual(@as(?isize, null), second_gap.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, before_err_floor.kind());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), before_err_floor.pointerValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, err_floor.kind());
    try std.testing.expectEqual(@as(?isize, -4095), err_floor.errorCode());
    try std.testing.expect(err_floor.isTaggedEntry());
}
