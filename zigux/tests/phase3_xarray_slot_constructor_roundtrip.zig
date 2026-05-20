const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "null constructor roundtrips through raw classification" {
    const constructed = xarray_slot_view.nullSlot();
    const reread = xarray_slot_view.fromRaw(constructed.rawValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.null, constructed.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.null, reread.kind());
    try testing.expect(constructed.isNull());
    try testing.expect(reread.isNull());
    try testing.expectEqual(@as(usize, 0), reread.rawValue());
}

test "safe inline limit constructor roundtrips as the last tagged value before the gap" {
    const constructed = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const reread = xarray_slot_view.fromRaw(constructed.rawValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.value, constructed.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.value, reread.kind());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), reread.value());
    try testing.expectEqual(err_ptr.err_floor - 2, reread.rawValue());
    try testing.expect(reread.rawValue() < err_ptr.err_floor - 1);
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(reread.rawValue()));
}

test "pointer gap constructor roundtrips without reopening tagged decoders" {
    const gap_raw = err_ptr.err_floor - 1;
    const constructed = xarray_slot_view.fromPointer(gap_raw);
    const reread = xarray_slot_view.fromRaw(constructed.rawValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, constructed.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, reread.kind());
    try testing.expectEqual(@as(?usize, gap_raw), reread.pointerValue());
    try testing.expectEqual(@as(?usize, null), reread.value());
    try testing.expectEqual(@as(?isize, null), reread.errorCode());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));
}

test "err constructors preserve floor next and top classification across raw rereads" {
    const floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const next_slot = xarray_slot_view.fromErrorCode(-4094);
    const top_slot = xarray_slot_view.fromErrorCode(-1);

    const floor_reread = xarray_slot_view.fromRaw(floor_slot.rawValue());
    const next_reread = xarray_slot_view.fromRaw(next_slot.rawValue());
    const top_reread = xarray_slot_view.fromRaw(top_slot.rawValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.err, floor_reread.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, next_reread.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, top_reread.kind());

    try testing.expectEqual(@as(?isize, -4095), floor_reread.errorCode());
    try testing.expectEqual(@as(?isize, -4094), next_reread.errorCode());
    try testing.expectEqual(@as(?isize, -1), top_reread.errorCode());

    try testing.expect(xarray_slot_view.isTaggedInternalEntry(floor_reread.rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(next_reread.rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(top_reread.rawValue()));

    try testing.expect((floor_reread.rawValue() & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try testing.expect((next_reread.rawValue() & xa_value.value_tag_mask) == 0);
    try testing.expect((top_reread.rawValue() & xa_value.value_tag_mask) == xa_value.value_tag_mask);
}

test "representative constructor raws stay ordered across the lane boundary sequence" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const next_slot = xarray_slot_view.fromErrorCode(-4094);
    const top_slot = xarray_slot_view.fromErrorCode(-1);

    try testing.expectEqual(err_ptr.err_floor - 2, value_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 1, pointer_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor, floor_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor + 1, next_slot.rawValue());

    try testing.expect(value_slot.rawValue() < pointer_slot.rawValue());
    try testing.expect(pointer_slot.rawValue() < floor_slot.rawValue());
    try testing.expect(floor_slot.rawValue() < next_slot.rawValue());
    try testing.expect(next_slot.rawValue() < top_slot.rawValue());
}
