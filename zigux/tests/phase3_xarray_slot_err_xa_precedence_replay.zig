const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "first rejected inline value aliases the err_ptr floor as an error slot" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(err_ptr.err_floor, raw);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "highest accepted inline value and the err-floor gap keep adjacent lanes distinct" {
    const value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const value_slot = xarray_slot_view.fromRaw(value_raw);
    const gap_raw = err_ptr.err_floor - 1;
    const gap_slot = xarray_slot_view.fromRaw(gap_raw);

    try std.testing.expectEqual(err_ptr.err_floor - 2, value_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try std.testing.expectEqual(@as(?isize, null), value_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), value_slot.pointerValue());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap_slot.kind());
    try std.testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), gap_slot.value());
    try std.testing.expectEqual(@as(?isize, null), gap_slot.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));
}

test "odd err_ptr samples do not leak through the xa_value decoder" {
    const error_codes = [_]isize{
        -@as(isize, @intCast(err_ptr.max_errno)),
        -4093,
        -17,
        -1,
    };

    for (error_codes) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect(!xa_value.isValue(raw));
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "constructor helpers preserve raw precedence immediately below and at the floor" {
    const value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const err_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try std.testing.expectEqual(err_ptr.err_floor - 2, value_slot.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());

    try std.testing.expectEqual(err_ptr.err_floor, err_slot.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, err_slot.kind());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), err_slot.errorCode());
    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1),
    );
}
