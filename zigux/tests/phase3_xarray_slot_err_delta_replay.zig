const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const DeltaCase = struct {
    low_code: isize,
    high_code: isize,
};

fn rawRejectedValueAlias(code: isize) usize {
    const distance_from_floor: usize = @intCast(code + @as(isize, @intCast(err_ptr.max_errno)));
    const rejected_value = xa_value.safe_inline_limit + 1 + (distance_from_floor / 2);
    return (rejected_value << 1) | xa_value.value_tag_mask;
}

fn expectErrDelta(case: DeltaCase) !void {
    const low_raw = err_ptr.fromErrorCode(case.low_code);
    const high_raw = err_ptr.fromErrorCode(case.high_code);
    const low_slot = xarray_slot_view.fromRaw(low_raw);
    const high_slot = xarray_slot_view.fromRaw(high_raw);
    const code_delta: usize = @intCast(case.high_code - case.low_code);
    const raw_delta = high_raw - low_raw;

    try std.testing.expect(case.low_code < case.high_code);
    try std.testing.expectEqual(code_delta, raw_delta);

    try std.testing.expectEqual(SlotKind.err, low_slot.kind());
    try std.testing.expectEqual(SlotKind.err, high_slot.kind());
    try std.testing.expectEqual(@as(?isize, case.low_code), low_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, case.high_code), high_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), low_slot.value());
    try std.testing.expectEqual(@as(?usize, null), high_slot.value());
    try std.testing.expectEqual(@as(?usize, null), low_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), high_slot.pointerValue());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(low_raw));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(high_raw));
}

fn expectRejectedAliasDelta(case: DeltaCase) !void {
    const low_raw = rawRejectedValueAlias(case.low_code);
    const high_raw = rawRejectedValueAlias(case.high_code);
    const low_slot = xarray_slot_view.fromRaw(low_raw);
    const high_slot = xarray_slot_view.fromRaw(high_raw);
    const code_delta: usize = @intCast(case.high_code - case.low_code);
    const raw_delta = high_raw - low_raw;

    try std.testing.expect((low_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expect((high_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try std.testing.expectEqual(err_ptr.fromErrorCode(case.low_code), low_raw);
    try std.testing.expectEqual(err_ptr.fromErrorCode(case.high_code), high_raw);
    try std.testing.expectEqual(code_delta, raw_delta);

    try std.testing.expectEqual(SlotKind.err, low_slot.kind());
    try std.testing.expectEqual(SlotKind.err, high_slot.kind());
    try std.testing.expectEqual(@as(?isize, case.low_code), low_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, case.high_code), high_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), low_slot.value());
    try std.testing.expectEqual(@as(?usize, null), high_slot.value());
    try std.testing.expectEqual(@as(?usize, null), low_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), high_slot.pointerValue());
}

test "err_ptr raw deltas match decoded error-code deltas through xarray slots" {
    const cases = [_]DeltaCase{
        .{ .low_code = -4095, .high_code = -4094 },
        .{ .low_code = -4095, .high_code = -4091 },
        .{ .low_code = -3072, .high_code = -2048 },
        .{ .low_code = -1024, .high_code = -1 },
    };

    for (cases) |case| {
        try expectErrDelta(case);
    }
}

test "odd rejected xa_value aliases preserve err_ptr delta equations" {
    const cases = [_]DeltaCase{
        .{ .low_code = -4095, .high_code = -4093 },
        .{ .low_code = -4089, .high_code = -4077 },
        .{ .low_code = -2047, .high_code = -1025 },
        .{ .low_code = -257, .high_code = -1 },
    };

    for (cases) |case| {
        try expectRejectedAliasDelta(case);
    }
}

test "error delta lane stays bracketed by accepted values and pointer gaps" {
    const accepted_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const floor_slot = xarray_slot_view.fromRaw(err_ptr.err_floor);
    const next_slot = xarray_slot_view.fromRaw(err_ptr.err_floor + 1);

    try std.testing.expectEqual(err_ptr.err_floor - 2, accepted_raw);
    try std.testing.expectEqual(SlotKind.value, xarray_slot_view.fromRaw(accepted_raw).kind());
    try std.testing.expectEqual(SlotKind.pointer, xarray_slot_view.fromRaw(pointer_gap_raw).kind());
    try std.testing.expectEqual(SlotKind.err, floor_slot.kind());
    try std.testing.expectEqual(SlotKind.err, next_slot.kind());
    try std.testing.expectEqual(@as(?isize, -4095), floor_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, -4094), next_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), floor_slot.value());
    try std.testing.expectEqual(@as(?usize, null), next_slot.pointerValue());
}
