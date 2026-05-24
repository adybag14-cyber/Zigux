const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn rejectedRaw(offset: usize) usize {
    const rejected_value = xa_value.safe_inline_limit + 1 + offset;
    return (rejected_value << 1) | xa_value.value_tag_mask;
}

test "rejected tagged window endpoints stay in the err lane" {
    const first_raw = rejectedRaw(0);
    const second_raw = rejectedRaw(1);
    const last_raw = rejectedRaw((err_ptr.max_errno - 1) / 2);

    const first_slot = xarray_slot_view.fromRaw(first_raw);
    const second_slot = xarray_slot_view.fromRaw(second_raw);
    const last_slot = xarray_slot_view.fromRaw(last_raw);

    try testing.expectEqual(err_ptr.err_floor, first_raw);
    try testing.expectEqual(err_ptr.err_floor + 2, second_raw);
    try testing.expectEqual(err_ptr.fromErrorCode(-1), last_raw);

    try testing.expectEqual(xarray_slot_view.SlotKind.err, first_slot.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, second_slot.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, last_slot.kind());

    try testing.expectEqual(@as(?isize, -4095), first_slot.errorCode());
    try testing.expectEqual(@as(?isize, -4093), second_slot.errorCode());
    try testing.expectEqual(@as(?isize, -1), last_slot.errorCode());

    try testing.expectEqual(@as(?usize, null), first_slot.value());
    try testing.expectEqual(@as(?usize, null), second_slot.value());
    try testing.expectEqual(@as(?usize, null), last_slot.value());
    try testing.expectEqual(@as(?usize, null), first_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), second_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), last_slot.pointerValue());
}

test "rejected tagged raws skip the first in-band even neighbor but both stay err" {
    const first_rejected_raw = rejectedRaw(0);
    const first_even_neighbor = first_rejected_raw + 1;
    const second_rejected_raw = rejectedRaw(1);

    const even_slot = xarray_slot_view.fromRaw(first_even_neighbor);
    const second_slot = xarray_slot_view.fromRaw(second_rejected_raw);

    try testing.expectEqual(err_ptr.err_floor + 1, first_even_neighbor);
    try testing.expectEqual(err_ptr.err_floor + 2, second_rejected_raw);

    try testing.expectEqual(@as(usize, 0), first_even_neighbor & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 1), second_rejected_raw & xa_value.value_tag_mask);

    try testing.expect(!xa_value.isValue(first_even_neighbor));
    try testing.expect(!xa_value.isValue(second_rejected_raw));
    try testing.expect(err_ptr.isErrValue(first_even_neighbor));
    try testing.expect(err_ptr.isErrValue(second_rejected_raw));

    try testing.expectEqual(xarray_slot_view.SlotKind.err, even_slot.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.err, second_slot.kind());
    try testing.expectEqual(@as(?isize, -4094), even_slot.errorCode());
    try testing.expectEqual(@as(?isize, -4093), second_slot.errorCode());
}

test "entire err band stays err while rejected xa_value aliases occupy exactly the odd raws" {
    var odd_err_count: usize = 0;
    var even_err_count: usize = 0;

    var code: isize = -@as(isize, @intCast(err_ptr.max_errno));
    while (code <= -1) : (code += 1) {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(slot.isErr());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(!xa_value.isValue(raw));

        if ((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask) {
            odd_err_count += 1;
        } else {
            even_err_count += 1;
        }
    }

    try testing.expectEqual(@as(usize, 2048), odd_err_count);
    try testing.expectEqual(@as(usize, 2047), even_err_count);
}

test "raw below err floor stays pointer-like outside the rejected tagged window" {
    const pointer_gap_raw = err_ptr.err_floor - 1;
    const first_rejected_raw = rejectedRaw(0);
    const pointer_gap_slot = xarray_slot_view.fromRaw(pointer_gap_raw);

    try testing.expectEqual(err_ptr.err_floor, first_rejected_raw);
    try testing.expect(pointer_gap_raw + 1 == first_rejected_raw);

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_gap_slot.kind());
    try testing.expect(pointer_gap_slot.isPointer());
    try testing.expectEqual(@as(?usize, pointer_gap_raw), pointer_gap_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), pointer_gap_slot.value());
    try testing.expectEqual(@as(?isize, null), pointer_gap_slot.errorCode());
    try testing.expect(!err_ptr.isErrValue(pointer_gap_raw));
    try testing.expect(!xa_value.isValue(pointer_gap_raw));
}
