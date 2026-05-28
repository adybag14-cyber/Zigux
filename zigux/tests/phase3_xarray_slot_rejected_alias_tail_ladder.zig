const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn uncheckedRawForSource(value: usize) usize {
    return (value *% 2) | xa_value.value_tag_mask;
}

fn expectedOddTailCode(offset_from_last: usize) isize {
    return -@as(isize, @intCast((offset_from_last * 2) + 1));
}

test "last rejected xa_value source values before wrap stay tagged err slots" {
    const last_alias_value = std.math.maxInt(usize) >> 1;
    const first_sample = last_alias_value - 3;

    inline for (0..4) |offset| {
        const source = first_sample + offset;
        const raw = uncheckedRawForSource(source);
        const slot = xarray_slot_view.fromRaw(raw);
        const reverse_offset = 3 - offset;
        const expected_code = expectedOddTailCode(reverse_offset);

        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(source));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source));
        try testing.expectEqual(err_ptr.fromErrorCode(expected_code), raw);
        try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "rejected alias tail advances by one source step, two raw steps, and two error-code steps" {
    const last_alias_value = std.math.maxInt(usize) >> 1;
    const first_sample = last_alias_value - 3;

    inline for (0..3) |offset| {
        const source = first_sample + offset;
        const next_source = source + 1;
        const raw = uncheckedRawForSource(source);
        const next_raw = uncheckedRawForSource(next_source);
        const code = err_ptr.toErrorCode(raw);
        const next_code = err_ptr.toErrorCode(next_raw);

        try testing.expectEqual(source + 1, next_source);
        try testing.expectEqual(raw + 2, next_raw);
        try testing.expectEqual(code + 2, next_code);
        try testing.expectEqual(@as(isize, 2), next_code - code);
    }
}

test "rejected alias tail reaches the top err_ptr encoding exactly at the final source" {
    const last_alias_value = std.math.maxInt(usize) >> 1;
    const last_raw = uncheckedRawForSource(last_alias_value);
    const last_slot = xarray_slot_view.fromRaw(last_raw);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(last_alias_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(last_alias_value));
    try testing.expectEqual(err_ptr.fromErrorCode(-1), last_raw);
    try testing.expectEqual(xarray_slot_view.SlotKind.err, last_slot.kind());
    try testing.expectEqual(@as(?isize, -1), last_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), last_slot.value());
    try testing.expectEqual(@as(?usize, null), last_slot.pointerValue());
}
