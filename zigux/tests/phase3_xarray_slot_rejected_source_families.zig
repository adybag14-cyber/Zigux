const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn uncheckedRawForSource(value: usize) usize {
    return (value *% 2) | xa_value.value_tag_mask;
}

test "first rejected xa_value source values decode as err slots" {
    var offset: usize = 0;
    while (offset < 4) : (offset += 1) {
        const source = xa_value.safe_inline_limit + 1 + offset;
        const raw = uncheckedRawForSource(source);
        const slot = xarray_slot_view.fromRaw(raw);
        const expected_code: ?isize = err_ptr.toErrorCode(raw);

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source));
        try std.testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try std.testing.expect(!slot.isNull());
        try std.testing.expect(!slot.isValue());
        try std.testing.expect(slot.isErr());
        try std.testing.expect(!slot.isPointer());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(expected_code, slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "wrapped rejected xa_value source values decode as low value slots" {
    const wrapped_base = @as(usize, 1) << (@bitSizeOf(usize) - 1);

    var offset: usize = 0;
    while (offset < 4) : (offset += 1) {
        const source = wrapped_base + offset;
        const raw = uncheckedRawForSource(source);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source));
        try std.testing.expectEqual(try xa_value.makeValue(offset), raw);
        try std.testing.expect(xa_value.isValue(raw));
        try std.testing.expect(!err_ptr.isErrValue(raw));
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try std.testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
        try std.testing.expect(!slot.isNull());
        try std.testing.expect(slot.isValue());
        try std.testing.expect(!slot.isErr());
        try std.testing.expect(!slot.isPointer());
        try std.testing.expectEqual(@as(?usize, offset), slot.value());
        try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "representative rejected xa_value source samples stay tagged and never decode as null or pointer" {
    const wrapped_base = @as(usize, 1) << (@bitSizeOf(usize) - 1);
    const samples = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        wrapped_base,
        wrapped_base + 1,
        std.math.maxInt(usize),
    };

    for (samples) |source| {
        const raw = uncheckedRawForSource(source);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source));
        try std.testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try std.testing.expect(!slot.isNull());
        try std.testing.expect(!slot.isPointer());
        try std.testing.expect(slot.isErr() or slot.isValue());
    }
}
