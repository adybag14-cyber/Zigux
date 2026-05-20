const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "cutoff walk keeps value gap and first err entries in separate lanes" {
    const highest_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const first_err_raw = err_ptr.err_floor;
    const second_err_raw = err_ptr.err_floor + 1;

    const highest_value_slot = xarray_slot_view.fromRaw(highest_value_raw);
    const gap_slot = xarray_slot_view.fromRaw(gap_raw);
    const first_err_slot = xarray_slot_view.fromRaw(first_err_raw);
    const second_err_slot = xarray_slot_view.fromRaw(second_err_raw);

    try testing.expectEqual(err_ptr.err_floor - 2, highest_value_raw);
    try testing.expectEqual(highest_value_raw + 1, gap_raw);
    try testing.expectEqual(gap_raw + 1, first_err_raw);
    try testing.expectEqual(first_err_raw + 1, second_err_raw);

    try testing.expect(highest_value_slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), highest_value_slot.value());
    try testing.expect(!highest_value_slot.isPointer());
    try testing.expect(!highest_value_slot.isErr());

    try testing.expect(gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), gap_slot.value());
    try testing.expectEqual(@as(?isize, null), gap_slot.errorCode());

    try testing.expect(first_err_slot.isErr());
    try testing.expectEqual(@as(?isize, -4095), first_err_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), first_err_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), first_err_slot.value());

    try testing.expect(second_err_slot.isErr());
    try testing.expectEqual(@as(?isize, -4094), second_err_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), second_err_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), second_err_slot.value());
}

test "second rejected inline raw already lives in the err lane" {
    const overlapping_value = xa_value.safe_inline_limit + 2;
    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(overlapping_raw);

    try testing.expect(!xa_value.canRepresent(overlapping_value));
    try testing.expect(err_ptr.isErrValue(overlapping_raw));
    try testing.expect(!xa_value.isValue(overlapping_raw));
    try testing.expect(slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?isize, err_ptr.toErrorCode(overlapping_raw)), slot.errorCode());
}

test "pointer constructor accepts the one raw gap below err floor" {
    const raw = err_ptr.err_floor - 1;
    const slot = xarray_slot_view.fromPointer(raw);

    try testing.expect(slot.isPointer());
    try testing.expectEqual(raw, slot.rawValue());
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
}

test "top two err_ptr codes stay contiguous and closed to other decoders" {
    const penultimate = xarray_slot_view.fromErrorCode(-2);
    const top = xarray_slot_view.fromErrorCode(-1);

    try testing.expectEqual(penultimate.rawValue() + 1, top.rawValue());

    try testing.expect(penultimate.isErr());
    try testing.expectEqual(@as(?isize, -2), penultimate.errorCode());
    try testing.expectEqual(@as(?usize, null), penultimate.value());
    try testing.expectEqual(@as(?usize, null), penultimate.pointerValue());

    try testing.expect(top.isErr());
    try testing.expectEqual(@as(?isize, -1), top.errorCode());
    try testing.expectEqual(@as(?usize, null), top.value());
    try testing.expectEqual(@as(?usize, null), top.pointerValue());
}
