const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const BoundaryRow = struct {
    label: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
    tagged: bool,
};

fn rejectedValueRaw(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

fn expectBoundaryRow(row: BoundaryRow) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expectEqual(row.kind, slot.kind());
    try std.testing.expectEqual(row.kind == .null, slot.isNull());
    try std.testing.expectEqual(row.kind == .value, slot.isValue());
    try std.testing.expectEqual(row.kind == .err, slot.isErr());
    try std.testing.expectEqual(row.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(row.raw, slot.rawValue());
    try std.testing.expectEqual(row.value, slot.value());
    try std.testing.expectEqual(row.error_code, slot.errorCode());
    try std.testing.expectEqual(row.pointer, slot.pointerValue());
    try std.testing.expectEqual(row.tagged, slot.isTaggedEntry());

    try std.testing.expectEqual(row.raw >= err_ptr.err_floor, err_ptr.isErrValue(row.raw));
    try std.testing.expectEqual(row.kind == .value, xa_value.isValue(row.raw));
}

test "safe inline ceiling, raw pointer gap, and err floor keep adjacent lanes stable" {
    const rows = [_]BoundaryRow{
        .{
            .label = "next-to-highest safe inline value",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit - 1),
            .kind = .value,
            .value = xa_value.safe_inline_limit - 1,
            .error_code = null,
            .pointer = null,
            .tagged = true,
        },
        .{
            .label = "highest safe inline value",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
            .tagged = true,
        },
        .{
            .label = "raw pointer gap two below floor",
            .raw = err_ptr.err_floor - 3,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 3,
            .tagged = false,
        },
        .{
            .label = "raw pointer gap one below floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
            .tagged = false,
        },
        .{
            .label = "first rejected inline alias",
            .raw = rejectedValueRaw(xa_value.safe_inline_limit + 1),
            .kind = .err,
            .value = null,
            .error_code = -4095,
            .pointer = null,
            .tagged = true,
        },
        .{
            .label = "second rejected inline alias",
            .raw = rejectedValueRaw(xa_value.safe_inline_limit + 2),
            .kind = .err,
            .value = null,
            .error_code = -4093,
            .pointer = null,
            .tagged = true,
        },
    };

    try std.testing.expectEqual(err_ptr.err_floor - 4, rows[0].raw);
    try std.testing.expectEqual(err_ptr.err_floor - 2, rows[1].raw);
    try std.testing.expectEqual(err_ptr.err_floor, rows[4].raw);
    try std.testing.expectEqual(err_ptr.err_floor + 2, rows[5].raw);

    for (rows) |row| {
        try expectBoundaryRow(row);
    }
}

test "constructor and raw projections agree at the inline-to-error boundary" {
    const safe_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const rejected_raw = rejectedValueRaw(xa_value.safe_inline_limit + 1);
    const rejected_slot = xarray_slot_view.fromRaw(rejected_raw);
    const floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const gap_slot = xarray_slot_view.fromRaw(safe_slot.rawValue() + 1);

    try std.testing.expectEqual(err_ptr.err_floor - 2, safe_slot.rawValue());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), safe_slot.value());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, safe_slot.kind());

    try std.testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1),
    );
    try std.testing.expectEqual(err_ptr.err_floor, rejected_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, rejected_slot.kind());
    try std.testing.expectEqual(@as(?isize, -4095), rejected_slot.errorCode());
    try std.testing.expectEqual(floor_slot.rawValue(), rejected_slot.rawValue());
    try std.testing.expectEqual(floor_slot.errorCode(), rejected_slot.errorCode());

    try std.testing.expectEqual(err_ptr.err_floor - 1, gap_slot.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap_slot.kind());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), gap_slot.pointerValue());
    try std.testing.expect(!gap_slot.isTaggedEntry());
}
