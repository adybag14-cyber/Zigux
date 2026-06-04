const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectErrSlot(code: isize) !void {
    const raw = err_ptr.fromErrorCode(code);
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "xarray slot decoding gives err_ptr encodings precedence over xa_value tags" {
    try expectErrSlot(-1);
    try expectErrSlot(-12);
    try expectErrSlot(-22);
    try expectErrSlot(-4094);
    try expectErrSlot(-4095);
}

test "near-floor values keep the value gap and err floor distinct" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const err_floor_raw = err_ptr.err_floor;

    try std.testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, xarray_slot_view.fromRaw(inline_limit_raw).kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), xarray_slot_view.fromRaw(inline_limit_raw).value());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, xarray_slot_view.fromRaw(gap_raw).kind());
    try std.testing.expectEqual(@as(?usize, gap_raw), xarray_slot_view.fromRaw(gap_raw).pointerValue());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, xarray_slot_view.fromRaw(err_floor_raw).kind());
    try std.testing.expectEqual(@as(?isize, -4095), xarray_slot_view.fromRaw(err_floor_raw).errorCode());
    try std.testing.expect(!xa_value.isValue(err_floor_raw));
}
