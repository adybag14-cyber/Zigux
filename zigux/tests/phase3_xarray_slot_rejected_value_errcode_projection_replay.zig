const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const ProjectionCase = struct {
    rejected_offset: usize,
    expected_code: isize,
};

fn rejectedValueRaw(offset: usize) usize {
    const rejected_value = xa_value.safe_inline_limit + 1 + offset;
    return (rejected_value << 1) | xa_value.value_tag_mask;
}

fn expectedErrorCode(offset: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(offset * 2));
}

fn expectRejectedProjection(case: ProjectionCase) !void {
    const rejected_value = xa_value.safe_inline_limit + 1 + case.rejected_offset;
    const raw = rejectedValueRaw(case.rejected_offset);
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(!xa_value.canRepresent(rejected_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected_value));

    try std.testing.expectEqual(err_ptr.fromErrorCode(case.expected_code), raw);
    try std.testing.expectEqual(case.expected_code, expectedErrorCode(case.rejected_offset));
    try std.testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expect(err_ptr.isErrValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

    try std.testing.expectEqual(SlotKind.err, slot.kind());
    try std.testing.expectEqual(@as(?isize, case.expected_code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "rejected inline values project onto every second err_ptr code" {
    const cases = [_]ProjectionCase{
        .{ .rejected_offset = 0, .expected_code = -4095 },
        .{ .rejected_offset = 1, .expected_code = -4093 },
        .{ .rejected_offset = 2, .expected_code = -4091 },
        .{ .rejected_offset = 17, .expected_code = -4061 },
        .{ .rejected_offset = 512, .expected_code = -3071 },
        .{ .rejected_offset = 1024, .expected_code = -2047 },
        .{ .rejected_offset = 2047, .expected_code = -1 },
    };

    for (cases) |case| {
        try expectRejectedProjection(case);
    }
}

test "neighboring even err raws stay errors while untagged to xa_value" {
    const offsets = [_]usize{ 0, 1, 2, 17, 512, 1024, 2046 };

    for (offsets) |offset| {
        const odd_err_raw = rejectedValueRaw(offset);
        const even_neighbor_raw = odd_err_raw + 1;
        const slot = xarray_slot_view.fromRaw(even_neighbor_raw);
        const expected_code = expectedErrorCode(offset) + 1;

        try std.testing.expect(even_neighbor_raw < err_ptr.fromErrorCode(-1));
        try std.testing.expect(err_ptr.isErrValue(even_neighbor_raw));
        try std.testing.expect(!xa_value.isValue(even_neighbor_raw));
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(even_neighbor_raw));
        try std.testing.expectEqual(SlotKind.err, slot.kind());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try std.testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try std.testing.expectEqual(@as(?usize, null), slot.value());
    }
}

test "top rejected projection lands on top err without spilling past it" {
    const last_offset = (err_ptr.max_errno - 1) / 2;
    const top_raw = rejectedValueRaw(last_offset);
    const top_slot = xarray_slot_view.fromRaw(top_raw);

    try std.testing.expectEqual(err_ptr.fromErrorCode(-1), top_raw);
    try std.testing.expectEqual(std.math.maxInt(usize), top_raw);
    try std.testing.expectEqual(SlotKind.err, top_slot.kind());
    try std.testing.expectEqual(@as(?isize, -1), top_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), top_slot.value());
    try std.testing.expectEqual(@as(?usize, null), top_slot.pointerValue());
}
