const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn rejectedInlineRaw(offset: usize) usize {
    const rejected_value = xa_value.safe_inline_limit + offset;
    return (rejected_value << 1) | xa_value.value_tag_mask;
}

fn expectErrSlot(raw: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, err_ptr.toErrorCode(raw)), slot.errorCode());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "rejected inline values hand off to the err_ptr slot lane" {
    const offsets = [_]usize{ 1, 2, 64, 2048 };

    inline for (offsets) |offset| {
        const rejected_value = xa_value.safe_inline_limit + offset;
        const raw = rejectedInlineRaw(offset);

        try std.testing.expect(!xa_value.canRepresent(rejected_value));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected_value));
        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect(!xa_value.isValue(raw));
        try expectErrSlot(raw);
    }
}

test "err-band neighbors beside rejected inline aliases stay out of value and pointer lanes" {
    const offsets = [_]usize{ 1, 2, 64 };

    inline for (offsets) |offset| {
        const raw = rejectedInlineRaw(offset) + 1;

        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect(!xa_value.isValue(raw));
        try expectErrSlot(raw);
    }
}
