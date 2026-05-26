const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ValueCase = struct {
    raw: usize,
    decoded_value: usize,
};

test "ok-side parity lanes keep even raws pointer-like and odd raws xa_value-tagged" {
    const pointer_cases = [_]usize{
        2,
        64,
        err_ptr.err_floor - 1,
    };

    const value_cases = [_]ValueCase{
        .{ .raw = try xa_value.makeValue(0), .decoded_value = 0 },
        .{ .raw = try xa_value.makeValue(29), .decoded_value = 29 },
        .{ .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .decoded_value = xa_value.safe_inline_limit },
    };

    for (pointer_cases) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(err_ptr.isOkValue(raw));
        try testing.expect(!err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
        try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());
    }

    for (value_cases) |case| {
        const slot = xarray_slot_view.fromRaw(case.raw);

        try testing.expect(err_ptr.isOkValue(case.raw));
        try testing.expect(!err_ptr.isErrValue(case.raw));
        try testing.expect(xa_value.isValue(case.raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
        try testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
        try testing.expectEqual(@as(?usize, case.decoded_value), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());
    }
}

test "err-side parity closes xa_value decoding even when the low bit stays set" {
    const err_cases = [_]struct {
        raw: usize,
        code: isize,
    }{
        .{ .raw = err_ptr.err_floor, .code = -4095 },
        .{ .raw = err_ptr.err_floor + 1, .code = -4094 },
        .{ .raw = err_ptr.fromErrorCode(-1), .code = -1 },
    };

    for (err_cases) |case| {
        const slot = xarray_slot_view.fromRaw(case.raw);

        try testing.expect(err_ptr.isErrValue(case.raw));
        try testing.expect(!err_ptr.isOkValue(case.raw));
        try testing.expect(!xa_value.isValue(case.raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expectEqual(@as(?isize, case.code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "boundary adjacency keeps the last odd ok raw in the value lane and the next odd raw in err space" {
    const last_value_raw = err_ptr.err_floor - 2;
    const first_err_raw = err_ptr.err_floor;

    const last_value_slot = xarray_slot_view.fromRaw(last_value_raw);
    const first_err_slot = xarray_slot_view.fromRaw(first_err_raw);

    try testing.expect(last_value_raw & xa_value.value_tag_mask == xa_value.value_tag_mask);
    try testing.expect(err_ptr.isOkValue(last_value_raw));
    try testing.expect(xa_value.isValue(last_value_raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.value, last_value_slot.kind());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), last_value_slot.value());

    try testing.expect(first_err_raw & xa_value.value_tag_mask == xa_value.value_tag_mask);
    try testing.expect(err_ptr.isErrValue(first_err_raw));
    try testing.expect(!xa_value.isValue(first_err_raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.err, first_err_slot.kind());
    try testing.expectEqual(@as(?isize, -4095), first_err_slot.errorCode());
}
