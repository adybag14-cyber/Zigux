const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "value ceiling rejection keeps raw gap and err floor in separate lanes" {
    const accepted_value = xa_value.safe_inline_limit;
    const rejected_value = accepted_value + 1;
    const accepted_raw = try xa_value.makeValue(accepted_value);
    const gap_raw = accepted_raw + 1;
    const rejected_alias_raw = (rejected_value << 1) | xa_value.value_tag_mask;

    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xa_value.makeValue(rejected_value),
    );
    try std.testing.expectEqual(err_ptr.err_floor - 2, accepted_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, gap_raw);
    try std.testing.expectEqual(err_ptr.err_floor, rejected_alias_raw);

    const accepted_slot = xarray_slot_view.fromRaw(accepted_raw);
    const gap_slot = xarray_slot_view.fromRaw(gap_raw);
    const rejected_alias_slot = xarray_slot_view.fromRaw(rejected_alias_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, accepted_slot.kind());
    try std.testing.expectEqual(@as(?usize, accepted_value), accepted_slot.value());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(accepted_raw));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap_slot.kind());
    try std.testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), gap_slot.value());
    try std.testing.expectEqual(@as(?isize, null), gap_slot.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, rejected_alias_slot.kind());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), rejected_alias_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), rejected_alias_slot.value());
    try std.testing.expectEqual(@as(?usize, null), rejected_alias_slot.pointerValue());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(rejected_alias_raw));
}

test "public value constructor agrees with raw decoder only below the ceiling" {
    const values = [_]usize{
        0,
        1,
        xa_value.safe_inline_limit - 1,
        xa_value.safe_inline_limit,
    };

    for (values) |value| {
        const raw_slot = xarray_slot_view.fromRaw(try xa_value.makeValue(value));
        const constructed_slot = try xarray_slot_view.fromValue(value);

        try std.testing.expectEqual(raw_slot.rawValue(), constructed_slot.rawValue());
        try std.testing.expectEqual(xarray_slot_view.SlotKind.value, constructed_slot.kind());
        try std.testing.expectEqual(@as(?usize, value), constructed_slot.value());
        try std.testing.expectEqual(@as(?isize, null), constructed_slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), constructed_slot.pointerValue());
    }

    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1),
    );
}

test "rejected value aliases decode as errors, not truncated values" {
    const rejected_values = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        xa_value.safe_inline_limit + 3,
        xa_value.safe_inline_limit + 4,
    };

    for (rejected_values) |value| {
        const raw = (value << 1) | xa_value.value_tag_mask;
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expect(!xa_value.canRepresent(value));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(value));
        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect(!xa_value.isValue(raw));
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}
