const std = @import("std");
const err_ptr = @import("err_ptr");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

test "low public constructors interleave null value and pointer raws exactly" {
    const slots = [_]xarray_slot_view.SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(0),
        xarray_slot_view.fromPointer(2),
        try xarray_slot_view.fromValue(1),
        xarray_slot_view.fromPointer(4),
        try xarray_slot_view.fromValue(2),
        xarray_slot_view.fromPointer(6),
        try xarray_slot_view.fromValue(3),
        xarray_slot_view.fromPointer(8),
    };
    const expected = [_]struct {
        raw: usize,
        kind: SlotKind,
        value: ?usize,
        pointer: ?usize,
    }{
        .{ .raw = 0, .kind = .null, .value = null, .pointer = null },
        .{ .raw = 1, .kind = .value, .value = 0, .pointer = null },
        .{ .raw = 2, .kind = .pointer, .value = null, .pointer = 2 },
        .{ .raw = 3, .kind = .value, .value = 1, .pointer = null },
        .{ .raw = 4, .kind = .pointer, .value = null, .pointer = 4 },
        .{ .raw = 5, .kind = .value, .value = 2, .pointer = null },
        .{ .raw = 6, .kind = .pointer, .value = null, .pointer = 6 },
        .{ .raw = 7, .kind = .value, .value = 3, .pointer = null },
        .{ .raw = 8, .kind = .pointer, .value = null, .pointer = 8 },
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

test "low constructor interleave keeps tagged-entry ownership on odd raws only" {
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(xarray_slot_view.nullSlot().rawValue()));

    inline for (0..4) |value| {
        const value_slot = try xarray_slot_view.fromValue(value);
        const pointer_raw = @as(usize, (value + 1) * 2);
        const pointer_slot = xarray_slot_view.fromPointer(pointer_raw);

        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(value_slot.rawValue()));
        try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_slot.rawValue()));
        try std.testing.expect(value_slot.isValue());
        try std.testing.expect(!pointer_slot.isValue());
        try std.testing.expect(pointer_slot.isPointer());
        try std.testing.expect(!pointer_slot.isErr());
    }
}

test "low constructor interleave stays below the err_ptr floor with room to spare" {
    const highest_value = try xarray_slot_view.fromValue(3);
    const highest_pointer = xarray_slot_view.fromPointer(8);
    const next_pointer_gap = err_ptr.err_floor - highest_pointer.rawValue();

    try std.testing.expectEqual(@as(usize, 7), highest_value.rawValue());
    try std.testing.expectEqual(@as(usize, 8), highest_pointer.rawValue());
    try std.testing.expect(highest_value.rawValue() < highest_pointer.rawValue());
    try std.testing.expect(highest_pointer.rawValue() < err_ptr.err_floor);
    try std.testing.expect(next_pointer_gap > 0);
    try std.testing.expect(!xarray_slot_view.fromRaw(highest_pointer.rawValue()).isErr());
    try std.testing.expect(xarray_slot_view.fromErrorCode(-1).isErr());
}
