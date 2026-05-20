const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "representative odd raws stay xa_value slots across low middle and upper windows" {
    const values = [_]usize{
        0,
        17,
        xa_value.safe_inline_limit / 2,
        xa_value.safe_inline_limit - 1,
        xa_value.safe_inline_limit,
    };

    for (values) |value| {
        const raw = try xa_value.makeValue(value);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(raw < err_ptr.err_floor);
        try testing.expect(xa_value.isValue(raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

        try testing.expect(slot.isValue());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isPointer());
        try testing.expect(!slot.isErr());
        try testing.expectEqual(@as(?usize, value), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());
    }
}

test "accepted odd raws keep exact pointer separators around consecutive value pairs" {
    const base_values = [_]usize{
        0,
        xa_value.safe_inline_limit / 2,
        xa_value.safe_inline_limit - 1,
    };

    for (base_values) |value| {
        const lower_raw = try xa_value.makeValue(value);
        const separator_raw = lower_raw + 1;
        const upper_raw = try xa_value.makeValue(value + 1);

        const lower_slot = xarray_slot_view.fromRaw(lower_raw);
        const separator_slot = xarray_slot_view.fromRaw(separator_raw);
        const upper_slot = xarray_slot_view.fromRaw(upper_raw);

        try testing.expectEqual(lower_raw + 1, separator_raw);
        try testing.expectEqual(separator_raw + 1, upper_raw);

        try testing.expect(lower_slot.isValue());
        try testing.expectEqual(@as(?usize, value), lower_slot.value());

        try testing.expect(separator_slot.isPointer());
        try testing.expectEqual(@as(?usize, separator_raw), separator_slot.pointerValue());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(separator_raw));

        try testing.expect(upper_slot.isValue());
        try testing.expectEqual(@as(?usize, value + 1), upper_slot.value());
    }
}

test "lowest accepted odd raw stays non-null while higher odd raws keep pointer lower neighbors" {
    const zero_raw = try xa_value.makeValue(0);
    const zero_slot = xarray_slot_view.fromRaw(zero_raw);
    const zero_lower = xarray_slot_view.fromRaw(zero_raw - 1);

    try testing.expectEqual(@as(usize, 1), zero_raw);
    try testing.expect(zero_slot.isValue());
    try testing.expectEqual(@as(?usize, 0), zero_slot.value());
    try testing.expect(zero_lower.isNull());

    const higher_values = [_]usize{
        1,
        xa_value.safe_inline_limit / 2,
        xa_value.safe_inline_limit,
    };

    for (higher_values) |value| {
        const raw = try xa_value.makeValue(value);
        const lower_slot = xarray_slot_view.fromRaw(raw - 1);

        try testing.expect(raw > 1);
        try testing.expect(lower_slot.isPointer());
        try testing.expectEqual(@as(?usize, raw - 1), lower_slot.pointerValue());
    }
}
