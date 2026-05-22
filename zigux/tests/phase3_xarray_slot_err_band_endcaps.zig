const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xarray_slot_view = @import("xarray_slot_view");

test "err band endcaps stay in the err lane across odd and even raws" {
    const raws = [_]usize{
        err_ptr.err_floor,
        err_ptr.err_floor + 1,
        err_ptr.fromErrorCode(-2),
        err_ptr.fromErrorCode(-1),
    };
    const expected_errors = [_]isize{ -4095, -4094, -2, -1 };

    try testing.expect((raws[0] & 1) == 1);
    try testing.expect((raws[1] & 1) == 0);
    try testing.expect((raws[2] & 1) == 0);
    try testing.expect((raws[3] & 1) == 1);

    for (raws, expected_errors) |raw, expected_error| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(raw, slot.rawValue());
        try testing.expectEqual(@as(?isize, expected_error), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "floor gap and err top keep the lane split closed at both ends" {
    const floor_gap_raw = err_ptr.err_floor - 1;
    const floor_slot = xarray_slot_view.fromRaw(err_ptr.err_floor);
    const floor_next_slot = xarray_slot_view.fromRaw(err_ptr.err_floor + 1);
    const top_prev_slot = xarray_slot_view.fromErrorCode(-2);
    const top_slot = xarray_slot_view.fromErrorCode(-1);
    const floor_gap_slot = xarray_slot_view.fromRaw(floor_gap_raw);

    try testing.expectEqual(err_ptr.err_floor, floor_gap_raw + 1);
    try testing.expectEqual(top_prev_slot.rawValue() + 1, top_slot.rawValue());
    try testing.expectEqual(std.math.maxInt(usize) - 1, top_prev_slot.rawValue());
    try testing.expectEqual(std.math.maxInt(usize), top_slot.rawValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, floor_gap_slot.kind());
    try testing.expect(floor_gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, floor_gap_raw), floor_gap_slot.pointerValue());
    try testing.expectEqual(@as(?isize, null), floor_gap_slot.errorCode());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(floor_gap_raw));

    try testing.expectEqual(@as(?isize, -4095), floor_slot.errorCode());
    try testing.expectEqual(@as(?isize, -4094), floor_next_slot.errorCode());
    try testing.expectEqual(@as(?isize, -2), top_prev_slot.errorCode());
    try testing.expectEqual(@as(?isize, -1), top_slot.errorCode());
}
