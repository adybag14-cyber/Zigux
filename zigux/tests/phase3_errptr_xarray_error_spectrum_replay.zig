const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectErrCase(code: isize) !void {
    const raw = err_ptr.fromErrorCode(code);
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expect(!err_ptr.isOkValue(raw));
    try testing.expect(!xa_value.isValue(raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try testing.expectEqual(raw, slot.rawValue());
    try testing.expectEqual(@as(?isize, code), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "error spectrum replay keeps representative err_ptr codes in the err lane" {
    const codes = [_]isize{ -1, -2, -5, -12, -22, -4095 };

    for (codes) |code| {
        try expectErrCase(code);
    }
}

test "error spectrum replay keeps odd and even err codes out of the xa_value decoder" {
    const odd_raw = err_ptr.fromErrorCode(-1);
    const even_raw = err_ptr.fromErrorCode(-2);
    const odd_lower_raw = err_ptr.fromErrorCode(-3);
    const even_lower_raw = err_ptr.fromErrorCode(-4);

    try testing.expectEqual(@as(usize, 1), odd_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), even_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 1), odd_lower_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), even_lower_raw & xa_value.value_tag_mask);

    try expectErrCase(-1);
    try expectErrCase(-2);
    try expectErrCase(-3);
    try expectErrCase(-4);
}

test "error spectrum replay keeps the err band contiguous above the pointer gap" {
    const top_raw = err_ptr.fromErrorCode(-1);
    const next_raw = err_ptr.fromErrorCode(-2);
    const lower_raw = err_ptr.fromErrorCode(-3);
    const floor_raw = err_ptr.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const pointer_gap_slot = xarray_slot_view.fromRaw(pointer_gap_raw);

    try testing.expectEqual(err_ptr.err_floor, floor_raw);
    try testing.expect(top_raw > next_raw);
    try testing.expect(next_raw > lower_raw);
    try testing.expect(lower_raw > floor_raw);
    try testing.expectEqual(@as(usize, 1), top_raw - next_raw);
    try testing.expectEqual(@as(usize, 1), next_raw - lower_raw);
    try testing.expectEqual(err_ptr.max_errno - 1, top_raw - floor_raw);

    try testing.expect(err_ptr.isOkValue(pointer_gap_raw));
    try testing.expect(!err_ptr.isErrValue(pointer_gap_raw));
    try testing.expect(!xa_value.isValue(pointer_gap_raw));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap_raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap_slot.kind());
    try testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap_slot.pointerValue());
}
