const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectAccessors(
    slot: xarray_slot_view.SlotView,
    expected_kind: xarray_slot_view.SlotKind,
    expected_value: ?usize,
    expected_error: ?isize,
    expected_pointer: ?usize,
) !void {
    try std.testing.expectEqual(expected_kind, slot.kind());
    try std.testing.expectEqual(expected_value, slot.value());
    try std.testing.expectEqual(expected_error, slot.errorCode());
    try std.testing.expectEqual(expected_pointer, slot.pointerValue());
}

test "public accessors stay lane-exclusive across representative raw values" {
    const cases = [_]struct {
        raw: usize,
        kind: xarray_slot_view.SlotKind,
        value: ?usize,
        err: ?isize,
        pointer: ?usize,
    }{
        .{ .raw = 0, .kind = .null, .value = null, .err = null, .pointer = null },
        .{ .raw = try xa_value.makeValue(0), .kind = .value, .value = 0, .err = null, .pointer = null },
        .{ .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .kind = .value, .value = xa_value.safe_inline_limit, .err = null, .pointer = null },
        .{ .raw = err_ptr.err_floor - 1, .kind = .pointer, .value = null, .err = null, .pointer = err_ptr.err_floor - 1 },
        .{ .raw = 0x1000, .kind = .pointer, .value = null, .err = null, .pointer = 0x1000 },
        .{ .raw = err_ptr.fromErrorCode(-4095), .kind = .err, .value = null, .err = -4095, .pointer = null },
        .{ .raw = err_ptr.fromErrorCode(-22), .kind = .err, .value = null, .err = -22, .pointer = null },
        .{ .raw = err_ptr.fromErrorCode(-1), .kind = .err, .value = null, .err = -1, .pointer = null },
    };

    for (cases) |case| {
        const slot = xarray_slot_view.fromRaw(case.raw);
        try expectAccessors(slot, case.kind, case.value, case.err, case.pointer);
    }
}

test "constructor helpers surface exactly one public accessor per lane" {
    const null_slot = xarray_slot_view.nullSlot();
    const value_slot = try xarray_slot_view.fromValue(37);
    const err_slot = xarray_slot_view.fromErrorCode(-17);
    const pointer_slot = xarray_slot_view.fromPointer(0x2000);

    try expectAccessors(null_slot, .null, null, null, null);
    try expectAccessors(value_slot, .value, 37, null, null);
    try expectAccessors(err_slot, .err, null, -17, null);
    try expectAccessors(pointer_slot, .pointer, null, null, 0x2000);
}

test "last inline xa_value and first pointer-gap raw split cleanly across accessors" {
    const last_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const last_value_slot = xarray_slot_view.fromRaw(last_value_raw);
    const first_gap_raw = err_ptr.err_floor - 1;
    const first_gap_slot = xarray_slot_view.fromRaw(first_gap_raw);

    try expectAccessors(
        last_value_slot,
        .value,
        xa_value.safe_inline_limit,
        null,
        null,
    );
    try expectAccessors(first_gap_slot, .pointer, null, null, first_gap_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 2, last_value_raw);
}
