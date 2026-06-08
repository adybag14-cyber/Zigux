const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const DecodeRow = struct {
    name: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    tagged: bool,
    ok_value: bool,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
};

fn expectRow(row: DecodeRow) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expectEqual(row.kind, slot.kind());
    try std.testing.expectEqual(row.raw, slot.rawValue());
    try std.testing.expectEqual(row.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(row.tagged, xarray_slot_view.isTaggedInternalEntry(row.raw));
    try std.testing.expectEqual(row.ok_value, err_ptr.isOkValue(row.raw));

    try std.testing.expectEqual(row.kind == .null, slot.isNull());
    try std.testing.expectEqual(row.kind == .value, slot.isValue());
    try std.testing.expectEqual(row.kind == .err, slot.isErr());
    try std.testing.expectEqual(row.kind == .pointer, slot.isPointer());

    try std.testing.expectEqual(row.value, slot.value());
    try std.testing.expectEqual(row.error_code, slot.errorCode());
    try std.testing.expectEqual(row.pointer, slot.pointerValue());

    if (row.value) |decoded| {
        try std.testing.expect(xa_value.isValue(row.raw));
        try std.testing.expectEqual(decoded, xa_value.toValue(row.raw));
    } else {
        try std.testing.expect(!slot.isValue());
    }

    if (row.error_code) |decoded| {
        try std.testing.expect(err_ptr.isErrValue(row.raw));
        try std.testing.expectEqual(decoded, err_ptr.toErrorCode(row.raw));
    } else {
        try std.testing.expect(!slot.isErr());
    }

    if (row.pointer) |decoded| {
        try std.testing.expectEqual(decoded, row.raw);
        try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(row.raw));
    } else {
        try std.testing.expect(!slot.isPointer());
    }
}

fn tableRows() ![8]DecodeRow {
    return .{
        .{
            .name = "null sentinel",
            .raw = 0,
            .kind = .null,
            .tagged = false,
            .ok_value = true,
            .value = null,
            .error_code = null,
            .pointer = null,
        },
        .{
            .name = "inline zero",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .tagged = true,
            .ok_value = true,
            .value = 0,
            .error_code = null,
            .pointer = null,
        },
        .{
            .name = "highest inline value",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .tagged = true,
            .ok_value = true,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
        },
        .{
            .name = "small pointer-like raw",
            .raw = 2,
            .kind = .pointer,
            .tagged = false,
            .ok_value = true,
            .value = null,
            .error_code = null,
            .pointer = 2,
        },
        .{
            .name = "last pointer-like raw below err floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .tagged = false,
            .ok_value = true,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "err floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .tagged = true,
            .ok_value = false,
            .value = null,
            .error_code = -4095,
            .pointer = null,
        },
        .{
            .name = "interior errno",
            .raw = err_ptr.fromErrorCode(-22),
            .kind = .err,
            .tagged = true,
            .ok_value = false,
            .value = null,
            .error_code = -22,
            .pointer = null,
        },
        .{
            .name = "top errno",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .tagged = true,
            .ok_value = false,
            .value = null,
            .error_code = -1,
            .pointer = null,
        },
    };
}

test "raw decode table keeps every err_ptr and xarray lane exclusive" {
    const rows = try tableRows();

    for (rows) |row| {
        try std.testing.expect(row.name.len > 0);
        try expectRow(row);
    }
}

test "public constructors reread into the same decode table rows" {
    const rows = try tableRows();
    const constructed = [_]xarray_slot_view.SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(0),
        try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
        xarray_slot_view.fromPointer(2),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
        xarray_slot_view.fromErrorCode(-4095),
        xarray_slot_view.fromErrorCode(-22),
        xarray_slot_view.fromErrorCode(-1),
    };

    for (rows, constructed) |row, slot| {
        try std.testing.expectEqual(row.raw, slot.rawValue());
        try expectRow(row);
        try expectRow(.{
            .name = row.name,
            .raw = slot.rawValue(),
            .kind = row.kind,
            .tagged = row.tagged,
            .ok_value = row.ok_value,
            .value = row.value,
            .error_code = row.error_code,
            .pointer = row.pointer,
        });
    }
}
