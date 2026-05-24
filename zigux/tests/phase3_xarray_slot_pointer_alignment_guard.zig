const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "aligned pointer candidates below the seam stay pointer-like while adjacent odd raws stay xa_values" {
    const aligned_raws = [_]usize{ 0x1000, 0x1002, err_ptr.err_floor - 3 };

    for (aligned_raws) |aligned_raw| {
        const tagged_neighbor_raw = aligned_raw + 1;
        const pointer_slot = xarray_slot_view.fromRaw(aligned_raw);
        const value_slot = xarray_slot_view.fromRaw(tagged_neighbor_raw);

        try testing.expect(!err_ptr.isErrValue(aligned_raw));
        try testing.expect(!xa_value.isValue(aligned_raw));
        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
        try testing.expect(pointer_slot.isPointer());
        try testing.expectEqual(@as(?usize, aligned_raw), pointer_slot.pointerValue());
        try testing.expectEqual(@as(?usize, null), pointer_slot.value());
        try testing.expectEqual(@as(?isize, null), pointer_slot.errorCode());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(aligned_raw));

        try testing.expect(!err_ptr.isErrValue(tagged_neighbor_raw));
        try testing.expect(xa_value.isValue(tagged_neighbor_raw));
        try testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
        try testing.expect(value_slot.isValue());
        try testing.expectEqual(@as(?usize, tagged_neighbor_raw >> 1), value_slot.value());
        try testing.expectEqual(@as(?usize, null), value_slot.pointerValue());
        try testing.expectEqual(@as(?isize, null), value_slot.errorCode());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(tagged_neighbor_raw));
    }
}

test "highest aligned pointer gap and highest inline value stay on opposite sides of the odd tag bit" {
    const highest_inline_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;

    const highest_inline_slot = xarray_slot_view.fromRaw(highest_inline_raw);
    const pointer_gap_slot = xarray_slot_view.fromRaw(pointer_gap_raw);

    try testing.expectEqual(err_ptr.err_floor - 2, highest_inline_raw);
    try testing.expectEqual(err_ptr.err_floor - 1, pointer_gap_raw);
    try testing.expectEqual(@as(usize, 1), highest_inline_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), pointer_gap_raw & xa_value.value_tag_mask);

    try testing.expectEqual(xarray_slot_view.SlotKind.value, highest_inline_slot.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap_slot.kind());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), highest_inline_slot.value());
    try testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap_slot.pointerValue());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(highest_inline_raw));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));
}

test "pointer gap below err floor borders the err lane instead of another xa_value" {
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const err_floor_slot = xarray_slot_view.fromRaw(err_ptr.err_floor);
    const pointer_gap_slot = xarray_slot_view.fromRaw(pointer_gap_raw);

    try testing.expectEqual(pointer_gap_raw + 1, err_ptr.err_floor);
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap_slot.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, err_floor_slot.kind());
    try testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap_slot.pointerValue());
    try testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());
    try testing.expect(!xa_value.isValue(err_ptr.err_floor));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(err_ptr.err_floor));
}

test "pointer constructor lane matches raw classification for aligned candidates below err floor" {
    const aligned_candidates = [_]usize{ 0x2000, 0x2002, err_ptr.err_floor - 1 };

    for (aligned_candidates) |raw| {
        const constructed_slot = xarray_slot_view.fromPointer(raw);
        const classified_slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, constructed_slot.kind());
        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, classified_slot.kind());
        try testing.expectEqual(@as(?usize, raw), constructed_slot.pointerValue());
        try testing.expectEqual(@as(?usize, raw), classified_slot.pointerValue());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
    }
}
