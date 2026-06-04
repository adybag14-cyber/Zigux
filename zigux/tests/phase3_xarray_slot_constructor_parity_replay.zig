const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

fn expectSameView(constructed: xarray_slot_view.SlotView, raw: usize, kind: SlotKind) !void {
    const decoded = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(raw, constructed.rawValue());
    try std.testing.expectEqual(raw, decoded.rawValue());
    try std.testing.expectEqual(kind, constructed.kind());
    try std.testing.expectEqual(kind, decoded.kind());
    try std.testing.expectEqual(decoded.value(), constructed.value());
    try std.testing.expectEqual(decoded.errorCode(), constructed.errorCode());
    try std.testing.expectEqual(decoded.pointerValue(), constructed.pointerValue());
    try std.testing.expectEqual(xarray_slot_view.isTaggedInternalEntry(raw), kind != .null and kind != .pointer);
}

test "public constructors match raw decoding for representative xarray slot lanes" {
    try expectSameView(xarray_slot_view.nullSlot(), 0, .null);
    try expectSameView(
        try xarray_slot_view.fromValue(0),
        try xa_value.makeValue(0),
        .value,
    );
    try expectSameView(
        try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
        try xa_value.makeValue(xa_value.safe_inline_limit),
        .value,
    );
    try expectSameView(
        xarray_slot_view.fromPointer(2),
        2,
        .pointer,
    );
    try expectSameView(
        xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
        err_ptr.err_floor - 1,
        .pointer,
    );
    try expectSameView(
        xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno))),
        err_ptr.err_floor,
        .err,
    );
    try expectSameView(
        xarray_slot_view.fromErrorCode(-1),
        err_ptr.fromErrorCode(-1),
        .err,
    );
}

test "constructor parity keeps inactive accessors closed" {
    const rows = [_]struct {
        slot: xarray_slot_view.SlotView,
        raw: usize,
        kind: SlotKind,
    }{
        .{ .slot = xarray_slot_view.nullSlot(), .raw = 0, .kind = .null },
        .{ .slot = try xarray_slot_view.fromValue(7), .raw = try xa_value.makeValue(7), .kind = .value },
        .{ .slot = xarray_slot_view.fromPointer(0x4000), .raw = 0x4000, .kind = .pointer },
        .{ .slot = xarray_slot_view.fromErrorCode(-22), .raw = err_ptr.fromErrorCode(-22), .kind = .err },
    };

    for (rows) |row| {
        const decoded = xarray_slot_view.fromRaw(row.raw);

        try std.testing.expectEqual(row.kind == .value, row.slot.value() != null);
        try std.testing.expectEqual(row.kind == .err, row.slot.errorCode() != null);
        try std.testing.expectEqual(row.kind == .pointer, row.slot.pointerValue() != null);
        try std.testing.expectEqual(row.slot.value(), decoded.value());
        try std.testing.expectEqual(row.slot.errorCode(), decoded.errorCode());
        try std.testing.expectEqual(row.slot.pointerValue(), decoded.pointerValue());
    }
}
