const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectSlot(
    raw: usize,
    expected_kind: xarray_slot_view.SlotKind,
    expected_value: ?usize,
    expected_error: ?isize,
    expected_pointer: ?usize,
) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectEqual(expected_kind, slot.kind());
    try testing.expectEqual(expected_value, slot.value());
    try testing.expectEqual(expected_error, slot.errorCode());
    try testing.expectEqual(expected_pointer, slot.pointerValue());
    try testing.expectEqual(expected_kind == .null, slot.isNull());
    try testing.expectEqual(expected_kind == .value, slot.isValue());
    try testing.expectEqual(expected_kind == .err, slot.isErr());
    try testing.expectEqual(expected_kind == .pointer, slot.isPointer());
}

test "value-gap-err boundary ladder stays explicit across adjacent raw encodings" {
    const inline_zero_raw = try xa_value.makeValue(0);
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const err_floor_raw = err_ptr.err_floor;
    const err_top_raw = err_ptr.fromErrorCode(-1);

    try testing.expectEqual(@as(usize, 1), inline_zero_raw);
    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);
    try testing.expectEqual(err_ptr.err_floor, inline_limit_raw + 2);
    try testing.expectEqual(err_ptr.err_floor, err_floor_raw);
    try testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(err_floor_raw));
    try testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(err_top_raw));

    try expectSlot(inline_zero_raw, .value, 0, null, null);
    try expectSlot(inline_limit_raw, .value, xa_value.safe_inline_limit, null, null);
    try expectSlot(gap_raw, .pointer, null, null, gap_raw);
    try expectSlot(err_floor_raw, .err, null, -4095, null);
    try expectSlot(err_top_raw, .err, null, -1, null);
}

test "first rejected inline value aliases the err floor and stays in the err lane" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
    try testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(overlapping_raw));
    try expectSlot(overlapping_raw, .err, null, -4095, null);
}

test "tagged-internal classification only covers xa_value and err_ptr bands" {
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const pointer_like_raw: usize = 0x1000;

    try testing.expect(xarray_slot_view.isTaggedInternalEntry(try xa_value.makeValue(29)));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(err_ptr.fromErrorCode(-12)));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(0));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_like_raw));

    try expectSlot(0, .null, null, null, null);
    try expectSlot(pointer_like_raw, .pointer, null, null, pointer_like_raw);
}
