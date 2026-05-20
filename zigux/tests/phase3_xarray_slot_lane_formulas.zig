const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectFormula(raw: usize, expected_kind: xarray_slot_view.SlotKind) !xarray_slot_view.SlotView {
    const slot = xarray_slot_view.fromRaw(raw);
    try testing.expectEqual(expected_kind, slot.kind());
    try testing.expectEqual(raw, slot.rawValue());
    try testing.expectEqual(expected_kind != .null and expected_kind != .pointer, xarray_slot_view.isTaggedInternalEntry(raw));
    return slot;
}

test "nonzero odd raws below the err floor stay in the value lane" {
    const values = [_]usize{ 0, 1, 2, 29, xa_value.safe_inline_limit - 1, xa_value.safe_inline_limit };

    for (values) |value| {
        const raw = try xa_value.makeValue(value);
        const slot = try expectFormula(raw, .value);

        try testing.expect(raw < err_ptr.err_floor);
        try testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(?usize, value), slot.value());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expectEqual(raw >> 1, value);
    }
}

test "positive even raws below the err floor stay pointer-like" {
    const raws = [_]usize{ 2, 4, 6, 0x20, err_ptr.err_floor - 3, err_ptr.err_floor - 1 };

    for (raws) |raw| {
        const slot = try expectFormula(raw, .pointer);

        try testing.expect(raw != 0);
        try testing.expect(raw < err_ptr.err_floor);
        try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());
        try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    }
}

test "the null raw and the contiguous err band close the remaining formulas" {
    const null_slot = try expectFormula(0, .null);
    try testing.expectEqual(@as(?usize, null), null_slot.value());
    try testing.expectEqual(@as(?isize, null), null_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), null_slot.pointerValue());

    const err_cases = [_]struct {
        code: isize,
        raw: usize,
    }{
        .{ .code = -4095, .raw = err_ptr.err_floor },
        .{ .code = -4094, .raw = err_ptr.err_floor + 1 },
        .{ .code = -2, .raw = err_ptr.fromErrorCode(-2) },
        .{ .code = -1, .raw = err_ptr.fromErrorCode(-1) },
    };

    for (err_cases, 0..) |case, index| {
        const slot = try expectFormula(case.raw, .err);
        try testing.expect(case.raw >= err_ptr.err_floor);
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?isize, case.code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());

        if (index != 0) {
            try testing.expect(err_cases[index - 1].raw < case.raw);
        }
    }
}
