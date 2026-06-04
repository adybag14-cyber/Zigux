const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const LowRawCase = struct {
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize = null,
    pointer: ?usize = null,
};

fn expectLowRaw(case: LowRawCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.kind == .null, slot.isNull());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expect(!slot.isErr());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
    try std.testing.expectEqual(case.kind == .value, xarray_slot_view.isTaggedInternalEntry(case.raw));
}

test "low raw lane alternates value and pointer slots after null" {
    const cases = [_]LowRawCase{
        .{ .raw = 0, .kind = .null },
        .{ .raw = 1, .kind = .value, .value = 0 },
        .{ .raw = 2, .kind = .pointer, .pointer = 2 },
        .{ .raw = 3, .kind = .value, .value = 1 },
        .{ .raw = 4, .kind = .pointer, .pointer = 4 },
        .{ .raw = 5, .kind = .value, .value = 2 },
        .{ .raw = 6, .kind = .pointer, .pointer = 6 },
        .{ .raw = 7, .kind = .value, .value = 3 },
        .{ .raw = 8, .kind = .pointer, .pointer = 8 },
    };

    for (cases) |case| {
        try expectLowRaw(case);
    }
}

test "low constructors preserve the same raw lane split" {
    const null_slot = xarray_slot_view.nullSlot();
    const value_zero = try xarray_slot_view.fromValue(0);
    const value_one = try xarray_slot_view.fromValue(1);
    const pointer_two = xarray_slot_view.fromPointer(2);
    const pointer_four = xarray_slot_view.fromPointer(4);

    try std.testing.expectEqual(@as(usize, 0), null_slot.rawValue());
    try std.testing.expectEqual(@as(usize, 1), value_zero.rawValue());
    try std.testing.expectEqual(@as(usize, 3), value_one.rawValue());
    try std.testing.expectEqual(@as(usize, 2), pointer_two.rawValue());
    try std.testing.expectEqual(@as(usize, 4), pointer_four.rawValue());

    try std.testing.expectEqual(xarray_slot_view.SlotKind.null, null_slot.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, value_zero.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, value_one.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_two.kind());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_four.kind());
}

test "low raw lane stays below the err_ptr band" {
    const raws = [_]usize{ 0, 1, 2, 3, 4, 5, 6, 7, 8 };

    for (raws) |raw| {
        try std.testing.expect(raw < err_ptr.err_floor);
        try std.testing.expect(!err_ptr.isErrValue(raw));
    }

    try std.testing.expectEqual(@as(usize, 1), try xa_value.makeValue(0));
    try std.testing.expectEqual(@as(usize, 3), try xa_value.makeValue(1));
    try std.testing.expectEqual(@as(usize, 5), try xa_value.makeValue(2));
    try std.testing.expectEqual(@as(usize, 7), try xa_value.makeValue(3));
}
