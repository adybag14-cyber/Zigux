const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const idr_slot_view = @import("idr_slot_view");

test "idr slot view keeps null slots explicit" {
    const slot = idr_slot_view.nullSlot();

    try testing.expect(slot.isNull());
    try testing.expect(!slot.isPointer());
    try testing.expect(!slot.isInvalid());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "idr slot view preserves ordinary aligned pointers" {
    const raw: usize = 0x1000;
    const slot = idr_slot_view.fromPointer(raw);

    try testing.expect(!slot.isNull());
    try testing.expect(slot.isPointer());
    try testing.expect(!slot.isInvalid());
    try testing.expect(idr_slot_view.isDirectPointerEncoding(raw));
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
}

test "idr slot view keeps xa_value entries out of the pointer lane" {
    const raw = try xa_value.makeValue(29);
    const slot = idr_slot_view.fromRaw(raw);

    try testing.expect(!slot.isNull());
    try testing.expect(!slot.isPointer());
    try testing.expect(slot.isInvalid());
    try testing.expect(!idr_slot_view.isDirectPointerEncoding(raw));
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "idr slot view keeps err_ptr entries out of the pointer lane" {
    const raw = err_ptr.fromErrorCode(-22);
    const slot = idr_slot_view.fromRaw(raw);

    try testing.expect(!slot.isNull());
    try testing.expect(!slot.isPointer());
    try testing.expect(slot.isInvalid());
    try testing.expect(!idr_slot_view.isDirectPointerEncoding(raw));
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "idr slot view keeps the last ok raw word before err_ptr as pointer-like" {
    const raw = err_ptr.err_floor - 1;
    const slot = idr_slot_view.fromRaw(raw);

    try testing.expect(!slot.isNull());
    try testing.expect(slot.isPointer());
    try testing.expect(!slot.isInvalid());
    try testing.expect(idr_slot_view.isDirectPointerEncoding(raw));
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
}

test "idr slot view rejects low-bit tagged pointer encodings" {
    const raw: usize = 0x1001;
    const slot = idr_slot_view.fromRaw(raw);

    try testing.expect(!slot.isNull());
    try testing.expect(!slot.isPointer());
    try testing.expect(slot.isInvalid());
    try testing.expect(!idr_slot_view.isDirectPointerEncoding(raw));
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}
