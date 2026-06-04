const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const ExpectedSlot = struct {
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer_value: ?usize = null,
    tagged: bool = false,
};

fn expectSlot(expected: ExpectedSlot) !void {
    const slot = xarray_slot_view.fromRaw(expected.raw);

    try testing.expectEqual(expected.raw, slot.rawValue());
    try testing.expectEqual(expected.kind, slot.kind());
    try testing.expectEqual(expected.value, slot.value());
    try testing.expectEqual(expected.error_code, slot.errorCode());
    try testing.expectEqual(expected.pointer_value, slot.pointerValue());
    try testing.expectEqual(expected.tagged, xarray_slot_view.isTaggedInternalEntry(expected.raw));
}

test "classifier walk keeps null value pointer and err lanes disjoint" {
    const value_zero = try xa_value.makeValue(0);
    const value_mid = try xa_value.makeValue(29);
    const value_top = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_low: usize = 2;
    const pointer_gap_top = err_ptr.err_floor - 1;
    const err_floor = err_ptr.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const err_near_floor = err_ptr.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno - 1)));
    const err_top = err_ptr.fromErrorCode(-1);

    const expected = [_]ExpectedSlot{
        .{ .raw = 0, .kind = .null },
        .{ .raw = value_zero, .kind = .value, .value = 0, .tagged = true },
        .{ .raw = pointer_gap_low, .kind = .pointer, .pointer_value = pointer_gap_low },
        .{ .raw = value_mid, .kind = .value, .value = 29, .tagged = true },
        .{ .raw = value_top, .kind = .value, .value = xa_value.safe_inline_limit, .tagged = true },
        .{ .raw = pointer_gap_top, .kind = .pointer, .pointer_value = pointer_gap_top },
        .{ .raw = err_floor, .kind = .err, .error_code = -@as(isize, @intCast(err_ptr.max_errno)), .tagged = true },
        .{ .raw = err_near_floor, .kind = .err, .error_code = -@as(isize, @intCast(err_ptr.max_errno - 1)), .tagged = true },
        .{ .raw = err_top, .kind = .err, .error_code = -1, .tagged = true },
    };

    for (expected) |entry| {
        try expectSlot(entry);
    }
}

test "constructor walk produces the same classifier lanes as raw replay" {
    const slots = [_]xarray_slot_view.SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(0),
        xarray_slot_view.fromPointer(2),
        try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
        xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno))),
        xarray_slot_view.fromErrorCode(-1),
    };
    const kinds = [_]xarray_slot_view.SlotKind{
        .null,
        .value,
        .pointer,
        .value,
        .pointer,
        .err,
        .err,
    };

    for (slots, kinds) |slot, expected_kind| {
        try testing.expectEqual(expected_kind, slot.kind());
    }

    try testing.expectEqual(@as(usize, 0), slots[0].rawValue());
    try testing.expectEqual(@as(?usize, 0), slots[1].value());
    try testing.expectEqual(@as(?usize, 2), slots[2].pointerValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), slots[3].value());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), slots[4].pointerValue());
    try testing.expectEqual(@as(?isize, -4095), slots[5].errorCode());
    try testing.expectEqual(@as(?isize, -1), slots[6].errorCode());
}

test "odd err raws prefer err_ptr over xa_value during classification" {
    const raw = err_ptr.fromErrorCode(-1);
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expect(!xa_value.isValue(raw));
    try testing.expect(slot.isErr());
    try testing.expect(!slot.isValue());
    try testing.expectEqual(@as(?isize, -1), slot.errorCode());
}
