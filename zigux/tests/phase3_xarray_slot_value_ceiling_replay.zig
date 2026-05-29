const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "highest xa_value payloads stay value slots below the err floor" {
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

    for (values, expected_raws) |value, expected_raw| {
        const slot = try xarray_slot_view.fromValue(value);

        try std.testing.expectEqual(expected_raw, slot.rawValue());
        try std.testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
        try std.testing.expect(slot.isValue());
        try std.testing.expect(!slot.isErr());
        try std.testing.expect(!slot.isPointer());
        try std.testing.expectEqual(@as(?usize, value), slot.value());
        try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(slot.rawValue()));
    }
}

test "first rejected xa_value payload hands off to the err_ptr floor" {
    const rejected = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (rejected << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(overlapping_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected));
    try std.testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, -4095), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(overlapping_raw));
}
