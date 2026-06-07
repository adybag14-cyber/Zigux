const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ErrnoRow = struct {
    code: isize,
    previous_raw_kind: xarray_slot_view.SlotKind,
};

fn expectErrnoProjection(row: ErrnoRow) !void {
    const raw = err_ptr.fromErrorCode(row.code);
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(row.code, err_ptr.toErrorCode(raw));
    try std.testing.expectEqual(row.code, @as(isize, @bitCast(raw)));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?isize, row.code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());

    const roundtrip = xarray_slot_view.fromErrorCode(row.code);
    try std.testing.expectEqual(raw, roundtrip.rawValue());
    try std.testing.expectEqual(slot.errorCode(), roundtrip.errorCode());

    if (raw > 0) {
        const previous = xarray_slot_view.fromRaw(raw - 1);
        try std.testing.expectEqual(row.previous_raw_kind, previous.kind());
        if (row.previous_raw_kind == .err) {
            try std.testing.expectEqual(@as(?isize, row.code - 1), previous.errorCode());
        } else {
            try std.testing.expectEqual(@as(?isize, null), previous.errorCode());
        }
    }
}

test "errno raw encodings sign-extend consistently through xarray slots" {
    const rows = [_]ErrnoRow{
        .{ .code = -4095, .previous_raw_kind = .pointer },
        .{ .code = -4094, .previous_raw_kind = .err },
        .{ .code = -2048, .previous_raw_kind = .err },
        .{ .code = -1024, .previous_raw_kind = .err },
        .{ .code = -22, .previous_raw_kind = .err },
        .{ .code = -1, .previous_raw_kind = .err },
    };

    for (rows) |row| {
        try expectErrnoProjection(row);
    }
}

test "xarray value and pointer neighbors do not sign-extend into errno slots" {
    const safe_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const floor_gap = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);
    const null_slot = xarray_slot_view.nullSlot();

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, safe_value.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), safe_value.value());
    try std.testing.expectEqual(@as(?isize, null), safe_value.errorCode());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, floor_gap.kind());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), floor_gap.pointerValue());
    try std.testing.expectEqual(@as(?isize, null), floor_gap.errorCode());
    try std.testing.expect(!floor_gap.isTaggedEntry());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.null, null_slot.kind());
    try std.testing.expectEqual(@as(?isize, null), null_slot.errorCode());
    try std.testing.expect(!null_slot.isTaggedEntry());
}
