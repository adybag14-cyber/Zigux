const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn uncheckedRaw(value: usize) usize {
    return (value *% 2) | xa_value.value_tag_mask;
}

test "rejected xa_value preimages split between err-band aliases and wrapped-low raws" {
    const first_alias_value = xa_value.safe_inline_limit + 1;
    const last_alias_value = std.math.maxInt(usize) >> 1;
    const first_wrap_value = last_alias_value + 1;
    const second_wrap_value = last_alias_value + 2;

    try testing.expect(err_ptr.isErrValue(uncheckedRaw(first_alias_value)));
    try testing.expect(err_ptr.isErrValue(uncheckedRaw(last_alias_value)));
    try testing.expect(!err_ptr.isErrValue(uncheckedRaw(first_wrap_value)));
    try testing.expect(!err_ptr.isErrValue(uncheckedRaw(second_wrap_value)));
}

test "wrapped-low rejected raws reread as ordinary low xa_values" {
    const last_alias_value = std.math.maxInt(usize) >> 1;
    const first_wrap_value = last_alias_value + 1;
    const second_wrap_value = last_alias_value + 2;

    const first_wrap_raw = uncheckedRaw(first_wrap_value);
    const second_wrap_raw = uncheckedRaw(second_wrap_value);
    const first_wrap_slot = xarray_slot_view.fromRaw(first_wrap_raw);
    const second_wrap_slot = xarray_slot_view.fromRaw(second_wrap_raw);

    try testing.expectEqual(@as(usize, 1), first_wrap_raw);
    try testing.expectEqual(@as(usize, 3), second_wrap_raw);

    try testing.expectEqual(xarray_slot_view.SlotKind.value, first_wrap_slot.kind());
    try testing.expectEqual(@as(?usize, 0), first_wrap_slot.value());
    try testing.expectEqual(@as(?isize, null), first_wrap_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), first_wrap_slot.pointerValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.value, second_wrap_slot.kind());
    try testing.expectEqual(@as(?usize, 1), second_wrap_slot.value());
    try testing.expectEqual(@as(?isize, null), second_wrap_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), second_wrap_slot.pointerValue());
}

test "source constructors keep wrapped-low candidates rejected even when raw rereads look valid" {
    const last_alias_value = std.math.maxInt(usize) >> 1;
    const first_wrap_value = last_alias_value + 1;
    const second_wrap_value = last_alias_value + 2;

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(first_wrap_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(second_wrap_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(first_wrap_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(second_wrap_value));
}

test "alias tail still reaches the top err_ptr encoding before the wrap" {
    const last_alias_value = std.math.maxInt(usize) >> 1;
    const alias_raw = uncheckedRaw(last_alias_value);
    const alias_slot = xarray_slot_view.fromRaw(alias_raw);

    try testing.expectEqual(err_ptr.fromErrorCode(-1), alias_raw);
    try testing.expectEqual(xarray_slot_view.SlotKind.err, alias_slot.kind());
    try testing.expectEqual(@as(?isize, -1), alias_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), alias_slot.value());
    try testing.expectEqual(@as(?usize, null), alias_slot.pointerValue());
}
