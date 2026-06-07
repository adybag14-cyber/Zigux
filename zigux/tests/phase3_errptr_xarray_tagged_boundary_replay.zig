const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const BoundaryRow = struct {
    label: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    tagged: bool,
    value: ?usize,
    err: ?isize,
    pointer: ?usize,
};

fn expectBoundaryRow(row: BoundaryRow) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expectEqual(row.kind, slot.kind());
    try std.testing.expectEqual(row.tagged, xarray_slot_view.isTaggedInternalEntry(row.raw));
    try std.testing.expectEqual(row.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(row.value, slot.value());
    try std.testing.expectEqual(row.err, slot.errorCode());
    try std.testing.expectEqual(row.pointer, slot.pointerValue());

    switch (row.kind) {
        .null => try std.testing.expectEqual(@as(usize, 0), row.raw),
        .value => try std.testing.expect(xa_value.isValue(row.raw)),
        .err => try std.testing.expect(err_ptr.isErrValue(row.raw)),
        .pointer => try std.testing.expect(err_ptr.isOkValue(row.raw) and !xa_value.isValue(row.raw)),
    }
}

test "tagged boundary replay keeps value pointer and err transitions explicit" {
    const max_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const first_rejected_value_raw = ((xa_value.safe_inline_limit + 1) << 1) | xa_value.value_tag_mask;
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const err_floor_raw = err_ptr.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try std.testing.expectEqual(err_ptr.err_floor - 2, max_value_raw);
    try std.testing.expectEqual(err_ptr.err_floor, first_rejected_value_raw);
    try std.testing.expectEqual(err_ptr.err_floor, err_floor_raw);

    const rows = [_]BoundaryRow{
        .{
            .label = "null",
            .raw = 0,
            .kind = .null,
            .tagged = false,
            .value = null,
            .err = null,
            .pointer = null,
        },
        .{
            .label = "inline-zero",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .tagged = true,
            .value = 0,
            .err = null,
            .pointer = null,
        },
        .{
            .label = "max-inline",
            .raw = max_value_raw,
            .kind = .value,
            .tagged = true,
            .value = xa_value.safe_inline_limit,
            .err = null,
            .pointer = null,
        },
        .{
            .label = "pointer-gap",
            .raw = pointer_gap_raw,
            .kind = .pointer,
            .tagged = false,
            .value = null,
            .err = null,
            .pointer = pointer_gap_raw,
        },
        .{
            .label = "rejected-inline-alias",
            .raw = first_rejected_value_raw,
            .kind = .err,
            .tagged = true,
            .value = null,
            .err = -4095,
            .pointer = null,
        },
        .{
            .label = "interior-errno",
            .raw = err_ptr.fromErrorCode(-512),
            .kind = .err,
            .tagged = true,
            .value = null,
            .err = -512,
            .pointer = null,
        },
        .{
            .label = "top-errno",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .tagged = true,
            .value = null,
            .err = -1,
            .pointer = null,
        },
    };

    for (rows) |row| {
        try std.testing.expect(row.label.len > 0);
        try expectBoundaryRow(row);
    }
}

test "tagged boundary replay preserves one-step raw adjacency around the err floor" {
    const max_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const err_floor_raw = err_ptr.err_floor;

    try std.testing.expectEqual(max_value_raw + 1, pointer_gap_raw);
    try std.testing.expectEqual(pointer_gap_raw + 1, err_floor_raw);

    const value_slot = xarray_slot_view.fromRaw(max_value_raw);
    const pointer_slot = xarray_slot_view.fromRaw(pointer_gap_raw);
    const err_slot = xarray_slot_view.fromRaw(err_floor_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, err_slot.kind());
    try std.testing.expect(value_slot.isTaggedEntry());
    try std.testing.expect(!pointer_slot.isTaggedEntry());
    try std.testing.expect(err_slot.isTaggedEntry());
}
