const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

fn expectTaggedComplement(slot: xarray_slot_view.SlotView, expected_kind: SlotKind) !void {
    try std.testing.expectEqual(expected_kind, slot.kind());
    try std.testing.expectEqual(expected_kind == .value, slot.isValue());
    try std.testing.expectEqual(expected_kind == .err, slot.isErr());
    try std.testing.expectEqual(expected_kind == .null, slot.isNull());
    try std.testing.expectEqual(expected_kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(
        expected_kind == .value or expected_kind == .err,
        slot.isTaggedEntry(),
    );
    try std.testing.expectEqual(
        expected_kind == .value or expected_kind == .err,
        xarray_slot_view.isTaggedInternalEntry(slot.rawValue()),
    );
}

test "tagged-entry predicate is the complement of null and pointer constructors" {
    const cases = [_]struct {
        slot: xarray_slot_view.SlotView,
        kind: SlotKind,
    }{
        .{ .slot = xarray_slot_view.nullSlot(), .kind = .null },
        .{ .slot = try xarray_slot_view.fromValue(0), .kind = .value },
        .{ .slot = try xarray_slot_view.fromValue(29), .kind = .value },
        .{ .slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit), .kind = .value },
        .{ .slot = xarray_slot_view.fromPointer(2), .kind = .pointer },
        .{ .slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1), .kind = .pointer },
        .{ .slot = xarray_slot_view.fromErrorCode(-4095), .kind = .err },
        .{ .slot = xarray_slot_view.fromErrorCode(-22), .kind = .err },
        .{ .slot = xarray_slot_view.fromErrorCode(-1), .kind = .err },
    };

    for (cases) |case| {
        try expectTaggedComplement(case.slot, case.kind);
    }
}

test "raw boundary rows keep tagged entry aligned with decoded lane" {
    const highest_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const cases = [_]struct {
        raw: usize,
        kind: SlotKind,
    }{
        .{ .raw = 0, .kind = .null },
        .{ .raw = 1, .kind = .value },
        .{ .raw = highest_value_raw, .kind = .value },
        .{ .raw = err_ptr.err_floor - 1, .kind = .pointer },
        .{ .raw = err_ptr.err_floor, .kind = .err },
        .{ .raw = err_ptr.fromErrorCode(-2048), .kind = .err },
        .{ .raw = err_ptr.fromErrorCode(-1), .kind = .err },
    };

    for (cases) |case| {
        const slot = xarray_slot_view.fromRaw(case.raw);

        try expectTaggedComplement(slot, case.kind);
        try std.testing.expectEqual(slot.rawValue(), case.raw);
        try std.testing.expectEqual(slot.isValue(), xa_value.isValue(case.raw));
        try std.testing.expectEqual(slot.isErr(), err_ptr.isErrValue(case.raw));
    }
}

test "rejected inline alias remains tagged only as err_ptr after raw projection" {
    const rejected_value = xa_value.safe_inline_limit + 1;
    const projected_raw = (rejected_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(projected_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected_value));
    try std.testing.expectEqual(err_ptr.err_floor, projected_raw);
    try expectTaggedComplement(slot, .err);
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, -4095), slot.errorCode());
}
