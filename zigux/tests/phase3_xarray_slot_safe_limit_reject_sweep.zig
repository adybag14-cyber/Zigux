const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn uncheckedTaggedValue(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

test "safe inline tail stays below err_ptr floor with pointer gaps preserved" {
    const cases = [_]usize{ 0, 1, 2, 17 };

    for (cases) |distance_from_tail| {
        const value = xa_value.safe_inline_limit - distance_from_tail;
        const raw = try xa_value.makeValue(value);
        const slot = xarray_slot_view.fromRaw(raw);
        const pointer_gap = raw + 1;

        try testing.expect(xa_value.canRepresent(value));
        try testing.expectEqual(err_ptr.err_floor - 2 - (distance_from_tail * 2), raw);
        try testing.expect(slot.isValue());
        try testing.expect(!slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?usize, value), slot.value());

        try testing.expectEqual(@as(usize, 0), pointer_gap & xa_value.value_tag_mask);
        try testing.expect(xarray_slot_view.fromRaw(pointer_gap).isPointer());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap));
    }
}

test "first rejected inline values project into err_ptr codes, not values" {
    const cases = [_]struct {
        value_delta: usize,
        expected_error: isize,
    }{
        .{ .value_delta = 1, .expected_error = -4095 },
        .{ .value_delta = 2, .expected_error = -4093 },
        .{ .value_delta = 3, .expected_error = -4091 },
        .{ .value_delta = 8, .expected_error = -4081 },
    };

    for (cases) |case| {
        const rejected_value = xa_value.safe_inline_limit + case.value_delta;
        const raw = uncheckedTaggedValue(rejected_value);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!xa_value.canRepresent(rejected_value));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
        try testing.expectEqual(err_ptr.fromErrorCode(case.expected_error), raw);
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, case.expected_error), slot.errorCode());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "even err_ptr neighbors stay errors even without the xa_value low bit" {
    const cases = [_]isize{ -4094, -4092, -4080, -2 };

    for (cases) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "slot constructors reject the overlap while raw views preserve provenance" {
    const rejected_value = xa_value.safe_inline_limit + 1;
    const rejected_raw = uncheckedTaggedValue(rejected_value);
    const below_floor_gap = err_ptr.err_floor - 1;

    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected_value));
    try testing.expectEqual(err_ptr.err_floor, rejected_raw);
    try testing.expect(xarray_slot_view.fromRaw(rejected_raw).isErr());
    try testing.expectEqual(@as(?isize, -4095), xarray_slot_view.fromRaw(rejected_raw).errorCode());

    try testing.expect(xarray_slot_view.fromRaw(below_floor_gap).isPointer());
    try testing.expectEqual(@as(?usize, below_floor_gap), xarray_slot_view.fromRaw(below_floor_gap).pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(below_floor_gap));
}
