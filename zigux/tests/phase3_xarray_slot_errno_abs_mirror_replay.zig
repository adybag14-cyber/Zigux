const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ErrnoMirrorCase = struct {
    code: isize,
    absolute_errno: usize,
};

test "xarray error slots mirror absolute Linux errno magnitudes" {
    const cases = [_]ErrnoMirrorCase{
        .{ .code = -1, .absolute_errno = 1 },
        .{ .code = -2, .absolute_errno = 2 },
        .{ .code = -12, .absolute_errno = 12 },
        .{ .code = -22, .absolute_errno = 22 },
        .{ .code = -95, .absolute_errno = 95 },
        .{ .code = -4094, .absolute_errno = 4094 },
        .{ .code = -4095, .absolute_errno = 4095 },
    };

    for (cases) |case| {
        const raw = err_ptr.fromErrorCode(case.code);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expect(slot.isTaggedEntry());
        try testing.expectEqual(raw, slot.rawValue());
        try testing.expectEqual(case.code, slot.errorCode().?);
        try testing.expectEqual(case.absolute_errno, @as(usize, @intCast(-slot.errorCode().?)));
        try testing.expectEqual(case.absolute_errno, @as(usize, @intCast(-err_ptr.toErrorCode(raw))));
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "errno abs mirror keeps neighboring non-error lanes closed" {
    const inline_zero = xarray_slot_view.fromRaw(try xa_value.makeValue(0));
    const pointer_gap = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);
    const err_floor = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try testing.expectEqual(xarray_slot_view.SlotKind.value, inline_zero.kind());
    try testing.expectEqual(@as(?usize, 0), inline_zero.value());
    try testing.expectEqual(@as(?isize, null), inline_zero.errorCode());
    try testing.expectEqual(@as(?usize, null), inline_zero.pointerValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap.kind());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), pointer_gap.pointerValue());
    try testing.expectEqual(@as(?isize, null), pointer_gap.errorCode());
    try testing.expectEqual(@as(?usize, null), pointer_gap.value());

    try testing.expectEqual(xarray_slot_view.SlotKind.err, err_floor.kind());
    try testing.expectEqual(@as(?isize, -4095), err_floor.errorCode());
    try testing.expectEqual(@as(usize, 4095), @as(usize, @intCast(-err_floor.errorCode().?)));
}
