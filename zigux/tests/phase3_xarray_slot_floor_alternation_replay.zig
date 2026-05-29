const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectValueSlot(raw: usize, expected_value: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
    try std.testing.expect(slot.isValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, expected_value), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

fn expectPointerSlot(raw: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(slot.isPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
}

test "xarray slot floor boundary alternates value and pointer before err_ptr takes precedence" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    try std.testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);

    try expectPointerSlot(err_ptr.err_floor - 7);
    try expectValueSlot(err_ptr.err_floor - 6, xa_value.safe_inline_limit - 2);
    try expectPointerSlot(err_ptr.err_floor - 5);
    try expectValueSlot(err_ptr.err_floor - 4, xa_value.safe_inline_limit - 1);
    try expectPointerSlot(err_ptr.err_floor - 3);
    try expectValueSlot(err_ptr.err_floor - 2, xa_value.safe_inline_limit);
    try expectPointerSlot(err_ptr.err_floor - 1);

    const floor_slot = xarray_slot_view.fromRaw(err_ptr.err_floor);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, floor_slot.kind());
    try std.testing.expectEqual(@as(?isize, -4095), floor_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), floor_slot.value());
    try std.testing.expectEqual(@as(?usize, null), floor_slot.pointerValue());
}

test "first rejected inline source lands exactly on the err_ptr floor" {
    const first_rejected_value = xa_value.safe_inline_limit + 1;
    const raw = (first_rejected_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(first_rejected_value));
    try std.testing.expectEqual(err_ptr.err_floor, raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
}
