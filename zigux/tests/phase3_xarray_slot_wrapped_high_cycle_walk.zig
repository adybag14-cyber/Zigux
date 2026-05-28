const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn projectRejectedSource(source: usize) usize {
    return (source << 1) | xa_value.value_tag_mask;
}

test "wrapped-high projection walks the odd err_ptr aliases in order" {
    const max = std.math.maxInt(usize);
    const cases = [_]struct {
        source_offset: usize,
        expected_error: isize,
    }{
        .{ .source_offset = 0, .expected_error = -1 },
        .{ .source_offset = 1, .expected_error = -3 },
        .{ .source_offset = 17, .expected_error = -35 },
        .{ .source_offset = (err_ptr.max_errno - 1) / 2, .expected_error = -4095 },
    };

    for (cases) |case| {
        const source = max - case.source_offset;
        const raw = projectRejectedSource(source);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!xa_value.canRepresent(source));
        try testing.expectEqual(err_ptr.fromErrorCode(case.expected_error), raw);
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, case.expected_error), slot.errorCode());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "wrapped-high projection walks down the safe inline value tail" {
    const max = std.math.maxInt(usize);
    const first_value_tail_offset = ((err_ptr.max_errno - 1) / 2) + 1;
    const cases = [_]usize{ 0, 1, 17, 1024 };

    for (cases) |delta| {
        const source = max - (first_value_tail_offset + delta);
        const expected_value = xa_value.safe_inline_limit - delta;
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

test "even gaps between wrapped-high projected value raws stay pointer-like" {
    const max = std.math.maxInt(usize);
    const first_value_tail_offset = ((err_ptr.max_errno - 1) / 2) + 1;
    const cases = [_]usize{ 0, 1, 17, 1024 };

    for (cases) |delta| {
        const source = max - (first_value_tail_offset + delta);
        const value_raw = projectRejectedSource(source);
        const pointer_gap = value_raw + 1;
        const slot = xarray_slot_view.fromRaw(pointer_gap);

        try testing.expect(value_raw < err_ptr.err_floor);
        try testing.expectEqual(@as(usize, 0), pointer_gap & xa_value.value_tag_mask);
        try testing.expect(!xarray_slot_view.fromRaw(value_raw).isPointer());
        try testing.expect(slot.isPointer());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isErr());
        try testing.expectEqual(@as(?usize, pointer_gap), slot.pointerValue());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap));
    }
}

test "wrapped-high cycle leaves zero value and returns to the top err alias" {
    const max = std.math.maxInt(usize);
    const zero_value_offset = max >> 1;
    const zero_value_source = max - zero_value_offset;
    const wrap_back_source = zero_value_source - 1;
    const zero_value_raw = projectRejectedSource(zero_value_source);
    const wrap_back_raw = projectRejectedSource(wrap_back_source);

    try testing.expect(!xa_value.canRepresent(zero_value_source));
    try testing.expectEqual(try xa_value.makeValue(0), zero_value_raw);
    try testing.expect(xarray_slot_view.fromRaw(zero_value_raw).isValue());
    try testing.expectEqual(@as(?usize, 0), xarray_slot_view.fromRaw(zero_value_raw).value());

    try testing.expect(!xa_value.canRepresent(wrap_back_source));
    try testing.expectEqual(err_ptr.fromErrorCode(-1), wrap_back_raw);
    try testing.expect(xarray_slot_view.fromRaw(wrap_back_raw).isErr());
    try testing.expectEqual(@as(?isize, -1), xarray_slot_view.fromRaw(wrap_back_raw).errorCode());
}
