const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const rejected_alias_count: usize = (err_ptr.max_errno + 1) / 2;

fn rejectedValue(offset: usize) usize {
    return xa_value.safe_inline_limit + 1 + offset;
}

fn rejectedRaw(offset: usize) usize {
    return (rejectedValue(offset) << 1) | xa_value.value_tag_mask;
}

fn expectedOddErrorCode(offset: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(offset * 2));
}

test "representative odd err slots keep one identity across direct raw, err constructor, and rejected value origins" {
    const offsets = [_]usize{ 0, rejected_alias_count / 2, rejected_alias_count - 1 };

    for (offsets) |offset| {
        const code = expectedOddErrorCode(offset);
        const source_value = rejectedValue(offset);
        const direct_raw = err_ptr.fromErrorCode(code);
        const constructed_slot = xarray_slot_view.fromErrorCode(code);
        const reread_slot = xarray_slot_view.fromRaw(direct_raw);
        const rejected_slot = xarray_slot_view.fromRaw(rejectedRaw(offset));

        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(source_value));
        try testing.expectEqual(direct_raw, rejectedRaw(offset));
        try testing.expectEqual(direct_raw, constructed_slot.rawValue());
        try testing.expectEqual(direct_raw, reread_slot.rawValue());
        try testing.expectEqual(direct_raw, rejected_slot.rawValue());
        try testing.expectEqual(@as(usize, 1), direct_raw & xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(direct_raw));
        try testing.expect(!xa_value.isValue(direct_raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(direct_raw));

        try testing.expectEqual(xarray_slot_view.SlotKind.err, constructed_slot.kind());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, reread_slot.kind());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, rejected_slot.kind());
        try testing.expectEqual(@as(?isize, code), constructed_slot.errorCode());
        try testing.expectEqual(@as(?isize, code), reread_slot.errorCode());
        try testing.expectEqual(@as(?isize, code), rejected_slot.errorCode());
        try testing.expectEqual(@as(?usize, null), constructed_slot.value());
        try testing.expectEqual(@as(?usize, null), reread_slot.value());
        try testing.expectEqual(@as(?usize, null), rejected_slot.value());
        try testing.expectEqual(@as(?usize, null), constructed_slot.pointerValue());
        try testing.expectEqual(@as(?usize, null), reread_slot.pointerValue());
        try testing.expectEqual(@as(?usize, null), rejected_slot.pointerValue());
    }
}

test "first odd err origin still sits between the pointer gap and the first even err raw" {
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const first_odd_raw = rejectedRaw(0);
    const first_even_raw = first_odd_raw + 1;

    const pointer_gap_slot = xarray_slot_view.fromRaw(pointer_gap_raw);
    const first_odd_slot = xarray_slot_view.fromErrorCode(-4095);
    const first_even_slot = xarray_slot_view.fromRaw(first_even_raw);

    try testing.expectEqual(err_ptr.err_floor, first_odd_raw);
    try testing.expectEqual(pointer_gap_raw + 1, first_odd_raw);
    try testing.expectEqual(first_odd_raw + 1, first_even_raw);

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap_slot.kind());
    try testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap_slot.pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));

    try testing.expectEqual(xarray_slot_view.SlotKind.err, first_odd_slot.kind());
    try testing.expectEqual(@as(?isize, -4095), first_odd_slot.errorCode());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, first_even_slot.kind());
    try testing.expectEqual(@as(?isize, -4094), first_even_slot.errorCode());
    try testing.expect(!xa_value.isValue(first_odd_raw));
    try testing.expect(!xa_value.isValue(first_even_raw));
}

test "top odd err origins keep the final odd-even-odd mapping exact" {
    const previous_odd_offset = rejected_alias_count - 2;
    const top_odd_offset = rejected_alias_count - 1;

    const previous_odd_raw = rejectedRaw(previous_odd_offset);
    const middle_even_raw = previous_odd_raw + 1;
    const top_odd_raw = rejectedRaw(top_odd_offset);

    const previous_odd_slot = xarray_slot_view.fromRaw(previous_odd_raw);
    const middle_even_slot = xarray_slot_view.fromRaw(middle_even_raw);
    const top_odd_slot = xarray_slot_view.fromErrorCode(-1);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejectedValue(previous_odd_offset)));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejectedValue(top_odd_offset)));

    try testing.expectEqual(err_ptr.fromErrorCode(-3), previous_odd_raw);
    try testing.expectEqual(err_ptr.fromErrorCode(-2), middle_even_raw);
    try testing.expectEqual(err_ptr.fromErrorCode(-1), top_odd_raw);
    try testing.expectEqual(previous_odd_raw + 2, top_odd_raw);

    try testing.expectEqual(@as(usize, 1), previous_odd_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), middle_even_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 1), top_odd_raw & xa_value.value_tag_mask);

    try testing.expectEqual(xarray_slot_view.SlotKind.err, previous_odd_slot.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, middle_even_slot.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, top_odd_slot.kind());
    try testing.expectEqual(@as(?isize, -3), previous_odd_slot.errorCode());
    try testing.expectEqual(@as(?isize, -2), middle_even_slot.errorCode());
    try testing.expectEqual(@as(?isize, -1), top_odd_slot.errorCode());
}
