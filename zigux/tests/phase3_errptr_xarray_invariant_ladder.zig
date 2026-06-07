const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

fn expectSlot(
    raw: usize,
    expected_kind: SlotKind,
    expected_value: ?usize,
    expected_error: ?isize,
    expected_pointer: ?usize,
    expected_tagged: bool,
) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(expected_kind, slot.kind());
    try std.testing.expectEqual(expected_kind == .null, slot.isNull());
    try std.testing.expectEqual(expected_kind == .value, slot.isValue());
    try std.testing.expectEqual(expected_kind == .err, slot.isErr());
    try std.testing.expectEqual(expected_kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(expected_value, slot.value());
    try std.testing.expectEqual(expected_error, slot.errorCode());
    try std.testing.expectEqual(expected_pointer, slot.pointerValue());
    try std.testing.expectEqual(expected_tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(xarray_slot_view.isTaggedInternalEntry(raw), slot.isTaggedEntry());
}

test "err_ptr xa_value and slot helpers keep the core encoding ladder aligned" {
    const inline_zero = try xa_value.makeValue(0);
    const inline_one = try xa_value.makeValue(1);
    const inline_tail = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap = err_ptr.err_floor - 1;
    const err_floor = err_ptr.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const top_err = err_ptr.fromErrorCode(-1);

    try std.testing.expectEqual(@as(usize, 0), inline_zero - xa_value.value_tag_mask);
    try std.testing.expectEqual(inline_zero + 2, inline_one);
    try std.testing.expectEqual(err_ptr.err_floor - 2, inline_tail);
    try std.testing.expectEqual(inline_tail + 1, pointer_gap);
    try std.testing.expectEqual(pointer_gap + 1, err_floor);
    try std.testing.expectEqual(err_ptr.err_floor, err_floor);
    try std.testing.expect(top_err > err_floor);

    try std.testing.expect(xa_value.canRepresent(xa_value.safe_inline_limit));
    try std.testing.expect(!xa_value.canRepresent(xa_value.safe_inline_limit + 1));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(xa_value.safe_inline_limit + 1));

    try expectSlot(0, .null, null, null, null, false);
    try expectSlot(inline_zero, .value, 0, null, null, true);
    try expectSlot(inline_one, .value, 1, null, null, true);
    try expectSlot(inline_tail, .value, xa_value.safe_inline_limit, null, null, true);
    try expectSlot(pointer_gap, .pointer, null, null, pointer_gap, false);
    try expectSlot(err_floor, .err, null, -@as(isize, @intCast(err_ptr.max_errno)), null, true);
    try expectSlot(top_err, .err, null, -1, null, true);
}

test "public constructors agree with raw classification at each ladder rung" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_slot = xarray_slot_view.fromErrorCode(-12);

    try std.testing.expectEqual(try xa_value.makeValue(xa_value.safe_inline_limit), value_slot.rawValue());
    try std.testing.expectEqual(SlotKind.value, value_slot.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try std.testing.expectEqual(@as(?isize, null), value_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), value_slot.pointerValue());

    try std.testing.expectEqual(err_ptr.err_floor - 1, pointer_slot.rawValue());
    try std.testing.expectEqual(SlotKind.pointer, pointer_slot.kind());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), pointer_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), pointer_slot.value());
    try std.testing.expectEqual(@as(?isize, null), pointer_slot.errorCode());

    try std.testing.expectEqual(err_ptr.fromErrorCode(-12), err_slot.rawValue());
    try std.testing.expectEqual(SlotKind.err, err_slot.kind());
    try std.testing.expectEqual(@as(?isize, -12), err_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), err_slot.value());
    try std.testing.expectEqual(@as(?usize, null), err_slot.pointerValue());
}
