const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectTopErrSlot(code: isize) !void {
    const raw = err_ptr.fromErrorCode(code);
    const slot = xarray_slot_view.fromRaw(raw);
    const magnitude: usize = @intCast(-code);

    try std.testing.expectEqual(std.math.maxInt(usize) - (magnitude - 1), raw);
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

test "top err_ptr neighbor raws stay contiguous through usize max" {
    const codes = [_]isize{ -6, -5, -4, -3, -2, -1 };

    for (codes, 0..) |code, index| {
        const raw = err_ptr.fromErrorCode(code);

        try expectTopErrSlot(code);
        try std.testing.expectEqual(err_ptr.fromErrorCode(-6) + index, raw);
    }

    try std.testing.expectEqual(std.math.maxInt(usize), err_ptr.fromErrorCode(-1));
}

test "top err_ptr neighbors keep xa_value closed on both tag parities" {
    const codes = [_]isize{ -6, -5, -4, -3, -2, -1 };

    for (codes) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const would_be_value = raw >> 1;

        try std.testing.expect(would_be_value > xa_value.safe_inline_limit);
        try std.testing.expect(!xa_value.canRepresent(would_be_value));
        try std.testing.expect(!xa_value.isValue(raw));
        if ((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask) {
            try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(would_be_value));
        }
    }
}

test "top err constructor matches raw decoder at the upper boundary" {
    const top_from_raw = xarray_slot_view.fromRaw(std.math.maxInt(usize));
    const top_from_code = xarray_slot_view.fromErrorCode(-1);
    const next_lower = xarray_slot_view.fromRaw(std.math.maxInt(usize) - 1);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, top_from_raw.kind());
    try std.testing.expectEqual(top_from_raw.rawValue(), top_from_code.rawValue());
    try std.testing.expectEqual(@as(?isize, -1), top_from_raw.errorCode());
    try std.testing.expectEqual(@as(?isize, -1), top_from_code.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, next_lower.kind());
    try std.testing.expectEqual(@as(?isize, -2), next_lower.errorCode());
    try std.testing.expectEqual(@as(?usize, null), next_lower.value());
    try std.testing.expectEqual(@as(?usize, null), next_lower.pointerValue());
}
