const std = @import("std");
const err_ptr = @import("err_ptr");
const xarray_slot_view = @import("xarray_slot_view");

const ErrOffsetCase = struct {
    offset: usize,
    expected_code: isize,
};

fn expectErrOffset(case: ErrOffsetCase) !void {
    const raw = err_ptr.err_floor + case.offset;
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expectEqual(raw, slot.rawValue());
    try std.testing.expectEqual(@as(?isize, case.expected_code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

test "raw err-band offsets decode as the matching xarray slot error codes" {
    const cases = [_]ErrOffsetCase{
        .{ .offset = 0, .expected_code = -4095 },
        .{ .offset = 1, .expected_code = -4094 },
        .{ .offset = 2, .expected_code = -4093 },
        .{ .offset = 255, .expected_code = -3840 },
        .{ .offset = 1023, .expected_code = -3072 },
        .{ .offset = 2047, .expected_code = -2048 },
        .{ .offset = 4093, .expected_code = -2 },
        .{ .offset = 4094, .expected_code = -1 },
    };

    for (cases) |case| {
        try expectErrOffset(case);
        try std.testing.expectEqual(err_ptr.fromErrorCode(case.expected_code), err_ptr.err_floor + case.offset);
    }
}

test "raw slots on both sides of the err ladder keep their non-err lanes" {
    const highest_value = xarray_slot_view.fromRaw(err_ptr.err_floor - 2);
    const pointer_gap = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);
    const first_err = xarray_slot_view.fromRaw(err_ptr.err_floor);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, highest_value.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, first_err.kind());
    try std.testing.expectEqual(@as(?isize, null), highest_value.errorCode());
    try std.testing.expectEqual(@as(?isize, null), pointer_gap.errorCode());
    try std.testing.expectEqual(@as(?isize, -4095), first_err.errorCode());
}
