const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const rejected_value_count: usize = (err_ptr.max_errno + 1) / 2;

fn rejectedValue(offset: usize) usize {
    return xa_value.safe_inline_limit + 1 + offset;
}

fn rejectedRaw(offset: usize) usize {
    return (rejectedValue(offset) << 1) | xa_value.value_tag_mask;
}

fn expectedErrorCode(offset: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(offset * 2));
}

test "rejected source-value endpoints map onto the odd err band" {
    const first_offset: usize = 0;
    const middle_offset: usize = rejected_value_count / 2;
    const last_offset: usize = rejected_value_count - 1;

    const first_slot = xarray_slot_view.fromRaw(rejectedRaw(first_offset));
    const middle_slot = xarray_slot_view.fromRaw(rejectedRaw(middle_offset));
    const last_slot = xarray_slot_view.fromRaw(rejectedRaw(last_offset));

    try testing.expectEqual(err_ptr.err_floor, rejectedRaw(first_offset));
    try testing.expectEqual(@as(?isize, -4095), first_slot.errorCode());

    try testing.expectEqual(err_ptr.err_floor + middle_offset * 2, rejectedRaw(middle_offset));
    try testing.expectEqual(@as(?isize, -2047), middle_slot.errorCode());

    try testing.expectEqual(err_ptr.fromErrorCode(-1), rejectedRaw(last_offset));
    try testing.expectEqual(@as(?isize, -1), last_slot.errorCode());

    try testing.expectEqual(xarray_slot_view.SlotKind.err, first_slot.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, middle_slot.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, last_slot.kind());
}

test "every rejected source value maps to an odd raw err code and never reopens as value" {
    var offset: usize = 0;
    while (offset < rejected_value_count) : (offset += 1) {
        const source_value = rejectedValue(offset);
        const raw = rejectedRaw(offset);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(source_value));
        try testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(slot.isErr());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expectEqual(@as(?isize, expectedErrorCode(offset)), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "rejected source-value window occupies exactly half of the err band" {
    var offset: usize = 0;
    var odd_err_codes: usize = 0;

    while (offset < rejected_value_count) : (offset += 1) {
        const raw = rejectedRaw(offset);
        const code = xarray_slot_view.fromRaw(raw).errorCode().?;

        try testing.expectEqual(err_ptr.fromErrorCode(code), raw);
        try testing.expect((@as(usize, @bitCast(code)) & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        odd_err_codes += 1;
    }

    try testing.expectEqual((err_ptr.max_errno + 1) / 2, odd_err_codes);
    try testing.expectEqual(@as(usize, 2048), odd_err_codes);
    try testing.expectEqual(@as(usize, 2047), err_ptr.max_errno - odd_err_codes);
}
