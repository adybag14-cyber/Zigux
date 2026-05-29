const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ErrCase = struct {
    code: isize,
    raw: usize,
};

fn expectErrSlot(case: ErrCase) !void {
    const slot = xarray_slot_view.fromErrorCode(case.code);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?isize, case.code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(err_ptr.isErrValue(slot.rawValue()));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(slot.rawValue()));
}

test "xarray err-code constructor preserves the Linux errno ladder" {
    const cases = [_]ErrCase{
        .{ .code = -4095, .raw = err_ptr.err_floor },
        .{ .code = -4094, .raw = err_ptr.err_floor + 1 },
        .{ .code = -2048, .raw = @bitCast(@as(isize, -2048)) },
        .{ .code = -512, .raw = @bitCast(@as(isize, -512)) },
        .{ .code = -22, .raw = @bitCast(@as(isize, -22)) },
        .{ .code = -1, .raw = @bitCast(@as(isize, -1)) },
    };

    for (cases) |case| {
        try expectErrSlot(case);
        try std.testing.expectEqual(case.code, err_ptr.toErrorCode(case.raw));
    }
}

test "err-code ladder leaves adjacent non-err lanes closed" {
    const below_floor = err_ptr.err_floor - 1;
    const top_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const inline_zero = try xarray_slot_view.fromValue(0);
    const pointer_slot = xarray_slot_view.fromPointer(0x2000);

    try std.testing.expectEqual(err_ptr.err_floor - 2, top_value_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, xarray_slot_view.fromRaw(below_floor).kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, xarray_slot_view.fromRaw(top_value_raw).kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, inline_zero.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());

    try std.testing.expectEqual(@as(?isize, null), xarray_slot_view.fromRaw(below_floor).errorCode());
    try std.testing.expectEqual(@as(?isize, null), xarray_slot_view.fromRaw(top_value_raw).errorCode());
    try std.testing.expectEqual(@as(?isize, null), inline_zero.errorCode());
    try std.testing.expectEqual(@as(?isize, null), pointer_slot.errorCode());
}
