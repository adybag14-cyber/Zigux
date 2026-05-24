const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "full err_ptr band stays monotonic and always classifies as err" {
    var code = -@as(isize, @intCast(err_ptr.max_errno));
    var expected_raw = err_ptr.err_floor;
    var seen: usize = 0;

    while (true) {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(expected_raw, raw);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!err_ptr.isOkValue(raw));
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try testing.expect(!xa_value.isValue(raw));

        seen += 1;
        if (code == -1) {
            break;
        }
        code += 1;
        expected_raw += 1;
    }

    try testing.expectEqual(err_ptr.max_errno, seen);
    try testing.expectEqual(@as(usize, std.math.maxInt(usize)), expected_raw);
}

test "err_ptr band keeps the floor and top edges exact" {
    const floor_slot = xarray_slot_view.fromRaw(err_ptr.err_floor);
    const top_raw = err_ptr.fromErrorCode(-1);
    const top_slot = xarray_slot_view.fromRaw(top_raw);

    try testing.expectEqual(err_ptr.err_floor - 2, try xa_value.makeValue(xa_value.safe_inline_limit));
    try testing.expectEqual(err_ptr.err_floor, err_ptr.fromErrorCode(-4095));
    try testing.expectEqual(@as(?isize, -4095), floor_slot.errorCode());
    try testing.expectEqual(@as(?isize, -1), top_slot.errorCode());
    try testing.expectEqual(std.math.maxInt(usize), top_raw);
    try testing.expectEqual(@as(usize, err_ptr.max_errno - 1), top_raw - err_ptr.err_floor);
}

test "err_ptr band preserves odd-even coverage without reopening xa_value decoding" {
    var code = -@as(isize, @intCast(err_ptr.max_errno));
    var odd_low_bit_count: usize = 0;
    var even_low_bit_count: usize = 0;

    while (true) {
        const raw = err_ptr.fromErrorCode(code);
        if ((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask) {
            odd_low_bit_count += 1;
            try testing.expect(!xa_value.isValue(raw));
        } else {
            even_low_bit_count += 1;
        }

        if (code == -1) {
            break;
        }
        code += 1;
    }

    try testing.expectEqual(@as(usize, 2048), odd_low_bit_count);
    try testing.expectEqual(@as(usize, 2047), even_low_bit_count);
    try testing.expectEqual(err_ptr.max_errno, odd_low_bit_count + even_low_bit_count);
}
