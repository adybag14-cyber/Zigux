const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const errno_codes = [_]isize{
    -1,
    -2,
    -12,
    -22,
    -512,
    -@as(isize, @intCast(err_ptr.max_errno)),
};

test "errno slots preserve err_ptr identity through xarray slot decoding" {
    for (errno_codes) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromErrorCode(code);

        try std.testing.expectEqual(raw, slot.rawValue());
        try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect(!xa_value.isValue(raw));
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "errno slot raws stay contiguous and ordered inside the err lane" {
    var previous_raw = err_ptr.fromErrorCode(errno_codes[0]);
    var previous_code = errno_codes[0];

    for (errno_codes[1..]) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const code_delta = previous_code - code;
        const raw_delta = previous_raw - raw;

        try std.testing.expect(code_delta > 0);
        try std.testing.expectEqual(@as(usize, @intCast(code_delta)), raw_delta);
        try std.testing.expectEqual(code, err_ptr.toErrorCode(raw));

        previous_raw = raw;
        previous_code = code;
    }
}

test "errno slot neighbors do not leak into xa_value or pointer decoders" {
    const floor_slot = xarray_slot_view.fromRaw(err_ptr.err_floor);
    const before_floor = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);
    const before_top_err = xarray_slot_view.fromRaw(err_ptr.fromErrorCode(-1) - 1);
    const top_err = xarray_slot_view.fromRaw(err_ptr.fromErrorCode(-1));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, floor_slot.kind());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), floor_slot.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, before_floor.kind());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), before_floor.pointerValue());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, before_top_err.kind());
    try std.testing.expectEqual(@as(?isize, -2), before_top_err.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, top_err.kind());
    try std.testing.expectEqual(@as(?isize, -1), top_err.errorCode());
    try std.testing.expectEqual(@as(?usize, null), top_err.value());
    try std.testing.expectEqual(@as(?usize, null), top_err.pointerValue());
}
