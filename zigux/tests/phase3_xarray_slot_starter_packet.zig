const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "xarray slot view keeps null slots explicit" {
    const slot = xarray_slot_view.fromRaw(0);

    try testing.expect(slot.isNull());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, null), slot.value());
}

test "xarray slot view keeps xa_value entries out of the err_ptr band" {
    const raw = try xa_value.makeValue(29);
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, 29), slot.value());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "xarray slot view preserves err_ptr encodings as tagged error entries" {
    const raw = err_ptr.fromErrorCode(-22);
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(slot.isErr());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?isize, -22), slot.errorCode());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "xarray slot view keeps ordinary pointer-like slots separate from tagged entries" {
    const raw: usize = 0x1000;
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(slot.isPointer());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
}

test "safe inline limit still lands in the tagged-value lane" {
    const raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), slot.value());
    try testing.expect(raw < err_ptr.err_floor);
}
