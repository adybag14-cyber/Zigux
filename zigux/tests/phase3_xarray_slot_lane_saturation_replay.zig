const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot = @import("xarray_slot_view");

const SlotKind = xarray_slot.SlotKind;

const ExpectedSlot = struct {
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    err: ?isize = null,
    pointer: ?usize = null,
    tagged: bool = false,
};

fn expectSlot(expected: ExpectedSlot) !void {
    const slot = xarray_slot.fromRaw(expected.raw);

    try testing.expectEqual(expected.raw, slot.rawValue());
    try testing.expectEqual(expected.kind, slot.kind());
    try testing.expectEqual(expected.kind == .null, slot.isNull());
    try testing.expectEqual(expected.kind == .value, slot.isValue());
    try testing.expectEqual(expected.kind == .err, slot.isErr());
    try testing.expectEqual(expected.kind == .pointer, slot.isPointer());
    try testing.expectEqual(expected.tagged, slot.isTaggedEntry());
    try testing.expectEqual(expected.tagged, xarray_slot.isTaggedInternalEntry(expected.raw));
    try testing.expectEqual(expected.value, slot.value());
    try testing.expectEqual(expected.err, slot.errorCode());
    try testing.expectEqual(expected.pointer, slot.pointerValue());
}

test "representative raw slots saturate exactly one public lane" {
    const rows = [_]ExpectedSlot{
        .{ .raw = 0, .kind = .null },
        .{ .raw = try xa_value.makeValue(0), .kind = .value, .value = 0, .tagged = true },
        .{ .raw = try xa_value.makeValue(1), .kind = .value, .value = 1, .tagged = true },
        .{ .raw = 0x1000, .kind = .pointer, .pointer = 0x1000 },
        .{ .raw = err_ptr.err_floor - 1, .kind = .pointer, .pointer = err_ptr.err_floor - 1 },
        .{ .raw = err_ptr.err_floor, .kind = .err, .err = -4095, .tagged = true },
        .{ .raw = err_ptr.fromErrorCode(-512), .kind = .err, .err = -512, .tagged = true },
        .{ .raw = err_ptr.fromErrorCode(-1), .kind = .err, .err = -1, .tagged = true },
    };

    for (rows) |row| {
        try expectSlot(row);
    }
}

test "boundary window alternates value and pointer before the err_ptr floor" {
    const rows = [_]ExpectedSlot{
        .{
            .raw = err_ptr.err_floor - 4,
            .kind = .value,
            .value = (err_ptr.err_floor - 4) >> 1,
            .tagged = true,
        },
        .{ .raw = err_ptr.err_floor - 3, .kind = .pointer, .pointer = err_ptr.err_floor - 3 },
        .{
            .raw = err_ptr.err_floor - 2,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .tagged = true,
        },
        .{ .raw = err_ptr.err_floor - 1, .kind = .pointer, .pointer = err_ptr.err_floor - 1 },
        .{ .raw = err_ptr.err_floor, .kind = .err, .err = -4095, .tagged = true },
        .{ .raw = err_ptr.err_floor + 1, .kind = .err, .err = -4094, .tagged = true },
        .{ .raw = err_ptr.err_floor + 2, .kind = .err, .err = -4093, .tagged = true },
    };

    for (rows) |row| {
        try expectSlot(row);
    }
}

test "public constructors land on the same saturated raw lanes" {
    const value_slot = try xarray_slot.fromValue(xa_value.safe_inline_limit);
    const pointer_slot = xarray_slot.fromPointer(err_ptr.err_floor - 1);
    const err_slot = xarray_slot.fromErrorCode(-4095);
    const null_slot = xarray_slot.nullSlot();

    try testing.expectEqual(SlotKind.value, value_slot.kind());
    try testing.expectEqual(err_ptr.err_floor - 2, value_slot.rawValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try testing.expectEqual(@as(?isize, null), value_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), value_slot.pointerValue());

    try testing.expectEqual(SlotKind.pointer, pointer_slot.kind());
    try testing.expectEqual(err_ptr.err_floor - 1, pointer_slot.rawValue());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), pointer_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), pointer_slot.value());
    try testing.expectEqual(@as(?isize, null), pointer_slot.errorCode());

    try testing.expectEqual(SlotKind.err, err_slot.kind());
    try testing.expectEqual(err_ptr.err_floor, err_slot.rawValue());
    try testing.expectEqual(@as(?isize, -4095), err_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), err_slot.value());
    try testing.expectEqual(@as(?usize, null), err_slot.pointerValue());

    try testing.expectEqual(SlotKind.null, null_slot.kind());
    try testing.expectEqual(@as(usize, 0), null_slot.rawValue());
    try testing.expectEqual(@as(?usize, null), null_slot.value());
    try testing.expectEqual(@as(?isize, null), null_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), null_slot.pointerValue());
}
