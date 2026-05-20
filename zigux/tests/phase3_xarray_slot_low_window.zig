const std = @import("std");
const testing = std.testing;

const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "low raw alternation keeps null value and pointer lanes distinct" {
    const raws = [_]usize{ 0, 1, 2, 3, 4, 5, 6 };
    const expected_kinds = [_]xarray_slot_view.SlotKind{
        .null,
        .value,
        .pointer,
        .value,
        .pointer,
        .value,
        .pointer,
    };

    inline for (raws, expected_kinds) |raw, expected_kind| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(expected_kind, slot.kind());
        try testing.expectEqual(raw, slot.rawValue());
    }
}

test "low odd raws decode as consecutive inline xa_values" {
    const values = [_]usize{ 0, 1, 2 };
    const raws = [_]usize{ 1, 3, 5 };

    inline for (values, raws) |value, raw| {
        const raw_slot = xarray_slot_view.fromRaw(raw);
        const constructed_slot = try xarray_slot_view.fromValue(value);

        try testing.expectEqual(raw, try xa_value.makeValue(value));
        try testing.expect(raw_slot.isValue());
        try testing.expectEqual(@as(?usize, value), raw_slot.value());
        try testing.expectEqual(@as(?usize, null), raw_slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try testing.expectEqual(raw_slot.rawValue(), constructed_slot.rawValue());
    }
}

test "low even raws stay pointer-like with tagged decoders closed" {
    const raws = [_]usize{ 2, 4, 6 };

    inline for (raws) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isErr());
        try testing.expect(slot.isPointer());
        try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
    }
}
