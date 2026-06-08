const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;
const SlotView = xarray_slot_view.SlotView;

const Row = struct {
    label: []const u8,
    raw: usize,
    expected_kind: SlotKind,
    tagged: bool,
    value: ?usize = null,
    code: ?isize = null,
    pointer: ?usize = null,
};

fn expectSlot(row: Row) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expectEqual(row.raw, slot.rawValue());
    try std.testing.expectEqual(row.expected_kind, slot.kind());
    try std.testing.expectEqual(row.expected_kind == .null, slot.isNull());
    try std.testing.expectEqual(row.expected_kind == .value, slot.isValue());
    try std.testing.expectEqual(row.expected_kind == .err, slot.isErr());
    try std.testing.expectEqual(row.expected_kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(row.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(row.tagged, xarray_slot_view.isTaggedInternalEntry(row.raw));
    try std.testing.expectEqual(row.value, slot.value());
    try std.testing.expectEqual(row.code, slot.errorCode());
    try std.testing.expectEqual(row.pointer, slot.pointerValue());

    if (slot.isValue()) {
        try std.testing.expect(xa_value.isValue(row.raw));
        try std.testing.expect(!err_ptr.isErrValue(row.raw));
    } else if (slot.isErr()) {
        try std.testing.expect(err_ptr.isErrValue(row.raw));
        try std.testing.expect(!xa_value.isValue(row.raw));
    } else {
        try std.testing.expect(!err_ptr.isErrValue(row.raw));
        try std.testing.expect(!xa_value.isValue(row.raw));
    }
}

fn expectConstructorReread(slot: SlotView, expected_kind: SlotKind, tagged: bool) !void {
    const reread = xarray_slot_view.fromRaw(slot.rawValue());

    try std.testing.expectEqual(slot.rawValue(), reread.rawValue());
    try std.testing.expectEqual(expected_kind, reread.kind());
    try std.testing.expectEqual(tagged, reread.isTaggedEntry());
    try std.testing.expectEqual(slot.value(), reread.value());
    try std.testing.expectEqual(slot.errorCode(), reread.errorCode());
    try std.testing.expectEqual(slot.pointerValue(), reread.pointerValue());
}

test "tagged entry precedence keeps err_ptr raws above xa_value raws" {
    const final_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const overlapping_alias = ((xa_value.safe_inline_limit + 1) << 1) | xa_value.value_tag_mask;
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const rows = [_]Row{
        .{
            .label = "null sentinel",
            .raw = 0,
            .expected_kind = .null,
            .tagged = false,
        },
        .{
            .label = "inline zero value",
            .raw = try xa_value.makeValue(0),
            .expected_kind = .value,
            .tagged = true,
            .value = 0,
        },
        .{
            .label = "highest inline value",
            .raw = final_value_raw,
            .expected_kind = .value,
            .tagged = true,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .label = "aligned pointer lane",
            .raw = 0x1000,
            .expected_kind = .pointer,
            .tagged = false,
            .pointer = 0x1000,
        },
        .{
            .label = "final pointer-like raw below err floor",
            .raw = pointer_gap_raw,
            .expected_kind = .pointer,
            .tagged = false,
            .pointer = pointer_gap_raw,
        },
        .{
            .label = "first rejected inline alias becomes err floor",
            .raw = overlapping_alias,
            .expected_kind = .err,
            .tagged = true,
            .code = -4095,
        },
        .{
            .label = "interior errno with xa tag bit clear",
            .raw = err_ptr.fromErrorCode(-128),
            .expected_kind = .err,
            .tagged = true,
            .code = -128,
        },
        .{
            .label = "top errno with xa tag bit set",
            .raw = err_ptr.fromErrorCode(-1),
            .expected_kind = .err,
            .tagged = true,
            .code = -1,
        },
    };

    for (rows) |row| {
        try expectSlot(row);
    }
}

test "constructor rereads preserve tagged entry precedence" {
    try expectConstructorReread(xarray_slot_view.nullSlot(), .null, false);
    try expectConstructorReread(try xarray_slot_view.fromValue(0), .value, true);
    try expectConstructorReread(try xarray_slot_view.fromValue(xa_value.safe_inline_limit), .value, true);
    try expectConstructorReread(xarray_slot_view.fromPointer(err_ptr.err_floor - 1), .pointer, false);
    try expectConstructorReread(xarray_slot_view.fromErrorCode(-4095), .err, true);
    try expectConstructorReread(xarray_slot_view.fromErrorCode(-1), .err, true);
}
