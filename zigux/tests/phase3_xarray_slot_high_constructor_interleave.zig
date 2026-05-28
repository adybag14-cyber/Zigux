const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

test "high public constructors interleave value and pointer raws exactly below err floor" {
    const values = [_]usize{
        xa_value.safe_inline_limit - 3,
        xa_value.safe_inline_limit - 2,
        xa_value.safe_inline_limit - 1,
        xa_value.safe_inline_limit,
    };
    const slots = [_]xarray_slot_view.SlotView{
        try xarray_slot_view.fromValue(values[0]),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 7),
        try xarray_slot_view.fromValue(values[1]),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 5),
        try xarray_slot_view.fromValue(values[2]),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 3),
        try xarray_slot_view.fromValue(values[3]),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
    };
    const expected = [_]struct {
        raw: usize,
        kind: SlotKind,
        value: ?usize,
        pointer: ?usize,
    }{
        .{ .raw = err_ptr.err_floor - 8, .kind = .value, .value = values[0], .pointer = null },
        .{ .raw = err_ptr.err_floor - 7, .kind = .pointer, .value = null, .pointer = err_ptr.err_floor - 7 },
        .{ .raw = err_ptr.err_floor - 6, .kind = .value, .value = values[1], .pointer = null },
        .{ .raw = err_ptr.err_floor - 5, .kind = .pointer, .value = null, .pointer = err_ptr.err_floor - 5 },
        .{ .raw = err_ptr.err_floor - 4, .kind = .value, .value = values[2], .pointer = null },
        .{ .raw = err_ptr.err_floor - 3, .kind = .pointer, .value = null, .pointer = err_ptr.err_floor - 3 },
        .{ .raw = err_ptr.err_floor - 2, .kind = .value, .value = values[3], .pointer = null },
        .{ .raw = err_ptr.err_floor - 1, .kind = .pointer, .value = null, .pointer = err_ptr.err_floor - 1 },
    };

    inline for (slots, expected) |slot, want| {
        try std.testing.expectEqual(want.raw, slot.rawValue());
        try std.testing.expectEqual(want.kind, slot.kind());
        try std.testing.expectEqual(want.value, slot.value());
        try std.testing.expectEqual(want.pointer, slot.pointerValue());
        try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
        try std.testing.expect(slot.rawValue() < err_ptr.err_floor);
    }
}

test "high constructor interleave keeps tagged-entry ownership on odd raws only" {
    inline for (0..4) |index| {
        const value_input = xa_value.safe_inline_limit - (3 - index);
        const value_slot = try xarray_slot_view.fromValue(value_input);
        const pointer_raw = value_slot.rawValue() + 1;
        const pointer_slot = xarray_slot_view.fromPointer(pointer_raw);

        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(value_slot.rawValue()));
        try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_slot.rawValue()));
        try std.testing.expect(value_slot.isValue());
        try std.testing.expect(!value_slot.isPointer());
        try std.testing.expect(pointer_slot.isPointer());
        try std.testing.expect(!pointer_slot.isValue());
        try std.testing.expect(!pointer_slot.isErr());
    }
}

test "high constructor interleave hands off to the err lane only at err floor" {
    const highest_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const highest_pointer = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try std.testing.expectEqual(err_ptr.err_floor - 2, highest_value.rawValue());
    try std.testing.expectEqual(err_ptr.err_floor - 1, highest_pointer.rawValue());
    try std.testing.expectEqual(err_ptr.err_floor, err_slot.rawValue());

    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), highest_value.value());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), highest_pointer.pointerValue());
    try std.testing.expectEqual(@as(?isize, -4095), err_slot.errorCode());

    try std.testing.expectEqual(@as(usize, 1), highest_pointer.rawValue() - highest_value.rawValue());
    try std.testing.expectEqual(@as(usize, 1), err_slot.rawValue() - highest_pointer.rawValue());
    try std.testing.expect(!xarray_slot_view.fromRaw(highest_pointer.rawValue()).isErr());
    try std.testing.expect(xarray_slot_view.fromRaw(err_slot.rawValue()).isErr());
}
