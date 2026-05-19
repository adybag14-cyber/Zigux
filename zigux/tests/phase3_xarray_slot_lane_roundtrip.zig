const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "raw null stays isolated from every rebuild path" {
    const slot = xarray_slot_view.fromRaw(0);
    const rebuilt = xarray_slot_view.nullSlot();

    try testing.expectEqual(xarray_slot_view.SlotKind.null, slot.kind());
    try testing.expect(slot.isNull());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isErr());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(usize, 0), rebuilt.rawValue());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "value lanes decode and rebuild back to the same tagged raw" {
    const cases = [_]usize{ 0, 29, xa_value.safe_inline_limit };

    inline for (cases) |value| {
        const raw = try xa_value.makeValue(value);
        const decoded = xarray_slot_view.fromRaw(raw);
        const rebuilt = try xarray_slot_view.fromValue(decoded.value().?);

        try testing.expectEqual(xarray_slot_view.SlotKind.value, decoded.kind());
        try testing.expectEqual(raw, rebuilt.rawValue());
        try testing.expectEqual(@as(?usize, value), decoded.value());
        try testing.expectEqual(@as(?isize, null), decoded.errorCode());
        try testing.expectEqual(@as(?usize, null), decoded.pointerValue());
    }
}

test "pointer-like lanes decode and rebuild without crossing tagged boundaries" {
    const cases = [_]usize{ 0x1000, err_ptr.err_floor - 1 };

    inline for (cases) |raw| {
        const decoded = xarray_slot_view.fromRaw(raw);
        const rebuilt = xarray_slot_view.fromPointer(decoded.pointerValue().?);

        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, decoded.kind());
        try testing.expectEqual(raw, rebuilt.rawValue());
        try testing.expectEqual(@as(?usize, raw), decoded.pointerValue());
        try testing.expectEqual(@as(?usize, null), decoded.value());
        try testing.expectEqual(@as(?isize, null), decoded.errorCode());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "err_ptr lanes decode and rebuild back to the same error raw" {
    const cases = [_]isize{ -1, -22, -4095 };

    inline for (cases) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const decoded = xarray_slot_view.fromRaw(raw);
        const rebuilt = xarray_slot_view.fromErrorCode(decoded.errorCode().?);

        try testing.expectEqual(xarray_slot_view.SlotKind.err, decoded.kind());
        try testing.expectEqual(raw, rebuilt.rawValue());
        try testing.expectEqual(@as(?isize, code), decoded.errorCode());
        try testing.expectEqual(@as(?usize, null), decoded.value());
        try testing.expectEqual(@as(?usize, null), decoded.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}
