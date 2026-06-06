const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;
const SlotView = xarray_slot_view.SlotView;

const AccessorExpectation = struct {
    name: []const u8,
    slot: SlotView,
    kind: SlotKind,
    value: ?usize,
    err: ?isize,
    pointer: ?usize,
    tagged: bool,
};

fn expectAccessors(row: AccessorExpectation) !void {
    try std.testing.expectEqual(row.kind, row.slot.kind());
    try std.testing.expectEqual(row.value, row.slot.value());
    try std.testing.expectEqual(row.err, row.slot.errorCode());
    try std.testing.expectEqual(row.pointer, row.slot.pointerValue());
    try std.testing.expectEqual(row.tagged, row.slot.isTaggedEntry());

    try std.testing.expectEqual(row.kind == .null, row.slot.isNull());
    try std.testing.expectEqual(row.kind == .value, row.slot.isValue());
    try std.testing.expectEqual(row.kind == .err, row.slot.isErr());
    try std.testing.expectEqual(row.kind == .pointer, row.slot.isPointer());

    const open_accessors =
        @intFromBool(row.slot.value() != null) +
        @intFromBool(row.slot.errorCode() != null) +
        @intFromBool(row.slot.pointerValue() != null);

    const expected_open_accessors: u2 = switch (row.kind) {
        .null => 0,
        .value, .err, .pointer => 1,
    };

    try std.testing.expectEqual(expected_open_accessors, open_accessors);
}

test "constructor-created slots open exactly one accessor outside null" {
    const rows = [_]AccessorExpectation{
        .{
            .name = "null constructor",
            .slot = xarray_slot_view.nullSlot(),
            .kind = .null,
            .value = null,
            .err = null,
            .pointer = null,
            .tagged = false,
        },
        .{
            .name = "inline value constructor",
            .slot = try xarray_slot_view.fromValue(37),
            .kind = .value,
            .value = 37,
            .err = null,
            .pointer = null,
            .tagged = true,
        },
        .{
            .name = "error constructor",
            .slot = xarray_slot_view.fromErrorCode(-22),
            .kind = .err,
            .value = null,
            .err = -22,
            .pointer = null,
            .tagged = true,
        },
        .{
            .name = "pointer constructor",
            .slot = xarray_slot_view.fromPointer(0x4000),
            .kind = .pointer,
            .value = null,
            .err = null,
            .pointer = 0x4000,
            .tagged = false,
        },
    };

    for (rows) |row| {
        try std.testing.expect(row.name.len != 0);
        try expectAccessors(row);
    }
}

test "raw boundary slots preserve accessor closure across value pointer and err lanes" {
    const highest_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const rejected_alias_raw = ((xa_value.safe_inline_limit + 1) << 1) | xa_value.value_tag_mask;
    const top_err_raw = err_ptr.fromErrorCode(-1);

    const rows = [_]AccessorExpectation{
        .{
            .name = "highest inline value",
            .slot = xarray_slot_view.fromRaw(highest_value_raw),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .err = null,
            .pointer = null,
            .tagged = true,
        },
        .{
            .name = "pointer gap before err floor",
            .slot = xarray_slot_view.fromRaw(pointer_gap_raw),
            .kind = .pointer,
            .value = null,
            .err = null,
            .pointer = pointer_gap_raw,
            .tagged = false,
        },
        .{
            .name = "rejected value alias at err floor",
            .slot = xarray_slot_view.fromRaw(rejected_alias_raw),
            .kind = .err,
            .value = null,
            .err = -4095,
            .pointer = null,
            .tagged = true,
        },
        .{
            .name = "top errno raw",
            .slot = xarray_slot_view.fromRaw(top_err_raw),
            .kind = .err,
            .value = null,
            .err = -1,
            .pointer = null,
            .tagged = true,
        },
    };

    try std.testing.expectEqual(err_ptr.err_floor - 2, highest_value_raw);
    try std.testing.expectEqual(err_ptr.err_floor, rejected_alias_raw);
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1));

    for (rows) |row| {
        try std.testing.expect(row.name.len != 0);
        try expectAccessors(row);
    }
}
