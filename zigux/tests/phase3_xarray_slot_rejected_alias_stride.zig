const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const rejected_alias_count: usize = (err_ptr.max_errno + 1) / 2;

fn rejectedRaw(index: usize) usize {
    const rejected_value = xa_value.safe_inline_limit + 1 + index;
    return (rejected_value << 1) | xa_value.value_tag_mask;
}

fn rejectedErrorCode(index: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(index * 2));
}

test "rejected tagged raws match the odd err_ptr alias ladder exactly" {
    var index: usize = 0;
    while (index < rejected_alias_count) : (index += 1) {
        const raw = rejectedRaw(index);
        const code = rejectedErrorCode(index);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(err_ptr.fromErrorCode(code), raw);
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
    }
}

test "rejected alias ladder endpoints and stride stay exact across the full band" {
    const first_raw = rejectedRaw(0);
    const second_raw = rejectedRaw(1);
    const last_raw = rejectedRaw(rejected_alias_count - 1);

    try testing.expectEqual(err_ptr.err_floor, first_raw);
    try testing.expectEqual(err_ptr.err_floor + 2, second_raw);
    try testing.expectEqual(err_ptr.fromErrorCode(-1), last_raw);
    try testing.expectEqual(@as(usize, 2), second_raw - first_raw);
    try testing.expectEqual(@as(usize, (rejected_alias_count - 1) * 2), last_raw - first_raw);
}

test "even err raws stay between rejected aliases without reopening xa_value decoding" {
    var index: usize = 0;
    while (index + 1 < rejected_alias_count) : (index += 1) {
        const lower_rejected_raw = rejectedRaw(index);
        const even_err_raw = lower_rejected_raw + 1;
        const upper_rejected_raw = rejectedRaw(index + 1);
        const even_slot = xarray_slot_view.fromRaw(even_err_raw);
        const lower_code = rejectedErrorCode(index);

        try testing.expectEqual(@as(usize, 0), even_err_raw & xa_value.value_tag_mask);
        try testing.expectEqual(upper_rejected_raw, even_err_raw + 1);
        try testing.expectEqual(err_ptr.fromErrorCode(lower_code + 1), even_err_raw);
        try testing.expect(err_ptr.isErrValue(even_err_raw));
        try testing.expect(!xa_value.isValue(even_err_raw));
        try testing.expectEqual(xarray_slot_view.SlotKind.err, even_slot.kind());
        try testing.expectEqual(@as(?isize, lower_code + 1), even_slot.errorCode());
        try testing.expectEqual(@as(?usize, null), even_slot.value());
        try testing.expectEqual(@as(?usize, null), even_slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(even_err_raw));
    }
}
