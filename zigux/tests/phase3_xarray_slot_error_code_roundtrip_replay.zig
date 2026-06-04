const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const errno_codes = [_]isize{
    -1,
    -2,
    -5,
    -12,
    -22,
    -4095,
};

fn expectErrorLane(slot: xarray_slot_view.SlotView, code: isize) !void {
    const raw = err_ptr.fromErrorCode(code);

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
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "error-code constructor round-trips representative Linux errno values" {
    for (errno_codes) |code| {
        try expectErrorLane(xarray_slot_view.fromErrorCode(code), code);
    }
}

test "raw error slots agree with public error-code construction" {
    for (errno_codes) |code| {
        const constructed = xarray_slot_view.fromErrorCode(code);
        const decoded = xarray_slot_view.fromRaw(constructed.rawValue());

        try expectErrorLane(decoded, code);
        try std.testing.expectEqual(constructed.kind(), decoded.kind());
        try std.testing.expectEqual(constructed.errorCode(), decoded.errorCode());
    }
}

test "low-bit tagged error raws stay out of the xa_value lane" {
    const odd_error_codes = [_]isize{ -1, -5, -4095 };

    for (odd_error_codes) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
        try std.testing.expect(slot.isErr());
        try std.testing.expect(!slot.isValue());
        try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
    }
}

test "the gap below the err floor remains pointer-like beside error-code slots" {
    const gap = err_ptr.err_floor - 1;
    const gap_slot = xarray_slot_view.fromRaw(gap);
    const floor_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try std.testing.expect(gap_slot.isPointer());
    try std.testing.expect(!gap_slot.isErr());
    try std.testing.expectEqual(@as(?usize, gap), gap_slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, null), gap_slot.errorCode());

    try expectErrorLane(floor_slot, -@as(isize, @intCast(err_ptr.max_errno)));
    try std.testing.expectEqual(err_ptr.err_floor, floor_slot.rawValue());
}
