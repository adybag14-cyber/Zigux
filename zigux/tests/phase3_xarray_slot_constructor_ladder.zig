const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "constructor ladder keeps each lane ordered from null through err top" {
    const null_slot = xarray_slot_view.nullSlot();
    const inline_zero_slot = try xarray_slot_view.fromValue(0);
    const low_pointer_slot = xarray_slot_view.fromPointer(2);
    const inline_limit_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_gap_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const err_top_slot = xarray_slot_view.fromErrorCode(-1);

    const slots = [_]xarray_slot_view.SlotView{
        null_slot,
        inline_zero_slot,
        low_pointer_slot,
        inline_limit_slot,
        pointer_gap_slot,
        err_floor_slot,
        err_top_slot,
    };
    const expected_kinds = [_]xarray_slot_view.SlotKind{
        .null,
        .value,
        .pointer,
        .value,
        .pointer,
        .err,
        .err,
    };
    const expected_values = [_]?usize{
        null,
        0,
        null,
        xa_value.safe_inline_limit,
        null,
        null,
        null,
    };
    const expected_errors = [_]?isize{
        null,
        null,
        null,
        null,
        null,
        -4095,
        -1,
    };
    const expected_pointers = [_]?usize{
        null,
        null,
        2,
        null,
        err_ptr.err_floor - 1,
        null,
        null,
    };

    try testing.expectEqual(@as(usize, 0), slots[0].rawValue());
    try testing.expectEqual(@as(usize, 1), slots[1].rawValue());
    try testing.expectEqual(@as(usize, 2), slots[2].rawValue());
    try testing.expectEqual(err_ptr.err_floor - 2, slots[3].rawValue());
    try testing.expectEqual(err_ptr.err_floor - 1, slots[4].rawValue());
    try testing.expectEqual(err_ptr.err_floor, slots[5].rawValue());
    try testing.expectEqual(std.math.maxInt(usize), slots[6].rawValue());

    for (slots, 0..) |slot, idx| {
        try testing.expectEqual(expected_kinds[idx], slot.kind());
        try testing.expectEqual(slot.kind() == .null, slot.isNull());
        try testing.expectEqual(slot.kind() == .value, slot.isValue());
        try testing.expectEqual(slot.kind() == .pointer, slot.isPointer());
        try testing.expectEqual(slot.kind() == .err, slot.isErr());
        try testing.expectEqual(expected_values[idx], slot.value());
        try testing.expectEqual(expected_errors[idx], slot.errorCode());
        try testing.expectEqual(expected_pointers[idx], slot.pointerValue());
    }

    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(slots[0].rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(slots[1].rawValue()));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(slots[2].rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(slots[3].rawValue()));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(slots[4].rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(slots[5].rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(slots[6].rawValue()));
}

test "constructors bracket the cutoff without overlap or decoder drift" {
    const inline_limit_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_gap_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;

    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 1, pointer_gap_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor, err_floor_slot.rawValue());

    try testing.expectEqual(inline_limit_slot.rawValue() + 1, pointer_gap_slot.rawValue());
    try testing.expectEqual(pointer_gap_slot.rawValue() + 1, err_floor_slot.rawValue());

    try testing.expect(inline_limit_slot.isValue());
    try testing.expect(pointer_gap_slot.isPointer());
    try testing.expect(err_floor_slot.isErr());

    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), inline_limit_slot.value());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), pointer_gap_slot.pointerValue());
    try testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());

    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(overlapping_value));
    try testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try testing.expect(err_ptr.isErrValue(overlapping_raw));
    try testing.expect(!xa_value.isValue(overlapping_raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.err, xarray_slot_view.fromRaw(overlapping_raw).kind());
}
