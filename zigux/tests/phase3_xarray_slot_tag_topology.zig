const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

fn expectKind(raw: usize, expected: SlotKind) !xarray_slot_view.SlotView {
    const slot = xarray_slot_view.fromRaw(raw);
    try testing.expectEqual(expected, slot.kind());
    try testing.expectEqual(raw, slot.rawValue());
    return slot;
}

test "low raw topology keeps null odd tagged values and even pointer gaps separated" {
    const cases = [_]struct {
        raw: usize,
        kind: SlotKind,
        value: ?usize,
        pointer_raw: ?usize,
    }{
        .{ .raw = 0, .kind = .null, .value = null, .pointer_raw = null },
        .{ .raw = 1, .kind = .value, .value = 0, .pointer_raw = null },
        .{ .raw = 2, .kind = .pointer, .value = null, .pointer_raw = 2 },
        .{ .raw = 3, .kind = .value, .value = 1, .pointer_raw = null },
        .{ .raw = 4, .kind = .pointer, .value = null, .pointer_raw = 4 },
        .{ .raw = 5, .kind = .value, .value = 2, .pointer_raw = null },
        .{ .raw = 6, .kind = .pointer, .value = null, .pointer_raw = 6 },
        .{ .raw = 7, .kind = .value, .value = 3, .pointer_raw = null },
    };

    var value_sum: usize = 0;
    var pointer_xor: usize = 0;

    for (cases) |case| {
        const slot = try expectKind(case.raw, case.kind);
        try testing.expectEqual(case.value, slot.value());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());
        try testing.expectEqual(case.pointer_raw, slot.pointerValue());
        try testing.expectEqual(case.kind != .pointer and case.kind != .null, xarray_slot_view.isTaggedInternalEntry(case.raw));

        if (case.value) |value| value_sum += value;
        if (case.pointer_raw) |pointer_raw| pointer_xor ^= pointer_raw;
    }

    try testing.expectEqual(@as(usize, 6), value_sum);
    try testing.expectEqual(@as(usize, 2 ^ 4 ^ 6), pointer_xor);
}

test "cutoff topology keeps the last odd values below the pointer gap and err floor" {
    const raws = [_]usize{
        err_ptr.err_floor - 4,
        err_ptr.err_floor - 3,
        err_ptr.err_floor - 2,
        err_ptr.err_floor - 1,
        err_ptr.err_floor,
        err_ptr.err_floor + 1,
    };
    const expected_kinds = [_]SlotKind{
        .value,
        .pointer,
        .value,
        .pointer,
        .err,
        .err,
    };
    const expected_values = [_]?usize{
        xa_value.safe_inline_limit - 1,
        null,
        xa_value.safe_inline_limit,
        null,
        null,
        null,
    };
    const expected_errors = [_]?isize{
        null,
        null,
        null,
        null,
        -4095,
        -4094,
    };

    for (raws, expected_kinds, expected_values, expected_errors) |raw, expected_kind, expected_value, expected_error| {
        const slot = try expectKind(raw, expected_kind);
        try testing.expectEqual(expected_value, slot.value());
        try testing.expectEqual(expected_error, slot.errorCode());
        try testing.expectEqual(
            if (expected_kind == .pointer) @as(?usize, raw) else null,
            slot.pointerValue(),
        );
    }

    const rebuilt_penultimate_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit - 1);
    const rebuilt_last_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const rebuilt_err_floor = xarray_slot_view.fromErrorCode(-4095);

    try testing.expectEqual(err_ptr.err_floor - 4, rebuilt_penultimate_value.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 2, rebuilt_last_value.rawValue());
    try testing.expectEqual(err_ptr.err_floor, rebuilt_err_floor.rawValue());
}

test "top err topology keeps contiguous terminal error raws in the err lane" {
    const raws = [_]usize{
        err_ptr.fromErrorCode(-3),
        err_ptr.fromErrorCode(-2),
        err_ptr.fromErrorCode(-1),
    };
    const expected_low_bits = [_]usize{ 1, 0, 1 };
    const expected_errors = [_]isize{ -3, -2, -1 };

    for (raws, expected_low_bits, expected_errors) |raw, expected_low_bit, expected_error| {
        const slot = try expectKind(raw, .err);
        try testing.expectEqual(expected_low_bit, raw & 0x1);
        try testing.expectEqual(@as(?isize, expected_error), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}
