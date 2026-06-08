const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Row = struct {
    name: []const u8,
    raw: usize,
    expected_kind: xarray_slot_view.SlotKind,
    expected_error: ?isize,
};

fn expectOkComplement(row: Row) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expectEqual(row.expected_kind, slot.kind());
    try std.testing.expectEqual(row.raw, slot.rawValue());
    try std.testing.expectEqual(!slot.isErr(), err_ptr.isOkValue(row.raw));
    try std.testing.expectEqual(slot.isErr(), err_ptr.isErrValue(row.raw));
    try std.testing.expectEqual(row.expected_error, slot.errorCode());

    if (row.expected_error) |code| {
        try std.testing.expectEqual(err_ptr.fromErrorCode(code), row.raw);
        try std.testing.expectEqual(code, err_ptr.toErrorCode(row.raw));
        try std.testing.expectEqual(@as(?usize, null), slot.value());
        try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    } else {
        try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    }
}

test "err_ptr ok predicate complements xarray error lane rows" {
    const rows = [_]Row{
        .{
            .name = "null sentinel",
            .raw = 0,
            .expected_kind = .null,
            .expected_error = null,
        },
        .{
            .name = "inline zero value",
            .raw = try xa_value.makeValue(0),
            .expected_kind = .value,
            .expected_error = null,
        },
        .{
            .name = "safe inline limit",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .expected_kind = .value,
            .expected_error = null,
        },
        .{
            .name = "first pointer gap",
            .raw = 2,
            .expected_kind = .pointer,
            .expected_error = null,
        },
        .{
            .name = "last pointer before err floor",
            .raw = err_ptr.err_floor - 1,
            .expected_kind = .pointer,
            .expected_error = null,
        },
        .{
            .name = "err floor",
            .raw = err_ptr.fromErrorCode(-4095),
            .expected_kind = .err,
            .expected_error = -4095,
        },
        .{
            .name = "interior even errno",
            .raw = err_ptr.fromErrorCode(-128),
            .expected_kind = .err,
            .expected_error = -128,
        },
        .{
            .name = "top odd errno",
            .raw = err_ptr.fromErrorCode(-1),
            .expected_kind = .err,
            .expected_error = -1,
        },
    };

    for (rows) |row| {
        errdefer std.debug.print("row failed: {s}\n", .{row.name});
        try expectOkComplement(row);
    }
}

test "constructor rereads preserve ok complement classification" {
    const slots = [_]xarray_slot_view.SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(7),
        xarray_slot_view.fromPointer(0x1000),
        xarray_slot_view.fromErrorCode(-22),
    };

    for (slots) |slot| {
        const reread = xarray_slot_view.fromRaw(slot.rawValue());

        try std.testing.expectEqual(slot.kind(), reread.kind());
        try std.testing.expectEqual(slot.rawValue(), reread.rawValue());
        try std.testing.expectEqual(!reread.isErr(), err_ptr.isOkValue(reread.rawValue()));
        try std.testing.expectEqual(reread.isErr(), err_ptr.isErrValue(reread.rawValue()));
    }
}
