const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const alias_slot_count: usize = (err_ptr.max_errno + 1) / 2;

const AliasSpanCase = struct {
    delta: usize,
    expected_error: isize,
};

fn rejectedValue(delta: usize) usize {
    return xa_value.safe_inline_limit + delta;
}

fn aliasedRaw(delta: usize) usize {
    return (rejectedValue(delta) << 1) | xa_value.value_tag_mask;
}

fn expectedError(delta: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno - ((delta - 1) * 2)));
}

test "rejected xa_value aliases reach the floor midpoint pair and top of the err band" {
    const cases = [_]AliasSpanCase{
        .{ .delta = 1, .expected_error = -4095 },
        .{ .delta = alias_slot_count / 2, .expected_error = expectedError(alias_slot_count / 2) },
        .{ .delta = (alias_slot_count / 2) + 1, .expected_error = expectedError((alias_slot_count / 2) + 1) },
        .{ .delta = alias_slot_count, .expected_error = -1 },
    };

    for (cases, 0..) |case, index| {
        const value = rejectedValue(case.delta);
        const raw = aliasedRaw(case.delta);

        try testing.expect(!xa_value.canRepresent(value));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(value));
        try testing.expectEqual(case.expected_error, expectedError(case.delta));
        try testing.expectEqual(err_ptr.fromErrorCode(case.expected_error), raw);
        try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expectEqual(case.expected_error, err_ptr.toErrorCode(raw));

        const slot = xarray_slot_view.fromRaw(raw);
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expectEqual(@as(?isize, case.expected_error), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

        _ = index;
    }

    try testing.expectEqual(
        aliasedRaw(alias_slot_count / 2) + 2,
        aliasedRaw((alias_slot_count / 2) + 1),
    );
    try testing.expectEqual(
        expectedError(alias_slot_count / 2) + 2,
        expectedError((alias_slot_count / 2) + 1),
    );
}

test "aliased xa_value coverage spans every other err raw from floor through top" {
    const first_raw = aliasedRaw(1);
    const last_raw = aliasedRaw(alias_slot_count);

    try testing.expectEqual(@as(usize, 2048), alias_slot_count);
    try testing.expectEqual(err_ptr.err_floor, first_raw);
    try testing.expectEqual(err_ptr.fromErrorCode(-1), last_raw);
    try testing.expectEqual(first_raw + ((alias_slot_count - 1) * 2), last_raw);
    try testing.expectEqual(@as(isize, -4095), err_ptr.toErrorCode(first_raw));
    try testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(last_raw));

    const preceding_gap = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);
    const top_neighbor = xarray_slot_view.fromRaw(last_raw - 1);

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, preceding_gap.kind());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), preceding_gap.pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(err_ptr.err_floor - 1));

    try testing.expectEqual(xarray_slot_view.SlotKind.err, top_neighbor.kind());
    try testing.expectEqual(@as(?isize, -2), top_neighbor.errorCode());
    try testing.expectEqual(@as(?usize, null), top_neighbor.value());
    try testing.expectEqual(@as(?usize, null), top_neighbor.pointerValue());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(last_raw - 1));
}

test "explicit err constructors and raw rereads agree at the aliased span endpoints" {
    const first = xarray_slot_view.fromErrorCode(-4095);
    const middle = xarray_slot_view.fromErrorCode(expectedError((alias_slot_count / 2) + 1));
    const last = xarray_slot_view.fromErrorCode(-1);

    try testing.expectEqual(aliasedRaw(1), first.rawValue());
    try testing.expectEqual(aliasedRaw((alias_slot_count / 2) + 1), middle.rawValue());
    try testing.expectEqual(aliasedRaw(alias_slot_count), last.rawValue());

    try testing.expectEqual(xarray_slot_view.fromRaw(first.rawValue()).errorCode(), first.errorCode());
    try testing.expectEqual(xarray_slot_view.fromRaw(middle.rawValue()).errorCode(), middle.errorCode());
    try testing.expectEqual(xarray_slot_view.fromRaw(last.rawValue()).errorCode(), last.errorCode());
}
