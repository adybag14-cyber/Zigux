const std = @import("std");
const testing = std.testing;

const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn uncheckedRaw(value: usize) usize {
    return (value *% 2) | xa_value.value_tag_mask;
}

test "wrapped-low rejected ladder advances through successive low xa_value raws" {
    const last_alias_value = std.math.maxInt(usize) >> 1;
    const first_wrap_value = last_alias_value + 1;

    inline for (0..4) |offset| {
        const source_value = first_wrap_value + offset;
        const raw = uncheckedRaw(source_value);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(@as(usize, (offset * 2) + 1), raw);
        try testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
        try testing.expect(slot.isValue());
        try testing.expect(!slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?usize, offset), slot.value());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "wrapped-low rejected ladder stays constructor-rejected at every rung" {
    const last_alias_value = std.math.maxInt(usize) >> 1;
    const first_wrap_value = last_alias_value + 1;

    inline for (0..4) |offset| {
        const source_value = first_wrap_value + offset;

        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(source_value));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source_value));
    }
}

test "wrapped-low rejected ladder preserves the low decoded value sequence" {
    const last_alias_value = std.math.maxInt(usize) >> 1;
    const first_wrap_value = last_alias_value + 1;

    inline for (0..4) |offset| {
        const raw = uncheckedRaw(first_wrap_value + offset);
        const decoded = xa_value.toValue(raw);

        try testing.expectEqual(@as(usize, offset), decoded);
    }
}
