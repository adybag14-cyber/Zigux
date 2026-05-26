const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectSlot(
    slot: xarray_slot_view.SlotView,
    expected_kind: xarray_slot_view.SlotKind,
    expected_raw: usize,
    expected_value: ?usize,
    expected_error: ?isize,
    expected_pointer: ?usize,
    expected_tagged: bool,
) !void {
    try testing.expectEqual(expected_kind, slot.kind());
    try testing.expectEqual(expected_raw, slot.rawValue());
    try testing.expectEqual(expected_value, slot.value());
    try testing.expectEqual(expected_error, slot.errorCode());
    try testing.expectEqual(expected_pointer, slot.pointerValue());
    try testing.expectEqual(expected_kind == .null, slot.isNull());
    try testing.expectEqual(expected_kind == .value, slot.isValue());
    try testing.expectEqual(expected_kind == .err, slot.isErr());
    try testing.expectEqual(expected_kind == .pointer, slot.isPointer());
    try testing.expectEqual(expected_tagged, xarray_slot_view.isTaggedInternalEntry(expected_raw));
}

test "constructor matrix keeps the value-gap-err seam ordered and explicit" {
    const null_slot = xarray_slot_view.nullSlot();
    const inline_zero_slot = try xarray_slot_view.fromValue(0);
    const inline_limit_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const gap_slot = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const err_top_slot = xarray_slot_view.fromErrorCode(-1);
    const pointer_slot = xarray_slot_view.fromPointer(0x1000);

    try testing.expectEqual(@as(usize, 0), null_slot.rawValue());
    try testing.expectEqual(@as(usize, 1), inline_zero_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit_slot.rawValue());
    try testing.expectEqual(inline_limit_slot.rawValue() + 1, gap_slot.rawValue());
    try testing.expectEqual(gap_slot.rawValue() + 1, err_floor_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor, err_floor_slot.rawValue());
    try testing.expect(err_top_slot.rawValue() > err_floor_slot.rawValue());

    try expectSlot(null_slot, .null, 0, null, null, null, false);
    try expectSlot(inline_zero_slot, .value, 1, 0, null, null, true);
    try expectSlot(
        inline_limit_slot,
        .value,
        err_ptr.err_floor - 2,
        xa_value.safe_inline_limit,
        null,
        null,
        true,
    );
    try expectSlot(
        gap_slot,
        .pointer,
        err_ptr.err_floor - 1,
        null,
        null,
        err_ptr.err_floor - 1,
        false,
    );
    try expectSlot(err_floor_slot, .err, err_ptr.err_floor, null, -4095, null, true);
    try expectSlot(err_top_slot, .err, err_ptr.fromErrorCode(-1), null, -1, null, true);
    try expectSlot(pointer_slot, .pointer, 0x1000, null, null, 0x1000, false);
}

test "rejected inline constructor boundary converges on the same raw as err floor" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const overlapping_slot = xarray_slot_view.fromRaw(overlapping_raw);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-4095);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(overlapping_value));
    try testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try testing.expectEqual(err_floor_slot.rawValue(), overlapping_slot.rawValue());
    try expectSlot(overlapping_slot, .err, err_ptr.err_floor, null, -4095, null, true);
    try expectSlot(err_floor_slot, .err, err_ptr.err_floor, null, -4095, null, true);
}

test "constructor and raw paths agree on tagged ownership around the seam" {
    const cases = [_]struct {
        raw: usize,
        expected_kind: xarray_slot_view.SlotKind,
        expected_value: ?usize,
        expected_error: ?isize,
        expected_pointer: ?usize,
        expected_tagged: bool,
    }{
        .{ .raw = try xa_value.makeValue(29), .expected_kind = .value, .expected_value = 29, .expected_error = null, .expected_pointer = null, .expected_tagged = true },
        .{ .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .expected_kind = .value, .expected_value = xa_value.safe_inline_limit, .expected_error = null, .expected_pointer = null, .expected_tagged = true },
        .{ .raw = err_ptr.err_floor - 1, .expected_kind = .pointer, .expected_value = null, .expected_error = null, .expected_pointer = err_ptr.err_floor - 1, .expected_tagged = false },
        .{ .raw = err_ptr.fromErrorCode(-22), .expected_kind = .err, .expected_value = null, .expected_error = -22, .expected_pointer = null, .expected_tagged = true },
        .{ .raw = err_ptr.fromErrorCode(-1), .expected_kind = .err, .expected_value = null, .expected_error = -1, .expected_pointer = null, .expected_tagged = true },
    };

    inline for (cases) |case| {
        try expectSlot(
            xarray_slot_view.fromRaw(case.raw),
            case.expected_kind,
            case.raw,
            case.expected_value,
            case.expected_error,
            case.expected_pointer,
            case.expected_tagged,
        );
    }
}
