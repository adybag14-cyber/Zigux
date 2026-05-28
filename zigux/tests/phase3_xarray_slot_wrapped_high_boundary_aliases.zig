const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn projectedRaw(source_value: usize) usize {
    return (source_value << 1) | xa_value.value_tag_mask;
}

test "wrapped-high boundary aliases jump from highest value raw to err floor" {
    const wrap_base = @as(usize, 1) << (@bitSizeOf(usize) - 1);
    const highest_value_source = wrap_base + xa_value.safe_inline_limit;
    const first_err_source = highest_value_source + 1;

    const highest_value_raw = projectedRaw(highest_value_source);
    const first_err_raw = projectedRaw(first_err_source);

    const highest_value_slot = xarray_slot_view.fromRaw(highest_value_raw);
    const first_err_slot = xarray_slot_view.fromRaw(first_err_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(highest_value_source));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(first_err_source));

    try std.testing.expectEqual(err_ptr.err_floor - 2, highest_value_raw);
    try std.testing.expectEqual(err_ptr.err_floor, first_err_raw);
    try std.testing.expectEqual(highest_value_raw + 2, first_err_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, highest_value_slot.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), highest_value_slot.value());
    try std.testing.expectEqual(@as(?usize, null), highest_value_slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, null), highest_value_slot.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, first_err_slot.kind());
    try std.testing.expectEqual(@as(?usize, null), first_err_slot.value());
    try std.testing.expectEqual(@as(?usize, null), first_err_slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), first_err_slot.errorCode());
}

test "wrapped-high boundary aliases cannot project into the pointer gap" {
    const wrap_base = @as(usize, 1) << (@bitSizeOf(usize) - 1);
    const highest_value_source = wrap_base + xa_value.safe_inline_limit;
    const first_err_source = highest_value_source + 1;
    const pointer_gap_raw = err_ptr.err_floor - 1;

    const highest_value_raw = projectedRaw(highest_value_source);
    const first_err_raw = projectedRaw(first_err_source);

    try std.testing.expect(highest_value_raw < pointer_gap_raw);
    try std.testing.expect(pointer_gap_raw < first_err_raw);
    try std.testing.expectEqual(@as(usize, 2), first_err_raw - highest_value_raw);
    try std.testing.expect((highest_value_raw & 1) == 1);
    try std.testing.expect((first_err_raw & 1) == 1);

    const pointer_gap_slot = xarray_slot_view.fromPointer(pointer_gap_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap_slot.kind());
    try std.testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap_slot.pointerValue());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));
}

test "boundary raw extremes have one accepted constructor lane and one rejected family preimage" {
    const wrap_base = @as(usize, 1) << (@bitSizeOf(usize) - 1);
    const wrapped_value_source = wrap_base + xa_value.safe_inline_limit;
    const wrapped_err_source = wrapped_value_source + 1;

    const accepted_value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const accepted_err_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    const wrapped_value_raw = projectedRaw(wrapped_value_source);
    const wrapped_err_raw = projectedRaw(wrapped_err_source);

    try std.testing.expectEqual(accepted_value_slot.rawValue(), wrapped_value_raw);
    try std.testing.expectEqual(accepted_err_slot.rawValue(), wrapped_err_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(wrapped_value_source));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(wrapped_err_source));

    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), xarray_slot_view.fromRaw(wrapped_value_raw).value());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), xarray_slot_view.fromRaw(wrapped_err_raw).errorCode());
}
