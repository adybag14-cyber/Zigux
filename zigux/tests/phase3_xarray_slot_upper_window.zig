const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn rawForUncheckedValue(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

test "last accepted xa_value raws stay contiguous right up to the pointer gap" {
    const values = [_]usize{
        xa_value.safe_inline_limit - 2,
        xa_value.safe_inline_limit - 1,
        xa_value.safe_inline_limit,
    };
    const expected_raws = [_]usize{
        err_ptr.err_floor - 6,
        err_ptr.err_floor - 4,
        err_ptr.err_floor - 2,
    };

    inline for (values, expected_raws) |value, expected_raw| {
        const raw = try xa_value.makeValue(value);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(expected_raw, raw);
        try testing.expect(slot.isValue());
        try testing.expect(!slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?usize, value), slot.value());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }

    const pointer_gap_raw = err_ptr.err_floor - 1;
    const pointer_gap_slot = xarray_slot_view.fromRaw(pointer_gap_raw);
    try testing.expect(pointer_gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap_slot.pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));
}

test "first rejected tagged xa_value raws reclassify as err_ptr slots" {
    const rejected_values = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        xa_value.safe_inline_limit + 3,
    };
    const expected_raws = [_]usize{
        err_ptr.err_floor,
        err_ptr.err_floor + 2,
        err_ptr.err_floor + 4,
    };
    const expected_codes = [_]isize{ -4095, -4093, -4091 };

    inline for (rejected_values, expected_raws, expected_codes) |value, expected_raw, expected_code| {
        const raw = rawForUncheckedValue(value);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(expected_raw, raw);
        try testing.expect(!xa_value.canRepresent(value));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(value));
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "opening contiguous err band stays in the err lane regardless of tag bit" {
    const raws = [_]usize{
        err_ptr.err_floor,
        err_ptr.err_floor + 1,
        err_ptr.err_floor + 2,
        err_ptr.err_floor + 3,
    };
    const expected_codes = [_]isize{ -4095, -4094, -4093, -4092 };

    inline for (raws, expected_codes) |raw, expected_code| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}
