const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "first rejected xa_value payloads alias the first tagged err_ptr raws" {
    inline for (0..3) |index| {
        const rejected_payload = xa_value.safe_inline_limit + 1 + index;
        const aliased_raw = (rejected_payload << 1) | xa_value.value_tag_mask;
        const expected_raw = err_ptr.err_floor + (index * 2);
        const expected_code = -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(index * 2));
        const slot = xarray_slot_view.fromRaw(aliased_raw);
        const rebuilt_err_slot = xarray_slot_view.fromErrorCode(expected_code);

        try testing.expectError(
            error.ValueWouldOverlapErrPtr,
            xarray_slot_view.fromValue(rejected_payload),
        );
        try testing.expectEqual(expected_raw, aliased_raw);
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expect(!slot.isNull());
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(aliased_raw));
        try testing.expectEqual(expected_raw, rebuilt_err_slot.rawValue());
        try testing.expectEqual(@as(?isize, expected_code), rebuilt_err_slot.errorCode());
    }
}

test "even err_ptr raws between rejected xa_value aliases stay outside the value lane" {
    const first_rejected_payload = xa_value.safe_inline_limit + 1;
    const second_rejected_payload = first_rejected_payload + 1;

    const first_alias_raw = (first_rejected_payload << 1) | xa_value.value_tag_mask;
    const second_alias_raw = (second_rejected_payload << 1) | xa_value.value_tag_mask;
    const intervening_raw = first_alias_raw + 1;

    const first_slot = xarray_slot_view.fromRaw(first_alias_raw);
    const gap_slot = xarray_slot_view.fromRaw(intervening_raw);
    const second_slot = xarray_slot_view.fromRaw(second_alias_raw);

    try testing.expectEqual(err_ptr.err_floor, first_alias_raw);
    try testing.expectEqual(err_ptr.err_floor + 1, intervening_raw);
    try testing.expectEqual(err_ptr.err_floor + 2, second_alias_raw);

    try testing.expect(first_slot.isErr());
    try testing.expect(gap_slot.isErr());
    try testing.expect(second_slot.isErr());

    try testing.expect(!first_slot.isValue());
    try testing.expect(!gap_slot.isValue());
    try testing.expect(!second_slot.isValue());

    try testing.expectEqual(@as(?isize, -4095), first_slot.errorCode());
    try testing.expectEqual(@as(?isize, -4094), gap_slot.errorCode());
    try testing.expectEqual(@as(?isize, -4093), second_slot.errorCode());
}

test "rejected xa_value alias window preserves odd tagged parity inside the err lane" {
    inline for (0..4) |index| {
        const rejected_payload = xa_value.safe_inline_limit + 1 + index;
        const aliased_raw = (rejected_payload << 1) | xa_value.value_tag_mask;
        const slot = xarray_slot_view.fromRaw(aliased_raw);

        try testing.expectEqual(@as(usize, 1), aliased_raw & xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(aliased_raw));
        try testing.expect(!xa_value.isValue(aliased_raw));
        try testing.expect(slot.isErr());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(aliased_raw));
    }
}
