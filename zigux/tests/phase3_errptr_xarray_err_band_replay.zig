const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ErrCase = struct {
    code: isize,
    expected_low_bit: usize,
};

fn expectErrCase(case: ErrCase) !void {
    const raw = err_ptr.fromErrorCode(case.code);
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expect(!err_ptr.isOkValue(raw));
    try testing.expect(!xa_value.isValue(raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    try testing.expectEqual(case.expected_low_bit, raw & xa_value.value_tag_mask);
    try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try testing.expectEqual(@as(?isize, case.code), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "err band replay keeps representative interior error encodings on the err lane" {
    const cases = [_]ErrCase{
        .{ .code = -4095, .expected_low_bit = 1 },
        .{ .code = -4094, .expected_low_bit = 0 },
        .{ .code = -4093, .expected_low_bit = 1 },
        .{ .code = -22, .expected_low_bit = 0 },
        .{ .code = -3, .expected_low_bit = 1 },
        .{ .code = -2, .expected_low_bit = 0 },
        .{ .code = -1, .expected_low_bit = 1 },
    };

    for (cases) |case| {
        try expectErrCase(case);
    }
}

test "err band replay keeps consecutive raw encodings adjacent across the floor" {
    const err_floor_raw = err_ptr.fromErrorCode(-4095);
    const next_raw = err_ptr.fromErrorCode(-4094);
    const third_raw = err_ptr.fromErrorCode(-4093);
    const fourth_raw = err_ptr.fromErrorCode(-4092);

    try testing.expectEqual(err_ptr.err_floor, err_floor_raw);
    try testing.expectEqual(err_floor_raw + 1, next_raw);
    try testing.expectEqual(next_raw + 1, third_raw);
    try testing.expectEqual(third_raw + 1, fourth_raw);

    try expectErrCase(.{ .code = -4095, .expected_low_bit = 1 });
    try expectErrCase(.{ .code = -4094, .expected_low_bit = 0 });
    try expectErrCase(.{ .code = -4093, .expected_low_bit = 1 });
    try expectErrCase(.{ .code = -4092, .expected_low_bit = 0 });
}

test "err band replay keeps the band entrance split from the last value and pointer gap" {
    const last_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const err_floor_raw = err_ptr.fromErrorCode(-4095);
    const next_err_raw = err_ptr.fromErrorCode(-4094);

    const value_slot = xarray_slot_view.fromRaw(last_value_raw);
    const gap_slot = xarray_slot_view.fromRaw(gap_raw);
    const err_floor_slot = xarray_slot_view.fromRaw(err_floor_raw);
    const next_err_slot = xarray_slot_view.fromRaw(next_err_raw);

    try testing.expectEqual(err_ptr.err_floor - 2, last_value_raw);
    try testing.expectEqual(last_value_raw + 1, gap_raw);
    try testing.expectEqual(gap_raw + 1, err_floor_raw);
    try testing.expectEqual(err_floor_raw + 1, next_err_raw);

    try testing.expect(xa_value.isValue(last_value_raw));
    try testing.expect(value_slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());

    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));
    try testing.expect(gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());

    try testing.expect(err_floor_slot.isErr());
    try testing.expect(next_err_slot.isErr());
    try testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());
    try testing.expectEqual(@as(?isize, -4094), next_err_slot.errorCode());
}
