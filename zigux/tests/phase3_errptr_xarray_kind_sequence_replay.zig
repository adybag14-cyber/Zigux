const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const Row = struct {
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    errno: ?isize = null,
    pointer: ?usize = null,
    tagged: bool,
};

fn expectRow(row: Row) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expectEqual(row.kind, slot.kind());
    try std.testing.expectEqual(row.raw, slot.rawValue());
    try std.testing.expectEqual(row.value, slot.value());
    try std.testing.expectEqual(row.errno, slot.errorCode());
    try std.testing.expectEqual(row.pointer, slot.pointerValue());
    try std.testing.expectEqual(row.tagged, slot.isTaggedEntry());

    try std.testing.expectEqual(row.kind == .null, slot.isNull());
    try std.testing.expectEqual(row.kind == .value, slot.isValue());
    try std.testing.expectEqual(row.kind == .err, slot.isErr());
    try std.testing.expectEqual(row.kind == .pointer, slot.isPointer());

    try std.testing.expectEqual(err_ptr.isErrValue(row.raw), row.kind == .err);
    try std.testing.expectEqual(xa_value.isValue(row.raw), row.kind == .value);
    try std.testing.expectEqual(xarray_slot_view.isTaggedInternalEntry(row.raw), row.tagged);
}

test "raw kind sequence preserves null value pointer and errno priority" {
    const rows = [_]Row{
        .{ .raw = 0, .kind = .null, .tagged = false },
        .{ .raw = try xa_value.makeValue(0), .kind = .value, .value = 0, .tagged = true },
        .{ .raw = 2, .kind = .pointer, .pointer = 2, .tagged = false },
        .{ .raw = try xa_value.makeValue(1), .kind = .value, .value = 1, .tagged = true },
        .{ .raw = 0x1000, .kind = .pointer, .pointer = 0x1000, .tagged = false },
        .{
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit - 1),
            .kind = .value,
            .value = xa_value.safe_inline_limit - 1,
            .tagged = true,
        },
        .{
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .tagged = true,
        },
        .{
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer = err_ptr.err_floor - 1,
            .tagged = false,
        },
        .{
            .raw = err_ptr.err_floor,
            .kind = .err,
            .errno = -4095,
            .tagged = true,
        },
        .{
            .raw = err_ptr.err_floor + 1,
            .kind = .err,
            .errno = -4094,
            .tagged = true,
        },
        .{
            .raw = err_ptr.fromErrorCode(-2),
            .kind = .err,
            .errno = -2,
            .tagged = true,
        },
        .{
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .errno = -1,
            .tagged = true,
        },
    };

    var previous_raw: ?usize = null;
    for (rows) |row| {
        if (previous_raw) |previous| {
            try std.testing.expect(row.raw > previous);
        }
        previous_raw = row.raw;
        try expectRow(row);
    }
}

test "constructor raws replay the same kind sequence after reread" {
    const constructed = [_]xarray_slot_view.SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(0),
        xarray_slot_view.fromPointer(2),
        try xarray_slot_view.fromValue(1),
        xarray_slot_view.fromPointer(0x1000),
        try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
        xarray_slot_view.fromErrorCode(-4095),
        xarray_slot_view.fromErrorCode(-4094),
        xarray_slot_view.fromErrorCode(-2),
        xarray_slot_view.fromErrorCode(-1),
    };

    var seen_value = false;
    var seen_pointer = false;
    var seen_err = false;

    for (constructed) |slot| {
        const reread = xarray_slot_view.fromRaw(slot.rawValue());
        try std.testing.expectEqual(slot.kind(), reread.kind());
        try std.testing.expectEqual(slot.value(), reread.value());
        try std.testing.expectEqual(slot.errorCode(), reread.errorCode());
        try std.testing.expectEqual(slot.pointerValue(), reread.pointerValue());

        seen_value = seen_value or reread.isValue();
        seen_pointer = seen_pointer or reread.isPointer();
        seen_err = seen_err or reread.isErr();
    }

    try std.testing.expect(seen_value);
    try std.testing.expect(seen_pointer);
    try std.testing.expect(seen_err);
}
