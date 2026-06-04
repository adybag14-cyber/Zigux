const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const ProjectionCase = struct {
    rejected_offset: usize,
    expected_code: isize,
};

fn rejectedValue(offset: usize) usize {
    return xa_value.safe_inline_limit + 1 + offset;
}

fn projectedRaw(offset: usize) usize {
    return (rejectedValue(offset) << 1) | xa_value.value_tag_mask;
}

fn expectedErrorCode(offset: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(offset * 2));
}

fn expectConstructorAgreement(case: ProjectionCase) !void {
    const rejected_value = rejectedValue(case.rejected_offset);
    const raw = projectedRaw(case.rejected_offset);
    const raw_slot = xarray_slot_view.fromRaw(raw);
    const err_slot = xarray_slot_view.fromErrorCode(case.expected_code);

    try std.testing.expect(!xa_value.canRepresent(rejected_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected_value));
    try std.testing.expectEqual(case.expected_code, expectedErrorCode(case.rejected_offset));
    try std.testing.expectEqual(err_ptr.fromErrorCode(case.expected_code), raw);

    try std.testing.expectEqual(raw_slot.rawValue(), err_slot.rawValue());
    try std.testing.expectEqual(SlotKind.err, raw_slot.kind());
    try std.testing.expectEqual(SlotKind.err, err_slot.kind());
    try std.testing.expectEqual(@as(?isize, case.expected_code), raw_slot.errorCode());
    try std.testing.expectEqual(raw_slot.errorCode(), err_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), raw_slot.value());
    try std.testing.expectEqual(@as(?usize, null), raw_slot.pointerValue());
    try std.testing.expect(raw_slot.isTaggedEntry());
    try std.testing.expect(err_slot.isTaggedEntry());
}

test "rejected value projections agree with err constructors across sampled aliases" {
    const cases = [_]ProjectionCase{
        .{ .rejected_offset = 0, .expected_code = -4095 },
        .{ .rejected_offset = 3, .expected_code = -4089 },
        .{ .rejected_offset = 255, .expected_code = -3585 },
        .{ .rejected_offset = 1023, .expected_code = -2049 },
        .{ .rejected_offset = 2047, .expected_code = -1 },
    };

    for (cases) |case| {
        try expectConstructorAgreement(case);
    }
}

test "accepted ceiling and rejected floor remain adjacent but constructor-distinct" {
    const accepted = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const rejected_floor_raw = projectedRaw(0);
    const err_floor = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try std.testing.expectEqual(SlotKind.value, accepted.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), accepted.value());
    try std.testing.expectEqual(err_ptr.err_floor - 2, accepted.rawValue());

    try std.testing.expectEqual(err_ptr.err_floor, rejected_floor_raw);
    try std.testing.expectEqual(rejected_floor_raw, err_floor.rawValue());
    try std.testing.expectEqual(SlotKind.err, err_floor.kind());
    try std.testing.expectEqual(@as(?isize, -4095), err_floor.errorCode());
    try std.testing.expect(!accepted.isErr());
    try std.testing.expect(!err_floor.isValue());
}

test "even err neighbors stay constructor-free error raws between projection aliases" {
    const offsets = [_]usize{ 0, 3, 255, 1023, 2046 };

    for (offsets) |offset| {
        const even_raw = projectedRaw(offset) + 1;
        const slot = xarray_slot_view.fromRaw(even_raw);
        const expected_code = expectedErrorCode(offset) + 1;

        try std.testing.expect((even_raw & xa_value.value_tag_mask) == 0);
        try std.testing.expect(err_ptr.isErrValue(even_raw));
        try std.testing.expect(!xa_value.isValue(even_raw));
        try std.testing.expectEqual(SlotKind.err, slot.kind());
        try std.testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expectEqual(even_raw, xarray_slot_view.fromErrorCode(expected_code).rawValue());
    }
}
