const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "xarray err lane spans exactly the Linux errno band" {
    const first_error_raw = err_ptr.err_floor;
    const last_error_raw = err_ptr.fromErrorCode(-1);
    const err_band_span = (last_error_raw - first_error_raw) + 1;

    try std.testing.expectEqual(err_ptr.max_errno, err_band_span);

    const sample_offsets = [_]usize{ 0, 1, 127, 1023, err_ptr.max_errno - 2, err_ptr.max_errno - 1 };
    for (sample_offsets) |offset| {
        const raw = first_error_raw + offset;
        const expected_code = -@as(isize, @intCast(err_ptr.max_errno - offset));
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try std.testing.expect(slot.isErr());
        try std.testing.expect(!slot.isValue());
        try std.testing.expect(!slot.isPointer());
        try std.testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "raws immediately outside the err band stay outside the err decoder" {
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const highest_value_raw = err_ptr.err_floor - 2;
    const null_after_wrapped_top_raw: usize = 0;

    const pointer_gap = xarray_slot_view.fromRaw(pointer_gap_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap.kind());
    try std.testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap.pointerValue());
    try std.testing.expectEqual(@as(?isize, null), pointer_gap.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));

    const highest_value = xarray_slot_view.fromRaw(highest_value_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, highest_value.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), highest_value.value());
    try std.testing.expectEqual(@as(?isize, null), highest_value.errorCode());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(highest_value_raw));

    const null_slot = xarray_slot_view.fromRaw(null_after_wrapped_top_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.null, null_slot.kind());
    try std.testing.expectEqual(@as(?isize, null), null_slot.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(null_after_wrapped_top_raw));
}

test "public error constructor preserves every sampled band endpoint" {
    const codes = [_]isize{ -4095, -4094, -2048, -512, -2, -1 };

    for (codes) |code| {
        const slot = xarray_slot_view.fromErrorCode(code);

        try std.testing.expectEqual(err_ptr.fromErrorCode(code), slot.rawValue());
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}
