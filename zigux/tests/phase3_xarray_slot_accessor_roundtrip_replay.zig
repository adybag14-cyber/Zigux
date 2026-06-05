const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectOnlyValueRoundTrips(raw: usize, expected_value: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(slot.isValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(@as(?usize, expected_value), slot.value());
    try std.testing.expectEqual(raw, try xa_value.makeValue(slot.value().?));
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

fn expectOnlyErrorRoundTrips(raw: usize, expected_code: isize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(slot.isErr());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
    try std.testing.expectEqual(raw, err_ptr.fromErrorCode(slot.errorCode().?));
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

fn expectOnlyPointerRoundTrips(raw: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(slot.isPointer());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try std.testing.expectEqual(raw, slot.pointerValue().?);
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
}

test "slot accessors round-trip only their owning xarray lane" {
    try expectOnlyValueRoundTrips(try xa_value.makeValue(0), 0);
    try expectOnlyValueRoundTrips(try xa_value.makeValue(29), 29);
    try expectOnlyValueRoundTrips(try xa_value.makeValue(xa_value.safe_inline_limit), xa_value.safe_inline_limit);
    try expectOnlyValueRoundTrips(err_ptr.err_floor - 2, xa_value.safe_inline_limit);

    try expectOnlyPointerRoundTrips(0x1000);
    try expectOnlyPointerRoundTrips(err_ptr.err_floor - 3);
    try expectOnlyPointerRoundTrips(err_ptr.err_floor - 1);

    try expectOnlyErrorRoundTrips(err_ptr.err_floor, -4095);
    try expectOnlyErrorRoundTrips(err_ptr.fromErrorCode(-2048), -2048);
    try expectOnlyErrorRoundTrips(err_ptr.fromErrorCode(-1), -1);
}

test "null and rejected inline aliases keep non-owning accessors closed" {
    const null_slot = xarray_slot_view.nullSlot();
    try std.testing.expect(null_slot.isNull());
    try std.testing.expectEqual(@as(usize, 0), null_slot.rawValue());
    try std.testing.expectEqual(@as(?usize, null), null_slot.value());
    try std.testing.expectEqual(@as(?isize, null), null_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), null_slot.pointerValue());

    const rejected_value = xa_value.safe_inline_limit + 1;
    const rejected_alias_raw = (rejected_value << 1) | xa_value.value_tag_mask;
    try std.testing.expectEqual(err_ptr.err_floor, rejected_alias_raw);
    try expectOnlyErrorRoundTrips(rejected_alias_raw, -4095);

    const top_rejected_value = (err_ptr.fromErrorCode(-1) >> 1);
    const top_rejected_alias_raw = (top_rejected_value << 1) | xa_value.value_tag_mask;
    try std.testing.expectEqual(err_ptr.fromErrorCode(-1), top_rejected_alias_raw);
    try expectOnlyErrorRoundTrips(top_rejected_alias_raw, -1);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(top_rejected_value));
}
