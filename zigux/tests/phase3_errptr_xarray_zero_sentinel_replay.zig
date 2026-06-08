const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectNullSlot(slot: xarray_slot_view.SlotView) !void {
    try std.testing.expectEqual(xarray_slot_view.SlotKind.null, slot.kind());
    try std.testing.expect(slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(!slot.isTaggedEntry());
    try std.testing.expectEqual(@as(usize, 0), slot.rawValue());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "raw zero is the only null sentinel across err_ptr and xarray views" {
    try std.testing.expect(err_ptr.isOkValue(0));
    try std.testing.expect(!err_ptr.isErrValue(0));
    try std.testing.expect(!xa_value.isValue(0));
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(0));

    try expectNullSlot(xarray_slot_view.fromRaw(0));
    try expectNullSlot(xarray_slot_view.nullSlot());

    const inline_zero_raw = try xa_value.makeValue(0);
    const inline_zero_slot = try xarray_slot_view.fromValue(0);
    try std.testing.expectEqual(@as(usize, 1), inline_zero_raw);
    try std.testing.expectEqual(inline_zero_raw, inline_zero_slot.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, inline_zero_slot.kind());
    try std.testing.expect(!inline_zero_slot.isNull());
    try std.testing.expect(inline_zero_slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?usize, 0), inline_zero_slot.value());
    try std.testing.expectEqual(@as(?isize, null), inline_zero_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), inline_zero_slot.pointerValue());
}

test "zero neighbors do not borrow the null lane" {
    const first_value = xarray_slot_view.fromRaw(1);
    const first_pointer = xarray_slot_view.fromRaw(2);
    const err_top = xarray_slot_view.fromErrorCode(-1);
    const err_floor = xarray_slot_view.fromRaw(err_ptr.err_floor);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, first_value.kind());
    try std.testing.expectEqual(@as(?usize, 0), first_value.value());
    try std.testing.expect(!first_value.isNull());
    try std.testing.expect(first_value.isTaggedEntry());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, first_pointer.kind());
    try std.testing.expectEqual(@as(?usize, 2), first_pointer.pointerValue());
    try std.testing.expect(!first_pointer.isNull());
    try std.testing.expect(!first_pointer.isTaggedEntry());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, err_top.kind());
    try std.testing.expectEqual(@as(?isize, -1), err_top.errorCode());
    try std.testing.expect(!err_top.isNull());
    try std.testing.expect(err_top.isTaggedEntry());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, err_floor.kind());
    try std.testing.expectEqual(@as(?isize, -4095), err_floor.errorCode());
    try std.testing.expect(!err_floor.isNull());
    try std.testing.expect(err_floor.isTaggedEntry());
}
