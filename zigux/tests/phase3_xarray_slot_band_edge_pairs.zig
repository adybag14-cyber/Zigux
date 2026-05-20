const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "highest accepted xa_value pair keeps both pointer-like separators explicit" {
    const next_to_limit = xa_value.safe_inline_limit - 1;
    const next_to_limit_raw = try xa_value.makeValue(next_to_limit);
    const between_values_raw = next_to_limit_raw + 1;
    const limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_before_err_floor_raw = limit_raw + 1;
    const first_err_raw = gap_before_err_floor_raw + 1;

    const lower_value_slot = xarray_slot_view.fromRaw(next_to_limit_raw);
    const between_values_slot = xarray_slot_view.fromRaw(between_values_raw);
    const limit_slot = xarray_slot_view.fromRaw(limit_raw);
    const gap_slot = xarray_slot_view.fromRaw(gap_before_err_floor_raw);
    const first_err_slot = xarray_slot_view.fromRaw(first_err_raw);

    try testing.expectEqual(next_to_limit_raw + 2, limit_raw);
    try testing.expectEqual(limit_raw + 2, first_err_raw);

    try testing.expect(lower_value_slot.isValue());
    try testing.expectEqual(@as(?usize, next_to_limit), lower_value_slot.value());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(next_to_limit_raw));

    try testing.expect(between_values_slot.isPointer());
    try testing.expectEqual(@as(?usize, between_values_raw), between_values_slot.pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(between_values_raw));

    try testing.expect(limit_slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), limit_slot.value());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(limit_raw));

    try testing.expect(gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, gap_before_err_floor_raw), gap_slot.pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_before_err_floor_raw));

    try testing.expect(first_err_slot.isErr());
    try testing.expectEqual(@as(?isize, -4095), first_err_slot.errorCode());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(first_err_raw));
}

test "opening err_ptr quartet alternates tag parity without leaving the err lane" {
    var offset: usize = 0;
    while (offset < 4) : (offset += 1) {
        const raw = err_ptr.err_floor + offset;
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, -4095 + @as(isize, @intCast(offset))), slot.errorCode());
        try testing.expectEqual((offset + 1) & 1, raw & xa_value.value_tag_mask);
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "top err_ptr quartet keeps tagged aliases and even neighbors inside the err lane" {
    const raws = [_]usize{
        err_ptr.fromErrorCode(-4),
        err_ptr.fromErrorCode(-3),
        err_ptr.fromErrorCode(-2),
        err_ptr.fromErrorCode(-1),
    };
    const expected_codes = [_]isize{ -4, -3, -2, -1 };

    for (raws, expected_codes, 0..) |raw, expected_code, index| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expectEqual(index & 1, raw & xa_value.value_tag_mask);
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }

    const tagged_penultimate = raws[1] >> 1;
    const tagged_top = raws[3] >> 1;
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(tagged_penultimate));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(tagged_top));
    try testing.expectEqual(raws[1], (tagged_penultimate << 1) | xa_value.value_tag_mask);
    try testing.expectEqual(raws[3], (tagged_top << 1) | xa_value.value_tag_mask);
}
