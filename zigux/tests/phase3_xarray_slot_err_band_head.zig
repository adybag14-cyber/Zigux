const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectErrHeadCase(code: isize, previous_raw: ?usize) !usize {
    const raw = err_ptr.fromErrorCode(code);
    const slot = xarray_slot_view.fromRaw(raw);
    const rebuilt = xarray_slot_view.fromErrorCode(code);

    try std.testing.expectEqual(raw, rebuilt.rawValue());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

    if ((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask) {
        try std.testing.expect(!xa_value.isValue(raw));
    }

    if (previous_raw) |prev| {
        try std.testing.expectEqual(prev + 1, raw);
    }

    return raw;
}

test "opening err_ptr raws stay contiguous and err-only at the xarray slot head" {
    const codes = [_]isize{ -4095, -4094, -4093, -4092 };
    var previous_raw: ?usize = null;

    for (codes) |code| {
        previous_raw = try expectErrHeadCase(code, previous_raw);
    }
}

test "err floor opening stays separated from the pointer-like gap below it" {
    const gap_raw = err_ptr.err_floor - 1;
    const gap_slot = xarray_slot_view.fromRaw(gap_raw);
    const first_err_slot = xarray_slot_view.fromRaw(err_ptr.err_floor);

    try std.testing.expectEqual(err_ptr.err_floor, gap_raw + 1);
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));
    try std.testing.expect(gap_slot.isPointer());
    try std.testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, null), gap_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), gap_slot.value());

    try std.testing.expect(first_err_slot.isErr());
    try std.testing.expectEqual(@as(?isize, -4095), first_err_slot.errorCode());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(err_ptr.err_floor));
}
