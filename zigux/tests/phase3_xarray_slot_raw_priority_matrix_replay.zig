const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const PriorityRow = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    tagged: bool,
    err_predicate: bool,
    value_predicate: bool,
    pointer: ?usize = null,
    value: ?usize = null,
    error_code: ?isize = null,
};

fn expectPriority(row: PriorityRow) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expectEqual(row.raw, slot.rawValue());
    try std.testing.expectEqual(row.kind, slot.kind());
    try std.testing.expectEqual(row.kind == .null, slot.isNull());
    try std.testing.expectEqual(row.kind == .value, slot.isValue());
    try std.testing.expectEqual(row.kind == .err, slot.isErr());
    try std.testing.expectEqual(row.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(row.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(row.tagged, xarray_slot_view.isTaggedInternalEntry(row.raw));
    try std.testing.expectEqual(row.err_predicate, err_ptr.isErrValue(row.raw));
    try std.testing.expectEqual(row.value_predicate, xa_value.isValue(row.raw));
    try std.testing.expectEqual(row.pointer, slot.pointerValue());
    try std.testing.expectEqual(row.value, slot.value());
    try std.testing.expectEqual(row.error_code, slot.errorCode());
}

test "raw priority matrix pins null value pointer and err classification order" {
    const rows = [_]PriorityRow{
        .{
            .name = "raw zero stays null before pointer fallback",
            .raw = 0,
            .kind = .null,
            .tagged = false,
            .err_predicate = false,
            .value_predicate = false,
        },
        .{
            .name = "inline zero odd tag stays value",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .tagged = true,
            .err_predicate = false,
            .value_predicate = true,
            .value = 0,
        },
        .{
            .name = "even raw gap stays pointer",
            .raw = 2,
            .kind = .pointer,
            .tagged = false,
            .err_predicate = false,
            .value_predicate = false,
            .pointer = 2,
        },
        .{
            .name = "highest inline value stays value below err floor",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .tagged = true,
            .err_predicate = false,
            .value_predicate = true,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .name = "last even raw before err floor stays pointer",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .tagged = false,
            .err_predicate = false,
            .value_predicate = false,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "err floor wins over odd xa_value tag",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .tagged = true,
            .err_predicate = true,
            .value_predicate = false,
            .error_code = -4095,
        },
        .{
            .name = "interior odd errno stays err not value",
            .raw = err_ptr.fromErrorCode(-513),
            .kind = .err,
            .tagged = true,
            .err_predicate = true,
            .value_predicate = false,
            .error_code = -513,
        },
        .{
            .name = "top errno stays err not value",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .tagged = true,
            .err_predicate = true,
            .value_predicate = false,
            .error_code = -1,
        },
    };

    for (rows) |row| {
        try expectPriority(row);
    }
}

test "constructor raws replay the same priority rows" {
    const rows = [_]PriorityRow{
        .{
            .name = "null constructor",
            .raw = xarray_slot_view.nullSlot().rawValue(),
            .kind = .null,
            .tagged = false,
            .err_predicate = false,
            .value_predicate = false,
        },
        .{
            .name = "value constructor",
            .raw = (try xarray_slot_view.fromValue(257)).rawValue(),
            .kind = .value,
            .tagged = true,
            .err_predicate = false,
            .value_predicate = true,
            .value = 257,
        },
        .{
            .name = "pointer constructor",
            .raw = xarray_slot_view.fromPointer(0x2000).rawValue(),
            .kind = .pointer,
            .tagged = false,
            .err_predicate = false,
            .value_predicate = false,
            .pointer = 0x2000,
        },
        .{
            .name = "err constructor",
            .raw = xarray_slot_view.fromErrorCode(-22).rawValue(),
            .kind = .err,
            .tagged = true,
            .err_predicate = true,
            .value_predicate = false,
            .error_code = -22,
        },
    };

    for (rows) |row| {
        try expectPriority(row);
    }
}
