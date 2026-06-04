const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "odd top errno raws keep err precedence over xa_value tag shape" {
    const odd_error_codes = [_]isize{ -1, -3, -5, -4095 };

    for (odd_error_codes) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectEqual(xa_value.value_tag_mask, raw & xa_value.value_tag_mask);
        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect(!xa_value.isValue(raw));
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try std.testing.expect(slot.isErr());
        try std.testing.expect(!slot.isValue());
        try std.testing.expect(!slot.isPointer());
        try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "top errno constructor and raw decoder agree across adjacent codes" {
    const error_codes = [_]isize{ -1, -2, -3, -4, -5, -6, -7, -8 };

    for (error_codes) |code| {
        const raw_slot = xarray_slot_view.fromRaw(err_ptr.fromErrorCode(code));
        const constructed_slot = xarray_slot_view.fromErrorCode(code);

        try std.testing.expectEqual(raw_slot.rawValue(), constructed_slot.rawValue());
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, raw_slot.kind());
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, constructed_slot.kind());
        try std.testing.expectEqual(@as(?isize, code), raw_slot.errorCode());
        try std.testing.expectEqual(@as(?isize, code), constructed_slot.errorCode());
    }
}

test "accepted inline value beside err floor remains the only low-bit value lane" {
    const value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const floor_raw = err_ptr.err_floor;
    const floor_slot = xarray_slot_view.fromRaw(floor_raw);
    const value_slot = xarray_slot_view.fromRaw(value_raw);

    try std.testing.expectEqual(err_ptr.err_floor - 2, value_raw);
    try std.testing.expectEqual(xa_value.value_tag_mask, value_raw & xa_value.value_tag_mask);
    try std.testing.expectEqual(xa_value.value_tag_mask, floor_raw & xa_value.value_tag_mask);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try std.testing.expectEqual(@as(?isize, null), value_slot.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, floor_slot.kind());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), floor_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), floor_slot.value());
}
