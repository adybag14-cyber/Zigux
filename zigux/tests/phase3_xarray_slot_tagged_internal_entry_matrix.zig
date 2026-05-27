const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectTaggedMatrix(
    raw: usize,
    expected_tagged: bool,
    expected_kind: xarray_slot_view.SlotKind,
) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(expected_tagged, xarray_slot_view.isTaggedInternalEntry(raw));
    try std.testing.expectEqual(expected_kind, slot.kind());
    try std.testing.expectEqual(expected_tagged, slot.kind() == .value or slot.kind() == .err);
}

test "tagged internal entry helper matches slot classification across representative raws" {
    try expectTaggedMatrix(0, false, .null);
    try expectTaggedMatrix(1, true, .value);
    try expectTaggedMatrix(try xa_value.makeValue(7), true, .value);
    try expectTaggedMatrix(try xa_value.makeValue(xa_value.safe_inline_limit), true, .value);
    try expectTaggedMatrix(err_ptr.err_floor - 2, true, .value);
    try expectTaggedMatrix(err_ptr.err_floor - 1, false, .pointer);
    try expectTaggedMatrix(err_ptr.err_floor, true, .err);
    try expectTaggedMatrix(err_ptr.fromErrorCode(-22), true, .err);
    try expectTaggedMatrix(err_ptr.fromErrorCode(-2), true, .err);
    try expectTaggedMatrix(err_ptr.fromErrorCode(-1), true, .err);
}

test "the seam from last inline value to pointer gap to err band stays explicit" {
    const last_inline = err_ptr.err_floor - 2;
    const pointer_gap = err_ptr.err_floor - 1;
    const err_floor = err_ptr.err_floor;

    try std.testing.expectEqual(last_inline, try xa_value.makeValue(xa_value.safe_inline_limit));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, xarray_slot_view.fromRaw(last_inline).kind());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(last_inline));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, xarray_slot_view.fromRaw(pointer_gap).kind());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, xarray_slot_view.fromRaw(err_floor).kind());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(err_floor));
}

test "constructor helpers land in the same tagged versus pointer lanes" {
    const null_slot = xarray_slot_view.nullSlot();
    const value_slot = try xarray_slot_view.fromValue(29);
    const err_slot = xarray_slot_view.fromErrorCode(-22);
    const pointer_slot = xarray_slot_view.fromPointer(0x1000);

    try std.testing.expectEqual(false, xarray_slot_view.isTaggedInternalEntry(null_slot.rawValue()));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.null, null_slot.kind());

    try std.testing.expectEqual(true, xarray_slot_view.isTaggedInternalEntry(value_slot.rawValue()));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());

    try std.testing.expectEqual(true, xarray_slot_view.isTaggedInternalEntry(err_slot.rawValue()));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, err_slot.kind());

    try std.testing.expectEqual(false, xarray_slot_view.isTaggedInternalEntry(pointer_slot.rawValue()));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
}

test "err floor alias from the first rejected xa_value still stays in the err lane" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const alias_raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(alias_raw);

    try std.testing.expectEqual(err_ptr.err_floor, alias_raw);
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(alias_raw));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, -4095), slot.errorCode());
}
