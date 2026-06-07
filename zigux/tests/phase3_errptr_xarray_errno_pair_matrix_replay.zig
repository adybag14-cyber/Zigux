const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ErrnoPair = struct {
    left: isize,
    right: isize,
};

const pairs = [_]ErrnoPair{
    .{ .left = -4095, .right = -4094 },
    .{ .left = -2049, .right = -2048 },
    .{ .left = -513, .right = -512 },
    .{ .left = -23, .right = -22 },
    .{ .left = -2, .right = -1 },
};

fn expectErrorSlot(code: isize) !usize {
    const raw = err_ptr.fromErrorCode(code);
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!err_ptr.isOkValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    return raw;
}

test "adjacent errno pairs keep one-raw spacing and exact signed decoding" {
    for (pairs) |pair| {
        const left_raw = try expectErrorSlot(pair.left);
        const right_raw = try expectErrorSlot(pair.right);

        try std.testing.expectEqual(left_raw + 1, right_raw);
        try std.testing.expectEqual(pair.left + 1, pair.right);
        try std.testing.expectEqual(pair.left, err_ptr.toErrorCode(left_raw));
        try std.testing.expectEqual(pair.right, err_ptr.toErrorCode(right_raw));
    }
}

test "errno pair constructors match raw slot decoding" {
    for (pairs) |pair| {
        const left_from_raw = xarray_slot_view.fromRaw(err_ptr.fromErrorCode(pair.left));
        const right_from_raw = xarray_slot_view.fromRaw(err_ptr.fromErrorCode(pair.right));
        const left_from_constructor = xarray_slot_view.fromErrorCode(pair.left);
        const right_from_constructor = xarray_slot_view.fromErrorCode(pair.right);

        try std.testing.expectEqual(left_from_raw.rawValue(), left_from_constructor.rawValue());
        try std.testing.expectEqual(right_from_raw.rawValue(), right_from_constructor.rawValue());
        try std.testing.expectEqual(left_from_raw.kind(), left_from_constructor.kind());
        try std.testing.expectEqual(right_from_raw.kind(), right_from_constructor.kind());
        try std.testing.expectEqual(left_from_raw.errorCode(), left_from_constructor.errorCode());
        try std.testing.expectEqual(right_from_raw.errorCode(), right_from_constructor.errorCode());
    }
}

test "errno-pair neighbors stay separated from value and pointer lanes" {
    const accepted_ceiling_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const floor_raw = err_ptr.fromErrorCode(-4095);

    try std.testing.expectEqual(err_ptr.err_floor - 2, accepted_ceiling_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, pointer_gap_raw);
    try std.testing.expectEqual(err_ptr.err_floor, floor_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, xarray_slot_view.fromRaw(accepted_ceiling_raw).kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, xarray_slot_view.fromRaw(pointer_gap_raw).kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, xarray_slot_view.fromRaw(floor_raw).kind());

    try std.testing.expect(!err_ptr.isErrValue(accepted_ceiling_raw));
    try std.testing.expect(!err_ptr.isErrValue(pointer_gap_raw));
    try std.testing.expect(err_ptr.isErrValue(floor_raw));
}
