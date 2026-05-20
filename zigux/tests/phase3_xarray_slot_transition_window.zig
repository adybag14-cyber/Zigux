const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "xarray slot transition window keeps value pointer and err lanes ordered" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const err_floor_raw = err_ptr.err_floor;
    const second_rejected_raw = err_floor_raw + 2;

    const inline_limit_slot = xarray_slot_view.fromRaw(inline_limit_raw);
    const pointer_gap_slot = xarray_slot_view.fromRaw(pointer_gap_raw);
    const err_floor_slot = xarray_slot_view.fromRaw(err_floor_raw);
    const second_rejected_slot = xarray_slot_view.fromRaw(second_rejected_raw);

    try testing.expectEqual(xarray_slot_view.SlotKind.value, inline_limit_slot.kind());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), inline_limit_slot.value());

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap_slot.kind());
    try testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap_slot.pointerValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.err, err_floor_slot.kind());
    try testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());

    try testing.expectEqual(xarray_slot_view.SlotKind.err, second_rejected_slot.kind());
    try testing.expectEqual(@as(?isize, -4093), second_rejected_slot.errorCode());
}

test "rejected xa_value raws stay tagged and keep value and pointer decoders closed" {
    const first_rejected_raw = err_ptr.err_floor;
    const second_rejected_raw = err_ptr.err_floor + 2;

    const first_rejected_slot = xarray_slot_view.fromRaw(first_rejected_raw);
    const second_rejected_slot = xarray_slot_view.fromRaw(second_rejected_raw);

    try testing.expect(!xa_value.canRepresent(xa_value.safe_inline_limit + 1));
    try testing.expect(!xa_value.canRepresent(xa_value.safe_inline_limit + 2));

    try testing.expect(xarray_slot_view.isTaggedInternalEntry(first_rejected_raw));
    try testing.expect(first_rejected_slot.isErr());
    try testing.expect(!first_rejected_slot.isValue());
    try testing.expect(!first_rejected_slot.isPointer());
    try testing.expectEqual(@as(?usize, null), first_rejected_slot.value());
    try testing.expectEqual(@as(?usize, null), first_rejected_slot.pointerValue());

    try testing.expect(xarray_slot_view.isTaggedInternalEntry(second_rejected_raw));
    try testing.expect(second_rejected_slot.isErr());
    try testing.expect(!second_rejected_slot.isValue());
    try testing.expect(!second_rejected_slot.isPointer());
    try testing.expectEqual(@as(?usize, null), second_rejected_slot.value());
    try testing.expectEqual(@as(?usize, null), second_rejected_slot.pointerValue());
}

test "constructor and raw paths agree for representative xarray slot lanes" {
    const value_slot = try xarray_slot_view.fromValue(7);
    const err_slot = xarray_slot_view.fromErrorCode(-12);
    const pointer_slot = xarray_slot_view.fromPointer(0x1000);

    try testing.expectEqual(
        xarray_slot_view.SlotKind.value,
        xarray_slot_view.fromRaw(value_slot.rawValue()).kind(),
    );
    try testing.expectEqual(
        xarray_slot_view.SlotKind.err,
        xarray_slot_view.fromRaw(err_slot.rawValue()).kind(),
    );
    try testing.expectEqual(
        xarray_slot_view.SlotKind.pointer,
        xarray_slot_view.fromRaw(pointer_slot.rawValue()).kind(),
    );

    try testing.expectEqual(@as(?usize, 7), xarray_slot_view.fromRaw(value_slot.rawValue()).value());
    try testing.expectEqual(@as(?isize, -12), xarray_slot_view.fromRaw(err_slot.rawValue()).errorCode());
    try testing.expectEqual(@as(?usize, 0x1000), xarray_slot_view.fromRaw(pointer_slot.rawValue()).pointerValue());
}
