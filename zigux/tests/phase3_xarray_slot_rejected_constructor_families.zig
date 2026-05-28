const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn projectedRaw(source_value: usize) usize {
    return (source_value << 1) | xa_value.value_tag_mask;
}

test "fromValue rejects err-band alias sources while raw projection still decodes as err" {
    inline for (0..4) |index| {
        const source_value = xa_value.safe_inline_limit + index + 1;
        const raw = projectedRaw(source_value);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source_value));
        try std.testing.expectEqual(err_ptr.err_floor + (index * 2), raw);
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expectEqual(@as(?isize, err_ptr.toErrorCode(raw)), slot.errorCode());
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "fromValue rejects wrapped-high sources while raw projection still decodes as low tagged value" {
    const wrap_base = @as(usize, 1) << (@bitSizeOf(usize) - 1);

    inline for (0..4) |index| {
        const source_value = wrap_base + index;
        const raw = projectedRaw(source_value);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source_value));
        try std.testing.expectEqual(@as(usize, index * 2 + 1), raw);
        try std.testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
        try std.testing.expectEqual(@as(?usize, index), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "representative rejected constructor families stay out of null and pointer lanes" {
    const alias_source = xa_value.safe_inline_limit + 1;
    const alias_slot = xarray_slot_view.fromRaw(projectedRaw(alias_source));
    const wrapped_source = (@as(usize, 1) << (@bitSizeOf(usize) - 1)) + 1;
    const wrapped_slot = xarray_slot_view.fromRaw(projectedRaw(wrapped_source));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, alias_slot.kind());
    try std.testing.expect(!alias_slot.isNull());
    try std.testing.expect(!alias_slot.isPointer());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), alias_slot.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, wrapped_slot.kind());
    try std.testing.expect(!wrapped_slot.isNull());
    try std.testing.expect(!wrapped_slot.isPointer());
    try std.testing.expectEqual(@as(?usize, 1), wrapped_slot.value());
}
