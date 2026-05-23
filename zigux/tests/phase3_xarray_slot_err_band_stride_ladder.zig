const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "consecutive interior err raws stay a continuous xarray error ladder" {
    const codes = [_]isize{ -2048, -2047, -2046, -2045 };

    var raws: [codes.len]usize = undefined;
    for (codes, 0..) |code, index| {
        raws[index] = err_ptr.fromErrorCode(code);
    }

    for (raws, 0..) |raw, index| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(slot.isErr());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expectEqual(raw, slot.rawValue());
        try testing.expectEqual(@as(?isize, codes[index]), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));

        if (index > 0) {
            try testing.expectEqual(raws[index - 1] + 1, raw);
            try testing.expectEqual(codes[index - 1] + 1, codes[index]);
        }
    }

    try testing.expect((raws[0] & xa_value.value_tag_mask) == 0);
    try testing.expect((raws[1] & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try testing.expect((raws[2] & xa_value.value_tag_mask) == 0);
    try testing.expect((raws[3] & xa_value.value_tag_mask) == xa_value.value_tag_mask);
}

test "odd interior err raws masquerade as rejected xa payloads but stay in err lane" {
    const odd_codes = [_]isize{ -2047, -511, -33 };

    for (odd_codes) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const overlapping_value = raw >> 1;
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expectEqual(raw, (overlapping_value << 1) | xa_value.value_tag_mask);
        try testing.expect(!xa_value.canRepresent(overlapping_value));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
        try testing.expect(slot.isErr());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(raw, xarray_slot_view.fromErrorCode(code).rawValue());
    }
}
