const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn projectedRaw(source_value: usize) usize {
    return (source_value << 1) | xa_value.value_tag_mask;
}

test "direct rejected family advances through odd err raws and odd error codes in lockstep" {
    const first_source = xa_value.safe_inline_limit + 1;

    inline for (0..4) |index| {
        const source_value = first_source + index;
        const raw = projectedRaw(source_value);
        const slot = xarray_slot_view.fromRaw(raw);
        const expected_code = -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(index * 2));

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source_value));
        try std.testing.expectEqual(err_ptr.err_floor + (index * 2), raw);
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try std.testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        if (index > 0) {
            const prev_raw = projectedRaw(source_value - 1);
            try std.testing.expectEqual(@as(usize, 2), raw - prev_raw);
            try std.testing.expectEqual(@as(isize, 2), slot.errorCode().? - err_ptr.toErrorCode(prev_raw));
        }
    }
}

test "wrapped-high rejected family advances through low odd tagged raws and decoded values in lockstep" {
    const wrap_base = @as(usize, 1) << (@bitSizeOf(usize) - 1);

    inline for (0..4) |index| {
        const source_value = wrap_base + index;
        const raw = projectedRaw(source_value);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source_value));
        try std.testing.expectEqual((index * 2) + 1, raw);
        try std.testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
        try std.testing.expectEqual(@as(?usize, index), slot.value());
        try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        if (index > 0) {
            const prev_raw = projectedRaw(source_value - 1);
            try std.testing.expectEqual(@as(usize, 2), raw - prev_raw);
            try std.testing.expectEqual(@as(usize, 1), slot.value().? - xarray_slot_view.fromRaw(prev_raw).value().?);
        }
    }
}

test "terminal direct stride and wrapped-high prefix share odd-tag cadence while staying in different lanes" {
    const direct_last_source = (@as(usize, 1) << (@bitSizeOf(usize) - 1)) - 1;
    const direct_start_source = direct_last_source - 3;
    const wrapped_start_source = @as(usize, 1) << (@bitSizeOf(usize) - 1);

    inline for (0..4) |index| {
        const direct_raw = projectedRaw(direct_start_source + index);
        const wrapped_raw = projectedRaw(wrapped_start_source + index);
        const direct_slot = xarray_slot_view.fromRaw(direct_raw);
        const wrapped_slot = xarray_slot_view.fromRaw(wrapped_raw);

        try std.testing.expect((direct_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try std.testing.expect((wrapped_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, direct_slot.kind());
        try std.testing.expectEqual(xarray_slot_view.SlotKind.value, wrapped_slot.kind());
        try std.testing.expectEqual(@as(?usize, null), direct_slot.value());
        try std.testing.expectEqual(@as(?usize, index), wrapped_slot.value());
        try std.testing.expectEqual(@as(?usize, null), direct_slot.pointerValue());
        try std.testing.expectEqual(@as(?usize, null), wrapped_slot.pointerValue());
    }
}
