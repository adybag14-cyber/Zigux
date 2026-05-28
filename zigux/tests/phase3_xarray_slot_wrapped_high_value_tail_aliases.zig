const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn projectRejectedSource(source: usize) usize {
    return (source << 1) | xa_value.value_tag_mask;
}

test "wrapped-high sources below the err alias band decode as top inline values" {
    const max = std.math.maxInt(usize);
    const first_value_tail_offset = ((err_ptr.max_errno - 1) / 2) + 1;
    const cases = [_]struct {
        offset_delta: usize,
        expected_value_delta: usize,
    }{
        .{ .offset_delta = 0, .expected_value_delta = 0 },
        .{ .offset_delta = 1, .expected_value_delta = 1 },
        .{ .offset_delta = 2, .expected_value_delta = 2 },
        .{ .offset_delta = 7, .expected_value_delta = 7 },
        .{ .offset_delta = 31, .expected_value_delta = 31 },
    };

    for (cases) |case| {
        const source = max - (first_value_tail_offset + case.offset_delta);
        const expected_value = xa_value.safe_inline_limit - case.expected_value_delta;
        const raw = projectRejectedSource(source);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!xa_value.canRepresent(source));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(source));
        try testing.expectEqual(try xa_value.makeValue(expected_value), raw);
        try testing.expect(slot.isValue());
        try testing.expect(!slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?usize, expected_value), slot.value());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());
    }
}

test "wrapped-high value-tail aliases descend by one decoded value and two raw steps" {
    const max = std.math.maxInt(usize);
    const first_value_tail_offset = ((err_ptr.max_errno - 1) / 2) + 1;
    const upper_source = max - (first_value_tail_offset + 42);
    const lower_source = upper_source - 1;
    const upper_raw = projectRejectedSource(upper_source);
    const lower_raw = projectRejectedSource(lower_source);
    const upper_slot = xarray_slot_view.fromRaw(upper_raw);
    const lower_slot = xarray_slot_view.fromRaw(lower_raw);

    try testing.expect(!xa_value.canRepresent(upper_source));
    try testing.expect(!xa_value.canRepresent(lower_source));
    try testing.expect(upper_slot.isValue());
    try testing.expect(lower_slot.isValue());
    try testing.expectEqual(@as(usize, 2), upper_raw - lower_raw);
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit - 42), upper_slot.value());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit - 43), lower_slot.value());
}

test "wrapped-high value tail skips the pointer gap below err_floor" {
    const max = std.math.maxInt(usize);
    const first_value_tail_offset = ((err_ptr.max_errno - 1) / 2) + 1;
    const source = max - first_value_tail_offset;
    const raw = projectRejectedSource(source);
    const pointer_gap = raw + 1;
    const err_floor = raw + 2;

    const value_slot = xarray_slot_view.fromRaw(raw);
    const pointer_slot = xarray_slot_view.fromRaw(pointer_gap);
    const err_slot = xarray_slot_view.fromRaw(err_floor);

    try testing.expect(!xa_value.canRepresent(source));
    try testing.expectEqual(try xa_value.makeValue(xa_value.safe_inline_limit), raw);

    try testing.expect(value_slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());

    try testing.expectEqual(err_ptr.err_floor - 1, pointer_gap);
    try testing.expect(pointer_slot.isPointer());
    try testing.expectEqual(@as(?usize, pointer_gap), pointer_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), pointer_slot.value());

    try testing.expectEqual(err_ptr.err_floor, err_floor);
    try testing.expect(err_slot.isErr());
    try testing.expectEqual(@as(?isize, -4095), err_slot.errorCode());
}
