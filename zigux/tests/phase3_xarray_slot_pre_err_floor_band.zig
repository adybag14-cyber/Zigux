const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "alternating raws below err floor keep value and pointer lanes split" {
    const previous_inline_raw = try xa_value.makeValue(xa_value.safe_inline_limit - 1);
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const first_pointer_gap_raw = err_ptr.err_floor - 3;
    const second_pointer_gap_raw = err_ptr.err_floor - 1;

    try testing.expectEqual(err_ptr.err_floor - 4, previous_inline_raw);
    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);
    try testing.expectEqual(previous_inline_raw + 1, first_pointer_gap_raw);
    try testing.expectEqual(first_pointer_gap_raw + 1, inline_limit_raw);
    try testing.expectEqual(inline_limit_raw + 1, second_pointer_gap_raw);
    try testing.expectEqual(second_pointer_gap_raw + 1, err_ptr.err_floor);

    const raws = [_]usize{
        previous_inline_raw,
        first_pointer_gap_raw,
        inline_limit_raw,
        second_pointer_gap_raw,
        err_ptr.err_floor,
    };
    const expected_kinds = [_]xarray_slot_view.SlotKind{
        .value,
        .pointer,
        .value,
        .pointer,
        .err,
    };
    const expected_values = [_]?usize{
        xa_value.safe_inline_limit - 1,
        null,
        xa_value.safe_inline_limit,
        null,
        null,
    };
    const expected_errors = [_]?isize{
        null,
        null,
        null,
        null,
        -4095,
    };

    for (raws, expected_kinds, expected_values, expected_errors) |raw, expected_kind, expected_value, expected_error| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(expected_kind, slot.kind());
        try testing.expectEqual(expected_value, slot.value());
        try testing.expectEqual(expected_error, slot.errorCode());
        try testing.expectEqual(raw, slot.rawValue());
    }

    try testing.expect(xarray_slot_view.isTaggedInternalEntry(previous_inline_raw));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(first_pointer_gap_raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(inline_limit_raw));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(second_pointer_gap_raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(err_ptr.err_floor));
}

test "constructors land on the same pre-floor band endpoints as raw classification" {
    const previous_inline_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit - 1);
    const inline_limit_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_gap_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 3);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-4095);

    try testing.expectEqual(err_ptr.err_floor - 4, previous_inline_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 3, pointer_gap_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor, err_floor_slot.rawValue());

    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit - 1), previous_inline_slot.value());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), inline_limit_slot.value());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 3), pointer_gap_slot.pointerValue());
    try testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());
}
