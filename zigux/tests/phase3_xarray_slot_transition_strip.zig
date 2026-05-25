const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "transition strip stays value value pointer err err across the err floor seam" {
    const raws = [_]usize{
        try xa_value.makeValue(xa_value.safe_inline_limit - 1),
        try xa_value.makeValue(xa_value.safe_inline_limit),
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

    for (raws, expected_kinds) |raw, expected_kind| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(expected_kind, slot.kind());
    }

    try testing.expectEqual(err_ptr.err_floor - 4, raws[0]);
    try testing.expectEqual(err_ptr.err_floor - 2, raws[1]);
    try testing.expectEqual(err_ptr.err_floor - 1, raws[2]);
}

test "transition strip preserves decoders and tagged-entry ownership" {
    const low_value = xarray_slot_view.fromRaw(try xa_value.makeValue(xa_value.safe_inline_limit - 1));
    const top_value = xarray_slot_view.fromRaw(try xa_value.makeValue(xa_value.safe_inline_limit));
    const gap = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);
    const first_err = xarray_slot_view.fromRaw(err_ptr.err_floor);
    const second_err = xarray_slot_view.fromRaw(err_ptr.err_floor + 1);

    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit - 1), low_value.value());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), top_value.value());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), gap.pointerValue());
    try testing.expectEqual(@as(?isize, -4095), first_err.errorCode());
    try testing.expectEqual(@as(?isize, -4094), second_err.errorCode());

    try testing.expect(xarray_slot_view.isTaggedInternalEntry(low_value.rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(top_value.rawValue()));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap.rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(first_err.rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(second_err.rawValue()));
}

test "transition strip rebuilds through public constructors without raw drift" {
    const low_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit - 1);
    const top_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const gap = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const first_err = xarray_slot_view.fromErrorCode(-4095);
    const second_err = xarray_slot_view.fromErrorCode(-4094);

    try testing.expectEqual(err_ptr.err_floor - 4, low_value.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 2, top_value.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 1, gap.rawValue());
    try testing.expectEqual(err_ptr.err_floor, first_err.rawValue());
    try testing.expectEqual(err_ptr.err_floor + 1, second_err.rawValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.value, low_value.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.value, top_value.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, first_err.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, second_err.kind());
}
