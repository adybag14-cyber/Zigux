const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const WeaveCase = struct {
    value: usize,
};

fn expectPointerValuePointer(case: WeaveCase) !void {
    const value_raw = try xa_value.makeValue(case.value);
    const left_pointer_raw = value_raw - 1;
    const right_pointer_raw = value_raw + 1;

    const left_slot = xarray_slot_view.fromRaw(left_pointer_raw);
    const value_slot = xarray_slot_view.fromRaw(value_raw);
    const right_slot = xarray_slot_view.fromRaw(right_pointer_raw);

    try testing.expect(case.value > 0);
    try testing.expect(value_raw < err_ptr.err_floor);
    try testing.expectEqual(left_pointer_raw + 1, value_raw);
    try testing.expectEqual(value_raw + 1, right_pointer_raw);

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, left_slot.kind());
    try testing.expect(left_slot.isPointer());
    try testing.expectEqual(@as(?usize, left_pointer_raw), left_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), left_slot.value());
    try testing.expectEqual(@as(?isize, null), left_slot.errorCode());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(left_pointer_raw));

    try testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
    try testing.expect(value_slot.isValue());
    try testing.expectEqual(@as(?usize, case.value), value_slot.value());
    try testing.expectEqual(@as(?usize, null), value_slot.pointerValue());
    try testing.expectEqual(@as(?isize, null), value_slot.errorCode());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(value_raw));

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, right_slot.kind());
    try testing.expect(right_slot.isPointer());
    try testing.expectEqual(@as(?usize, right_pointer_raw), right_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), right_slot.value());
    try testing.expectEqual(@as(?isize, null), right_slot.errorCode());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(right_pointer_raw));
}

test "value raws keep pointer neighbors on both sides across the pre-floor weave" {
    const cases = [_]WeaveCase{
        .{ .value = 1 },
        .{ .value = 2 },
        .{ .value = xa_value.safe_inline_limit / 2 },
        .{ .value = xa_value.safe_inline_limit - 1 },
        .{ .value = xa_value.safe_inline_limit },
    };

    for (cases) |case| {
        try expectPointerValuePointer(case);
    }
}

test "consecutive xa_values stay separated by a single pointer raw" {
    const starts = [_]usize{
        1,
        xa_value.safe_inline_limit / 2,
        xa_value.safe_inline_limit - 1,
    };

    for (starts) |start| {
        const lower_raw = try xa_value.makeValue(start);
        const separator_raw = lower_raw + 1;
        const upper_raw = try xa_value.makeValue(start + 1);

        const lower_slot = xarray_slot_view.fromRaw(lower_raw);
        const separator_slot = xarray_slot_view.fromRaw(separator_raw);
        const upper_slot = xarray_slot_view.fromRaw(upper_raw);

        try testing.expectEqual(lower_raw + 1, separator_raw);
        try testing.expectEqual(separator_raw + 1, upper_raw);
        try testing.expect(separator_raw < err_ptr.err_floor);

        try testing.expect(lower_slot.isValue());
        try testing.expect(separator_slot.isPointer());
        try testing.expect(upper_slot.isValue());
        try testing.expectEqual(@as(?usize, start), lower_slot.value());
        try testing.expectEqual(@as(?usize, separator_raw), separator_slot.pointerValue());
        try testing.expectEqual(@as(?usize, start + 1), upper_slot.value());
    }
}

test "constructors preserve the same weave right up to the pointer gap below err floor" {
    const last_value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const right_gap_slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-4095);

    try testing.expectEqual(err_ptr.err_floor - 2, last_value_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 1, right_gap_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor, err_floor_slot.rawValue());

    try testing.expect(last_value_slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), last_value_slot.value());

    try testing.expect(right_gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), right_gap_slot.pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(right_gap_slot.rawValue()));

    try testing.expect(err_floor_slot.isErr());
    try testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());
}
