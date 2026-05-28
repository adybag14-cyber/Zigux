const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn projectRejectedSource(source: usize) usize {
    return (source << 1) | xa_value.value_tag_mask;
}

test "wrapped-high partition starts at odd err aliases and descends through err floor" {
    const max = std.math.maxInt(usize);
    const first_err_source = max;
    const last_err_offset = (err_ptr.max_errno - 1) / 2;
    const last_err_source = max - last_err_offset;

    try testing.expectEqual(err_ptr.fromErrorCode(-1), projectRejectedSource(first_err_source));
    try testing.expectEqual(err_ptr.err_floor, projectRejectedSource(last_err_source));
    try testing.expectEqual(@as(usize, 2047), last_err_offset);

    for ([_]usize{ 0, 1, 2, 127, last_err_offset }) |offset| {
        const source = max - offset;
        const raw = projectRejectedSource(source);
        const slot = xarray_slot_view.fromRaw(raw);
        const expected_code = -@as(isize, @intCast((offset * 2) + 1));

        try testing.expect(!xa_value.canRepresent(source));
        try testing.expectEqual(err_ptr.fromErrorCode(expected_code), raw);
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "wrapped-high value-tail partition begins immediately below the err alias partition" {
    const max = std.math.maxInt(usize);
    const first_value_tail_offset = ((err_ptr.max_errno - 1) / 2) + 1;
    const first_value_source = max - first_value_tail_offset;
    const first_value_raw = projectRejectedSource(first_value_source);
    const previous_err_raw = projectRejectedSource(first_value_source + 1);
    const pointer_gap = first_value_raw + 1;
    const err_floor = first_value_raw + 2;

    try testing.expectEqual(@as(usize, 2048), first_value_tail_offset);
    try testing.expectEqual(err_ptr.err_floor, previous_err_raw);
    try testing.expectEqual(try xa_value.makeValue(xa_value.safe_inline_limit), first_value_raw);
    try testing.expectEqual(err_ptr.err_floor - 1, pointer_gap);
    try testing.expectEqual(err_ptr.err_floor, err_floor);

    try testing.expect(xarray_slot_view.fromRaw(previous_err_raw).isErr());
    try testing.expect(xarray_slot_view.fromRaw(first_value_raw).isValue());
    try testing.expect(xarray_slot_view.fromRaw(pointer_gap).isPointer());
    try testing.expect(xarray_slot_view.fromRaw(err_floor).isErr());
}

test "wrapped-high value-tail partition mirrors the top safe inline value window" {
    const max = std.math.maxInt(usize);
    const first_value_tail_offset = ((err_ptr.max_errno - 1) / 2) + 1;
    const cases = [_]struct {
        delta: usize,
        expected_value_delta: usize,
    }{
        .{ .delta = 0, .expected_value_delta = 0 },
        .{ .delta = 1, .expected_value_delta = 1 },
        .{ .delta = 2, .expected_value_delta = 2 },
        .{ .delta = 255, .expected_value_delta = 255 },
    };

    for (cases) |case| {
        const source = max - (first_value_tail_offset + case.delta);
        const expected_value = xa_value.safe_inline_limit - case.expected_value_delta;
        const raw = projectRejectedSource(source);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!xa_value.canRepresent(source));
        try testing.expectEqual(try xa_value.makeValue(expected_value), raw);
        try testing.expect(slot.isValue());
        try testing.expect(!slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?usize, expected_value), slot.value());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "wrapped-high rejected sources stay on odd tagged raws through the zero value" {
    const max = std.math.maxInt(usize);
    const first_value_tail_offset = ((err_ptr.max_errno - 1) / 2) + 1;
    const zero_value_offset = max >> 1;
    const zero_value_source = max - zero_value_offset;
    const zero_value_raw = projectRejectedSource(zero_value_source);
    const wrap_back_source = zero_value_source - 1;
    const wrap_back_raw = projectRejectedSource(wrap_back_source);

    try testing.expect(zero_value_offset > first_value_tail_offset);
    try testing.expect(!xa_value.canRepresent(zero_value_source));
    try testing.expectEqual(try xa_value.makeValue(0), zero_value_raw);
    try testing.expect(xarray_slot_view.fromRaw(zero_value_raw).isValue());
    try testing.expectEqual(@as(?usize, 0), xarray_slot_view.fromRaw(zero_value_raw).value());

    try testing.expect(!xa_value.canRepresent(wrap_back_source));
    try testing.expectEqual(err_ptr.fromErrorCode(-1), wrap_back_raw);
    try testing.expect(xarray_slot_view.fromRaw(wrap_back_raw).isErr());
    try testing.expectEqual(@as(?isize, -1), xarray_slot_view.fromRaw(wrap_back_raw).errorCode());
}
