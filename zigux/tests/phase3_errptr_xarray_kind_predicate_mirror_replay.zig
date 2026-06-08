const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;
const SlotView = xarray_slot_view.SlotView;

const PredicateMirror = struct {
    raw: usize,
    expected_kind: SlotKind,
};

fn expectKindPredicateMirror(slot: SlotView, expected_kind: SlotKind) !void {
    try std.testing.expectEqual(expected_kind, slot.kind());
    try std.testing.expectEqual(expected_kind == .null, slot.isNull());
    try std.testing.expectEqual(expected_kind == .value, slot.isValue());
    try std.testing.expectEqual(expected_kind == .err, slot.isErr());
    try std.testing.expectEqual(expected_kind == .pointer, slot.isPointer());

    const predicate_count =
        @intFromBool(slot.isNull()) +
        @intFromBool(slot.isValue()) +
        @intFromBool(slot.isErr()) +
        @intFromBool(slot.isPointer());
    try std.testing.expectEqual(@as(u4, 1), predicate_count);
}

fn expectRawMirror(row: PredicateMirror) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try expectKindPredicateMirror(slot, row.expected_kind);
    try std.testing.expectEqual(row.raw, slot.rawValue());
}

test "raw slot kind mirrors the four public predicates" {
    const raw_rows = [_]PredicateMirror{
        .{ .raw = 0, .expected_kind = .null },
        .{ .raw = try xa_value.makeValue(0), .expected_kind = .value },
        .{ .raw = try xa_value.makeValue(1), .expected_kind = .value },
        .{ .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .expected_kind = .value },
        .{ .raw = 2, .expected_kind = .pointer },
        .{ .raw = 0x1000, .expected_kind = .pointer },
        .{ .raw = err_ptr.err_floor - 1, .expected_kind = .pointer },
        .{ .raw = err_ptr.err_floor, .expected_kind = .err },
        .{ .raw = err_ptr.fromErrorCode(-4094), .expected_kind = .err },
        .{ .raw = err_ptr.fromErrorCode(-1), .expected_kind = .err },
    };

    for (raw_rows) |row| {
        try expectRawMirror(row);
    }
}

test "constructor slots keep kind and predicate mirrors after raw reread" {
    const constructor_rows = [_]SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(0),
        try xarray_slot_view.fromValue(37),
        try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
        xarray_slot_view.fromPointer(2),
        xarray_slot_view.fromPointer(0x1000),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
        xarray_slot_view.fromErrorCode(-4095),
        xarray_slot_view.fromErrorCode(-1024),
        xarray_slot_view.fromErrorCode(-1),
    };

    for (constructor_rows) |slot| {
        try expectKindPredicateMirror(slot, slot.kind());
        try expectKindPredicateMirror(xarray_slot_view.fromRaw(slot.rawValue()), slot.kind());
    }
}
