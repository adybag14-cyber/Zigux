const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "cutoff strip keeps value pointer and err lanes contiguous" {
    const last_value = xa_value.safe_inline_limit;
    const previous_value = last_value - 1;
    const raws = [_]usize{
        try xa_value.makeValue(previous_value),
        try xa_value.makeValue(last_value),
        err_ptr.err_floor - 1,
        err_ptr.err_floor,
        err_ptr.err_floor + 1,
    };
    const expected_kinds = [_]xarray_slot_view.SlotKind{
        .value,
        .value,
        .pointer,
        .err,
        .err,
    };
    const expected_values = [_]?usize{
        previous_value,
        last_value,
        null,
        null,
        null,
    };
    const expected_errors = [_]?isize{
        null,
        null,
        null,
        -4095,
        -4094,
    };

    const expected_deltas = [_]usize{ 2, 1, 1, 1 };

    for (expected_deltas, 0..) |delta, idx| {
        try testing.expectEqual(raws[idx] + delta, raws[idx + 1]);
    }

    for (raws, expected_kinds, expected_values, expected_errors) |raw, expected_kind, expected_value, expected_error| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(expected_kind, slot.kind());
        try testing.expectEqual(raw, slot.rawValue());
        try testing.expectEqual(expected_value, slot.value());
        try testing.expectEqual(expected_error, slot.errorCode());
    }

    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raws[0]));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raws[1]));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raws[2]));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raws[3]));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raws[4]));
}

test "constructors stay on their owning side of the pointer gap" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_gap_slot = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);
    const err_slot = xarray_slot_view.fromErrorCode(-4095);

    try testing.expectEqual(err_ptr.err_floor - 2, value_slot.rawValue());
    try testing.expect(value_slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());

    try testing.expectEqual(err_ptr.err_floor - 1, pointer_gap_slot.rawValue());
    try testing.expect(pointer_gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), pointer_gap_slot.pointerValue());

    try testing.expectEqual(err_ptr.err_floor, err_slot.rawValue());
    try testing.expect(err_slot.isErr());
    try testing.expectEqual(@as(?isize, -4095), err_slot.errorCode());

    try testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1),
    );
}
