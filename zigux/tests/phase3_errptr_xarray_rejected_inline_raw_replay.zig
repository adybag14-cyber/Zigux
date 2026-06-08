const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const rejected_values = [_]usize{
    xa_value.safe_inline_limit + 1,
    xa_value.safe_inline_limit + 2,
    xa_value.safe_inline_limit + 17,
    xa_value.safe_inline_limit + 255,
    xa_value.safe_inline_limit + 1024,
    (std.math.maxInt(usize) >> 1) - 2,
};

fn rawFromUncheckedInline(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

fn expectRejectedInlineDecodesAsErr(value: usize) !void {
    try std.testing.expect(!xa_value.canRepresent(value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(value));

    const raw = rawFromUncheckedInline(value);
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!err_ptr.isOkValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, @bitCast(raw)), slot.errorCode());
    try std.testing.expectEqual(raw, err_ptr.fromErrorCode(slot.errorCode().?));
}

test "rejected inline values decode through the xarray raw error lane" {
    for (rejected_values) |value| {
        try expectRejectedInlineDecodesAsErr(value);
    }
}

test "accepted inline ceiling and rejected floor remain adjacent but disjoint" {
    const accepted_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const rejected_raw = rawFromUncheckedInline(xa_value.safe_inline_limit + 1);
    const accepted_slot = xarray_slot_view.fromRaw(accepted_raw);
    const rejected_slot = xarray_slot_view.fromRaw(rejected_raw);

    try std.testing.expectEqual(err_ptr.err_floor - 2, accepted_raw);
    try std.testing.expectEqual(err_ptr.err_floor, rejected_raw);
    try std.testing.expectEqual(@as(usize, 2), rejected_raw - accepted_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, accepted_slot.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), accepted_slot.value());
    try std.testing.expectEqual(@as(?isize, null), accepted_slot.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, rejected_slot.kind());
    try std.testing.expectEqual(@as(?usize, null), rejected_slot.value());
    try std.testing.expectEqual(@as(?isize, -4095), rejected_slot.errorCode());
}
