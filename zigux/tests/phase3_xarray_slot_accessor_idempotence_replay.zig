const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectStableAccessors(
    raw: usize,
    expected_kind: xarray_slot_view.SlotKind,
    expected_value: ?usize,
    expected_error: ?isize,
    expected_pointer: ?usize,
) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectEqual(raw, slot.rawValue());
    try testing.expectEqual(expected_kind, slot.kind());
    try testing.expectEqual(expected_kind, slot.kind());
    try testing.expectEqual(expected_value, slot.value());
    try testing.expectEqual(expected_value, slot.value());
    try testing.expectEqual(expected_error, slot.errorCode());
    try testing.expectEqual(expected_error, slot.errorCode());
    try testing.expectEqual(expected_pointer, slot.pointerValue());
    try testing.expectEqual(expected_pointer, slot.pointerValue());
    try testing.expectEqual(raw, slot.rawValue());
}

test "xarray slot accessors are stable across raw lane representatives" {
    try expectStableAccessors(0, .null, null, null, null);
    try expectStableAccessors(try xa_value.makeValue(0), .value, 0, null, null);
    try expectStableAccessors(try xa_value.makeValue(29), .value, 29, null, null);
    try expectStableAccessors(0x1000, .pointer, null, null, 0x1000);
    try expectStableAccessors(err_ptr.err_floor - 1, .pointer, null, null, err_ptr.err_floor - 1);
    try expectStableAccessors(err_ptr.err_floor, .err, null, -4095, null);
    try expectStableAccessors(err_ptr.fromErrorCode(-22), .err, null, -22, null);
    try expectStableAccessors(err_ptr.fromErrorCode(-1), .err, null, -1, null);
}

test "constructor-created slots keep repeated decoder calls closed outside their lane" {
    const slots = [_]xarray_slot_view.SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 3),
        xarray_slot_view.fromErrorCode(-5),
    };
    const kinds = [_]xarray_slot_view.SlotKind{ .null, .value, .pointer, .err };

    for (slots, kinds) |slot, kind| {
        try testing.expectEqual(kind, slot.kind());
        try testing.expectEqual(kind, slot.kind());
        switch (kind) {
            .null => {
                try testing.expectEqual(@as(?usize, null), slot.value());
                try testing.expectEqual(@as(?isize, null), slot.errorCode());
                try testing.expectEqual(@as(?usize, null), slot.pointerValue());
            },
            .value => {
                try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), slot.value());
                try testing.expectEqual(@as(?isize, null), slot.errorCode());
                try testing.expectEqual(@as(?usize, null), slot.pointerValue());
            },
            .pointer => {
                try testing.expectEqual(@as(?usize, null), slot.value());
                try testing.expectEqual(@as(?isize, null), slot.errorCode());
                try testing.expectEqual(@as(?usize, err_ptr.err_floor - 3), slot.pointerValue());
            },
            .err => {
                try testing.expectEqual(@as(?usize, null), slot.value());
                try testing.expectEqual(@as(?isize, -5), slot.errorCode());
                try testing.expectEqual(@as(?usize, null), slot.pointerValue());
            },
        }
    }
}

test "tagged-internal predicate remains stable beside repeated payload access" {
    const raws = [_]usize{
        0,
        try xa_value.makeValue(1),
        err_ptr.err_floor - 1,
        err_ptr.err_floor,
        err_ptr.fromErrorCode(-1),
    };

    for (raws) |raw| {
        const before = xarray_slot_view.isTaggedInternalEntry(raw);
        const slot = xarray_slot_view.fromRaw(raw);
        _ = slot.value();
        _ = slot.errorCode();
        _ = slot.pointerValue();
        try testing.expectEqual(before, xarray_slot_view.isTaggedInternalEntry(raw));
        try testing.expectEqual(raw, slot.rawValue());
    }
}
