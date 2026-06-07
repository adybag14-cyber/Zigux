const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

fn expectClosedAccessors(
    slot: xarray_slot_view.SlotView,
    expected_value: ?usize,
    expected_error: ?isize,
    expected_pointer: ?usize,
) !void {
    try std.testing.expectEqual(expected_value, slot.value());
    try std.testing.expectEqual(expected_error, slot.errorCode());
    try std.testing.expectEqual(expected_pointer, slot.pointerValue());
}

test "pointer errno boundary preserves the last value, last pointer, and first err lanes" {
    const last_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const last_pointer_raw = err_ptr.err_floor - 1;
    const floor_raw = err_ptr.err_floor;
    const next_errno_raw = err_ptr.err_floor + 1;

    try std.testing.expectEqual(err_ptr.err_floor - 2, last_value_raw);
    try std.testing.expectEqual(last_value_raw + 1, last_pointer_raw);
    try std.testing.expectEqual(last_pointer_raw + 1, floor_raw);
    try std.testing.expectEqual(floor_raw + 1, next_errno_raw);

    const last_value = xarray_slot_view.fromRaw(last_value_raw);
    const last_pointer = xarray_slot_view.fromRaw(last_pointer_raw);
    const floor_err = xarray_slot_view.fromRaw(floor_raw);
    const next_errno = xarray_slot_view.fromRaw(next_errno_raw);

    try std.testing.expectEqual(SlotKind.value, last_value.kind());
    try expectClosedAccessors(last_value, xa_value.safe_inline_limit, null, null);
    try std.testing.expect(last_value.isTaggedEntry());

    try std.testing.expectEqual(SlotKind.pointer, last_pointer.kind());
    try expectClosedAccessors(last_pointer, null, null, last_pointer_raw);
    try std.testing.expect(!last_pointer.isTaggedEntry());

    try std.testing.expectEqual(SlotKind.err, floor_err.kind());
    try expectClosedAccessors(floor_err, null, -4095, null);
    try std.testing.expect(floor_err.isTaggedEntry());

    try std.testing.expectEqual(SlotKind.err, next_errno.kind());
    try expectClosedAccessors(next_errno, null, -4094, null);
    try std.testing.expect(next_errno.isTaggedEntry());
}

test "constructor rereads keep pointer gaps outside the err band and errno rows inside it" {
    const value_before_boundary = try xarray_slot_view.fromValue(xa_value.safe_inline_limit - 1);
    const gap_before_last_value_raw = value_before_boundary.rawValue() + 1;
    const pointer_before_floor = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const floor_err = xarray_slot_view.fromErrorCode(-4095);
    const top_err = xarray_slot_view.fromErrorCode(-1);

    try std.testing.expectEqual(SlotKind.pointer, xarray_slot_view.fromRaw(gap_before_last_value_raw).kind());
    try expectClosedAccessors(
        xarray_slot_view.fromRaw(gap_before_last_value_raw),
        null,
        null,
        gap_before_last_value_raw,
    );
    try std.testing.expect(!err_ptr.isErrValue(gap_before_last_value_raw));
    try std.testing.expect(!xarray_slot_view.fromRaw(gap_before_last_value_raw).isTaggedEntry());

    const reread_pointer = xarray_slot_view.fromRaw(pointer_before_floor.rawValue());
    try std.testing.expectEqual(SlotKind.pointer, reread_pointer.kind());
    try expectClosedAccessors(reread_pointer, null, null, err_ptr.err_floor - 1);
    try std.testing.expect(!err_ptr.isErrValue(reread_pointer.rawValue()));

    const reread_floor = xarray_slot_view.fromRaw(floor_err.rawValue());
    try std.testing.expectEqual(SlotKind.err, reread_floor.kind());
    try expectClosedAccessors(reread_floor, null, -4095, null);
    try std.testing.expect(err_ptr.isErrValue(reread_floor.rawValue()));

    const reread_top = xarray_slot_view.fromRaw(top_err.rawValue());
    try std.testing.expectEqual(SlotKind.err, reread_top.kind());
    try expectClosedAccessors(reread_top, null, -1, null);
    try std.testing.expect(err_ptr.isErrValue(reread_top.rawValue()));
}
