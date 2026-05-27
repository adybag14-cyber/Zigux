const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const AliasCase = struct {
    value: usize,
    expected_raw: usize,
    expected_error: isize,
};

fn expectedAliasedRaw(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

test "rejected xa_value encodings alias every other raw inside a contiguous err band" {
    const cases = [_]AliasCase{
        .{
            .value = xa_value.safe_inline_limit + 1,
            .expected_raw = err_ptr.err_floor,
            .expected_error = -4095,
        },
        .{
            .value = xa_value.safe_inline_limit + 2,
            .expected_raw = err_ptr.err_floor + 2,
            .expected_error = -4093,
        },
        .{
            .value = xa_value.safe_inline_limit + 3,
            .expected_raw = err_ptr.err_floor + 4,
            .expected_error = -4091,
        },
    };

    for (cases, 0..) |case, index| {
        try testing.expect(!xa_value.canRepresent(case.value));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(case.value));

        const raw = expectedAliasedRaw(case.value);
        try testing.expectEqual(case.expected_raw, raw);
        try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expectEqual(case.expected_error, err_ptr.toErrorCode(raw));

        const slot = xarray_slot_view.fromRaw(raw);
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expectEqual(@as(?isize, case.expected_error), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());

        if (index != 0) {
            try testing.expectEqual(cases[index - 1].expected_raw + 2, case.expected_raw);
            try testing.expectEqual(cases[index - 1].expected_error + 2, case.expected_error);
        }

        if (index + 1 < cases.len) {
            const intervening_raw = raw + 1;
            const intervening = xarray_slot_view.fromRaw(intervening_raw);
            try testing.expectEqual(xarray_slot_view.SlotKind.err, intervening.kind());
            try testing.expectEqual(@as(?isize, case.expected_error + 1), intervening.errorCode());
            try testing.expectEqual(@as(?usize, null), intervening.value());
            try testing.expectEqual(@as(?usize, null), intervening.pointerValue());
            try testing.expect(xarray_slot_view.isTaggedInternalEntry(intervening_raw));
        }
    }
}

test "aliased overlap raws match the constructor and decoder arithmetic directly" {
    const baseline = try xa_value.makeValue(xa_value.safe_inline_limit);
    try testing.expectEqual(err_ptr.err_floor - 2, baseline);

    for (1..4) |delta| {
        const overlapping_value = xa_value.safe_inline_limit + delta;
        const raw = expectedAliasedRaw(overlapping_value);

        try testing.expectEqual(err_ptr.err_floor + ((delta - 1) * 2), raw);
        try testing.expectEqual(
            -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast((delta - 1) * 2)),
            err_ptr.toErrorCode(raw),
        );
    }
}

test "explicit constructors still agree with the raw alias window endpoints" {
    const first_err = xarray_slot_view.fromErrorCode(-4095);
    const middle_err = xarray_slot_view.fromErrorCode(-4093);
    const later_err = xarray_slot_view.fromErrorCode(-4091);

    try testing.expectEqual(err_ptr.err_floor, first_err.rawValue());
    try testing.expectEqual(err_ptr.err_floor + 2, middle_err.rawValue());
    try testing.expectEqual(err_ptr.err_floor + 4, later_err.rawValue());

    try testing.expectEqual(@as(?isize, -4095), xarray_slot_view.fromRaw(first_err.rawValue()).errorCode());
    try testing.expectEqual(@as(?isize, -4093), xarray_slot_view.fromRaw(middle_err.rawValue()).errorCode());
    try testing.expectEqual(@as(?isize, -4091), xarray_slot_view.fromRaw(later_err.rawValue()).errorCode());
}
