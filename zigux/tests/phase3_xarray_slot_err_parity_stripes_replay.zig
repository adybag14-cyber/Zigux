const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectErrSlot(code: isize, has_value_tag_bit: bool) !void {
    const raw = err_ptr.fromErrorCode(code);
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(has_value_tag_bit, (raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "odd err_ptr stripe keeps err precedence over xa_value tag" {
    const odd_codes = [_]isize{ -4095, -3, -1 };

    for (odd_codes) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const would_be_value = raw >> 1;

        try std.testing.expect(would_be_value > xa_value.safe_inline_limit);
        try std.testing.expect(!xa_value.canRepresent(would_be_value));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(would_be_value));
        try expectErrSlot(code, true);
    }
}

test "even err_ptr stripe stays err without xa_value tag" {
    const even_codes = [_]isize{ -4094, -22, -2 };

    for (even_codes) |code| {
        const raw = err_ptr.fromErrorCode(code);

        try std.testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
        try std.testing.expect(!xa_value.isValue(raw));
        try expectErrSlot(code, false);
    }
}

test "safe value ceiling hands off through pointer gap into err floor" {
    const top_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const floor_raw = err_ptr.err_floor;

    const top_value = xarray_slot_view.fromRaw(top_value_raw);
    const gap = xarray_slot_view.fromRaw(gap_raw);
    const floor = xarray_slot_view.fromRaw(floor_raw);

    try std.testing.expectEqual(err_ptr.err_floor - 2, top_value_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, top_value.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), top_value.value());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap.kind());
    try std.testing.expectEqual(@as(?usize, gap_raw), gap.pointerValue());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, floor.kind());
    try std.testing.expectEqual(@as(?isize, -4095), floor.errorCode());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(floor_raw));
}
