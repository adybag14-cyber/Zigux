const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectPointerSlot(raw: usize) !void {
    const slot = xarray_slot_view.fromPointer(raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
}

test "fromPointer admits even raws beside xa_value lanes" {
    const inline_zero = try xa_value.makeValue(0);
    const inline_top = try xa_value.makeValue(xa_value.safe_inline_limit);

    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(inline_zero));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(inline_top));

    try expectPointerSlot(inline_zero + 1);
    try expectPointerSlot(inline_top + 1);
}

test "fromPointer admits the last non-error raw below err_ptr floor" {
    const raw = err_ptr.err_floor - 1;

    try std.testing.expect(err_ptr.isOkValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try expectPointerSlot(raw);
}

test "fromRaw keeps pointer admission boundaries separate from tagged entries" {
    const value_raw = try xa_value.makeValue(7);
    const pointer_raw = value_raw + 1;
    const err_raw = err_ptr.fromErrorCode(-7);

    const value_slot = xarray_slot_view.fromRaw(value_raw);
    const pointer_slot = xarray_slot_view.fromRaw(pointer_raw);
    const err_slot = xarray_slot_view.fromRaw(err_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, err_slot.kind());

    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(value_raw));
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(err_raw));
}
