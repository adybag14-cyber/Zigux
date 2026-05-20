const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectNullEquation() !void {
    const slot = xarray_slot_view.fromRaw(0);
    const rebuilt = xarray_slot_view.nullSlot();

    try testing.expectEqual(xarray_slot_view.SlotKind.null, slot.kind());
    try testing.expectEqual(@as(usize, 0), slot.rawValue());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try testing.expectEqual(@as(usize, 0), rebuilt.rawValue());
}

fn expectValueEquation(payload: usize) !void {
    const raw = try xa_value.makeValue(payload);
    const slot = xarray_slot_view.fromRaw(raw);
    const rebuilt = try xarray_slot_view.fromValue(payload);

    try testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
    try testing.expectEqual((payload << 1) | xa_value.value_tag_mask, raw);
    try testing.expectEqual(raw >> 1, slot.value().?);
    try testing.expectEqual(raw, rebuilt.rawValue());
    try testing.expect(raw < err_ptr.err_floor);
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

fn expectPointerEquation(raw: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);
    const rebuilt = xarray_slot_view.fromPointer(raw);

    try testing.expect(raw != 0);
    try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
    try testing.expect(raw < err_ptr.err_floor);
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try testing.expectEqual(raw, rebuilt.rawValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
}

fn expectErrEquation(code: isize) !void {
    const raw = err_ptr.fromErrorCode(code);
    const slot = xarray_slot_view.fromRaw(raw);
    const rebuilt = xarray_slot_view.fromErrorCode(code);

    try testing.expectEqual(@as(usize, @bitCast(code)), raw);
    try testing.expectEqual(code, @as(isize, @bitCast(raw)));
    try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try testing.expectEqual(@as(?isize, code), slot.errorCode());
    try testing.expectEqual(raw, rebuilt.rawValue());
    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "xarray-slot null and value lanes obey their direct decode equations" {
    try expectNullEquation();

    const payloads = [_]usize{ 0, 1, 29, xa_value.safe_inline_limit - 1, xa_value.safe_inline_limit };
    for (payloads) |payload| {
        try expectValueEquation(payload);
    }
}

test "xarray-slot pointer lane returns the raw unchanged on representative even raws" {
    const raws = [_]usize{ 2, 4, 0x20, err_ptr.err_floor - 5, err_ptr.err_floor - 3, err_ptr.err_floor - 1 };
    for (raws) |raw| {
        try expectPointerEquation(raw);
    }
}

test "xarray-slot err lane obeys the raw bitcast error equation across the live band" {
    const codes = [_]isize{ -4095, -2048, -17, -2, -1 };
    for (codes) |code| {
        try expectErrEquation(code);
    }
}
