const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const ErrorCase = struct {
    code: isize,
    raw: usize,
};

fn assertErrSlot(case: ErrorCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
    try std.testing.expect(err_ptr.isErrValue(case.raw));
    try std.testing.expect(!err_ptr.isOkValue(case.raw));
    try std.testing.expect(!xa_value.isValue(case.raw));
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(@as(?isize, case.code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "xarray slot err lane preserves monotonic errno ordering" {
    const cases = [_]ErrorCase{
        .{ .code = -4095, .raw = err_ptr.fromErrorCode(-4095) },
        .{ .code = -4094, .raw = err_ptr.fromErrorCode(-4094) },
        .{ .code = -2048, .raw = err_ptr.fromErrorCode(-2048) },
        .{ .code = -2047, .raw = err_ptr.fromErrorCode(-2047) },
        .{ .code = -2, .raw = err_ptr.fromErrorCode(-2) },
        .{ .code = -1, .raw = err_ptr.fromErrorCode(-1) },
    };

    try std.testing.expectEqual(err_ptr.err_floor, cases[0].raw);

    var previous_raw = cases[0].raw;
    var previous_code = cases[0].code;
    for (cases, 0..) |case, index| {
        try assertErrSlot(case);
        if (index == 0) continue;

        try std.testing.expect(case.raw > previous_raw);
        try std.testing.expect(case.code > previous_code);
        try std.testing.expectEqual(@as(usize, @intCast(case.code - previous_code)), case.raw - previous_raw);

        previous_raw = case.raw;
        previous_code = case.code;
    }
}

test "err band raw residues do not escape to value or pointer lanes" {
    const cases = [_]ErrorCase{
        .{ .code = -4095, .raw = err_ptr.err_floor },
        .{ .code = -4094, .raw = err_ptr.err_floor + 1 },
        .{ .code = -4093, .raw = err_ptr.err_floor + 2 },
        .{ .code = -4092, .raw = err_ptr.err_floor + 3 },
        .{ .code = -3, .raw = err_ptr.fromErrorCode(-3) },
        .{ .code = -2, .raw = err_ptr.fromErrorCode(-2) },
        .{ .code = -1, .raw = err_ptr.fromErrorCode(-1) },
    };

    for (cases) |case| {
        try assertErrSlot(case);
        try std.testing.expectEqual(@as(isize, @bitCast(case.raw)), case.code);
    }
}
