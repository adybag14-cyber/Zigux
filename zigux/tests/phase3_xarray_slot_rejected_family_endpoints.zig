const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn projectedRaw(source_value: usize) usize {
    return (source_value << 1) | xa_value.value_tag_mask;
}

test "direct rejected family endpoints cover the full odd err band" {
    const first_source = xa_value.safe_inline_limit + 1;
    const last_source = (@as(usize, 1) << (@bitSizeOf(usize) - 1)) - 1;

    const first_raw = projectedRaw(first_source);
    const last_raw = projectedRaw(last_source);

    const first_slot = xarray_slot_view.fromRaw(first_raw);
    const last_slot = xarray_slot_view.fromRaw(last_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(first_source));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(last_source));

    try std.testing.expectEqual(err_ptr.err_floor, first_raw);
    try std.testing.expectEqual(err_ptr.fromErrorCode(-1), last_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, first_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, last_slot.kind());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), first_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, -1), last_slot.errorCode());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(first_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(last_raw));
}

test "wrapped-high rejected family endpoints split between low value and top err raw" {
    const wrap_base = @as(usize, 1) << (@bitSizeOf(usize) - 1);
    const low_source = wrap_base;
    const high_source = std.math.maxInt(usize);

    const low_raw = projectedRaw(low_source);
    const high_raw = projectedRaw(high_source);

    const low_slot = xarray_slot_view.fromRaw(low_raw);
    const high_slot = xarray_slot_view.fromRaw(high_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(low_source));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(high_source));

    try std.testing.expectEqual(@as(usize, 1), low_raw);
    try std.testing.expectEqual(err_ptr.fromErrorCode(-1), high_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, low_slot.kind());
    try std.testing.expectEqual(@as(?usize, 0), low_slot.value());
    try std.testing.expectEqual(@as(?isize, null), low_slot.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, high_slot.kind());
    try std.testing.expectEqual(@as(?usize, null), high_slot.value());
    try std.testing.expectEqual(@as(?isize, -1), high_slot.errorCode());
}

test "top odd err raw has rejected preimages from both source families" {
    const direct_source = (@as(usize, 1) << (@bitSizeOf(usize) - 1)) - 1;
    const wrapped_source = std.math.maxInt(usize);

    const direct_raw = projectedRaw(direct_source);
    const wrapped_raw = projectedRaw(wrapped_source);
    const slot = xarray_slot_view.fromRaw(direct_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(direct_source));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(wrapped_source));

    try std.testing.expectEqual(err_ptr.fromErrorCode(-1), direct_raw);
    try std.testing.expectEqual(direct_raw, wrapped_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expectEqual(@as(?isize, -1), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}
