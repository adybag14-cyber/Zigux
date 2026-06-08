const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectOnlyNull(slot: xarray_slot_view.SlotView) !void {
    try std.testing.expectEqual(xarray_slot_view.SlotKind.null, slot.kind());
    try std.testing.expect(slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(!slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

fn expectOnlyValue(slot: xarray_slot_view.SlotView, expected_value: usize) !void {
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(slot.isValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?usize, expected_value), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

fn expectOnlyPointer(slot: xarray_slot_view.SlotView, expected_raw: usize) !void {
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(slot.isPointer());
    try std.testing.expect(!slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, expected_raw), slot.pointerValue());
}

test "raw zero is the only null slot next to value and pointer lanes" {
    const zero = xarray_slot_view.fromRaw(0);
    const first_value_raw = try xa_value.makeValue(0);
    const first_value = xarray_slot_view.fromRaw(first_value_raw);
    const first_pointer = xarray_slot_view.fromRaw(2);

    try std.testing.expectEqual(@as(usize, 1), first_value_raw);
    try expectOnlyNull(zero);
    try expectOnlyValue(first_value, 0);
    try expectOnlyPointer(first_pointer, 2);

    try std.testing.expect(!err_ptr.isErrValue(zero.rawValue()));
    try std.testing.expect(!err_ptr.isErrValue(first_value.rawValue()));
    try std.testing.expect(!err_ptr.isErrValue(first_pointer.rawValue()));
}

test "public constructors reread the null boundary without lane bleed" {
    const null_slot = xarray_slot_view.nullSlot();
    const value_slot = try xarray_slot_view.fromValue(0);
    const pointer_slot = xarray_slot_view.fromPointer(2);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try expectOnlyNull(xarray_slot_view.fromRaw(null_slot.rawValue()));
    try expectOnlyValue(xarray_slot_view.fromRaw(value_slot.rawValue()), 0);
    try expectOnlyPointer(xarray_slot_view.fromRaw(pointer_slot.rawValue()), 2);

    const reread_err_floor = xarray_slot_view.fromRaw(err_floor_slot.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, reread_err_floor.kind());
    try std.testing.expect(reread_err_floor.isErr());
    try std.testing.expect(reread_err_floor.isTaggedEntry());
    try std.testing.expectEqual(@as(?isize, -4095), reread_err_floor.errorCode());
    try std.testing.expectEqual(@as(?usize, null), reread_err_floor.value());
    try std.testing.expectEqual(@as(?usize, null), reread_err_floor.pointerValue());
}
