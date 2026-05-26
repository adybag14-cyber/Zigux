const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");
const idr_slot_view = @import("idr_slot_view");

test "idr slot view keeps empty slots explicit" {
    const slot = idr_slot_view.emptySlot();

    try testing.expect(slot.isEmpty());
    try testing.expect(!slot.isInternalValue());
    try testing.expect(!slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "idr slot view keeps mapped pointers distinct from xarray-tagged internals" {
    const raw: usize = 0x1000;
    const slot = idr_slot_view.fromPointer(raw);

    try testing.expect(slot.isPointer());
    try testing.expect(!slot.isInternalValue());
    try testing.expect(!slot.isErr());
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try testing.expect(!idr_slot_view.isTaggedInternalEntry(raw));
}

test "idr slot view keeps xa_value entries in the internal lane" {
    const raw = try xa_value.makeValue(29);
    const slot = idr_slot_view.fromRaw(raw);

    try testing.expect(!slot.isEmpty());
    try testing.expect(slot.isInternalValue());
    try testing.expect(!slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?usize, 29), slot.internalValue());
    try testing.expect(idr_slot_view.isTaggedInternalEntry(raw));
}

test "idr slot view preserves err_ptr encodings as tagged error entries" {
    const raw = err_ptr.fromErrorCode(-22);
    const slot = idr_slot_view.fromRaw(raw);

    try testing.expect(!slot.isEmpty());
    try testing.expect(!slot.isInternalValue());
    try testing.expect(slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?isize, -22), slot.errorCode());
    try testing.expect(idr_slot_view.isTaggedInternalEntry(raw));
}

test "idr slot wrapper agrees with the xarray slot surface on all visible lanes" {
    const empty_slot = idr_slot_view.fromRaw(0);
    const internal_slot = try idr_slot_view.fromInternalValue(7);
    const err_slot = idr_slot_view.fromErrorCode(-1);
    const pointer_slot = idr_slot_view.fromPointer(0x2000);

    try testing.expect(empty_slot.isEmpty());

    try testing.expect(internal_slot.isInternalValue());
    try testing.expectEqual(@as(?usize, 7), internal_slot.internalValue());
    try testing.expect(xarray_slot_view.fromRaw(internal_slot.rawValue()).isValue());

    try testing.expect(err_slot.isErr());
    try testing.expectEqual(@as(?isize, -1), err_slot.errorCode());
    try testing.expect(xarray_slot_view.fromRaw(err_slot.rawValue()).isErr());

    try testing.expect(pointer_slot.isPointer());
    try testing.expectEqual(@as(?usize, 0x2000), pointer_slot.pointerValue());
    try testing.expect(xarray_slot_view.fromRaw(pointer_slot.rawValue()).isPointer());
}
