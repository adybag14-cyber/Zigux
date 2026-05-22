const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "successive odd xa_value aliases inside the err band stay rejected and classify as err" {
    const candidate_values = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        xa_value.safe_inline_limit + 3,
    };
    const expected_raws = [_]usize{
        err_ptr.err_floor,
        err_ptr.err_floor + 2,
        err_ptr.err_floor + 4,
    };
    const expected_errors = [_]isize{ -4095, -4093, -4091 };

    for (candidate_values, expected_raws, expected_errors) |candidate_value, expected_raw, expected_error| {
        const raw = (candidate_value << 1) | xa_value.value_tag_mask;
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(expected_raw, raw);
        try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(candidate_value));
        try testing.expect(!xa_value.canRepresent(candidate_value));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(raw, slot.rawValue());
        try testing.expectEqual(@as(?isize, expected_error), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "contiguous low err strip stays in the err lane across odd aliases and even raws" {
    const raws = [_]usize{
        err_ptr.err_floor,
        err_ptr.err_floor + 1,
        err_ptr.err_floor + 2,
        err_ptr.err_floor + 3,
        err_ptr.err_floor + 4,
    };
    const expected_errors = [_]isize{ -4095, -4094, -4093, -4092, -4091 };
    const expected_low_bits = [_]usize{ 1, 0, 1, 0, 1 };

    for (0..raws.len - 1) |idx| {
        try testing.expectEqual(raws[idx] + 1, raws[idx + 1]);
    }

    for (raws, expected_errors, expected_low_bits) |raw, expected_error, expected_low_bit| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(expected_low_bit, raw & xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expectEqual(@as(?isize, expected_error), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}
