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

test "inline zero stays tagged without looking like a null slot" {
    const raw = try xa_value.makeValue(0);
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(!slot.isNull());
    try testing.expect(slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, 0), slot.value());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "top err_ptr encoding stays tagged and never falls back to pointer-like" {
    const raw = err_ptr.fromErrorCode(-1);
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(!slot.isNull());
    try testing.expect(!slot.isValue());
    try testing.expect(slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?isize, -1), slot.errorCode());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "constructor helpers build explicit xarray slot lanes" {
    const null_slot = xarray_slot_view.nullSlot();
    const value_slot = try xarray_slot_view.fromValue(29);
    const err_slot = xarray_slot_view.fromErrorCode(-22);
    const pointer_slot = xarray_slot_view.fromPointer(0x1000);

    try testing.expect(null_slot.isNull());
    try testing.expectEqual(@as(usize, 0), null_slot.rawValue());

    try testing.expect(value_slot.isValue());
    try testing.expectEqual(try xa_value.makeValue(29), value_slot.rawValue());
    try testing.expectEqual(@as(?usize, 29), value_slot.value());

    try testing.expect(err_slot.isErr());
    try testing.expectEqual(err_ptr.fromErrorCode(-22), err_slot.rawValue());
    try testing.expectEqual(@as(?isize, -22), err_slot.errorCode());

    try testing.expect(pointer_slot.isPointer());
    try testing.expectEqual(@as(usize, 0x1000), pointer_slot.rawValue());
    try testing.expectEqual(@as(?usize, 0x1000), pointer_slot.pointerValue());
}

test "low boundary raws stay ordered as null, tagged value, then pointer-like gap" {
    const null_slot = xarray_slot_view.fromRaw(0);
    const inline_zero_raw = try xa_value.makeValue(0);
    const inline_zero_slot = xarray_slot_view.fromRaw(inline_zero_raw);
    const low_gap_raw = inline_zero_raw + 1;
    const low_gap_slot = xarray_slot_view.fromRaw(low_gap_raw);

    try testing.expect(null_slot.isNull());
    try testing.expectEqual(@as(?usize, null), null_slot.value());

    try testing.expectEqual(@as(usize, 1), inline_zero_raw);
    try testing.expect(inline_zero_slot.isValue());
    try testing.expectEqual(@as(?usize, 0), inline_zero_slot.value());

    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(low_gap_raw));
    try testing.expect(low_gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, low_gap_raw), low_gap_slot.pointerValue());
}

test "high boundary raws stay ordered as tagged value, pointer-like gap, then err_ptr" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const inline_limit_slot = xarray_slot_view.fromRaw(inline_limit_raw);
    const high_gap_raw = inline_limit_raw + 1;
    const high_gap_slot = xarray_slot_view.fromRaw(high_gap_raw);
    const err_floor_slot = xarray_slot_view.fromRaw(err_ptr.err_floor);

    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);
    try testing.expect(inline_limit_slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), inline_limit_slot.value());

    try testing.expectEqual(err_ptr.err_floor - 1, high_gap_raw);
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(high_gap_raw));
    try testing.expect(high_gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, high_gap_raw), high_gap_slot.pointerValue());

    try testing.expect(err_floor_slot.isErr());
    try testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());
}
