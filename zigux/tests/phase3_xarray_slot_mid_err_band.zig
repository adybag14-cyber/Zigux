const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn rawForUncheckedValue(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

test "interior err_ptr window stays in the err lane for contiguous codes" {
    const codes = [_]isize{ -2050, -2049, -2048, -2047 };

    inline for (codes) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "tagged interior err raws still reject xa_value decoding" {
    const tagged_raws = [_]usize{
        err_ptr.err_floor + 2044,
        err_ptr.err_floor + 2046,
    };

    inline for (tagged_raws) |raw| {
        const overlapping_value = (raw - xa_value.value_tag_mask) >> 1;
        const slot = xarray_slot_view.fromRaw(rawForUncheckedValue(overlapping_value));

        try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expectEqual(raw, rawForUncheckedValue(overlapping_value));
        try testing.expect(!xa_value.canRepresent(overlapping_value));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, err_ptr.toErrorCode(raw)), slot.errorCode());
    }
}

test "raw and constructor err-slot paths agree in the middle of the band" {
    const codes = [_]isize{ -2050, -2048, -2046, -2044 };

    inline for (codes) |code| {
        const raw_slot = xarray_slot_view.fromRaw(err_ptr.fromErrorCode(code));
        const constructed_slot = xarray_slot_view.fromErrorCode(code);

        try testing.expectEqual(xarray_slot_view.SlotKind.err, raw_slot.kind());
        try testing.expectEqual(raw_slot.kind(), constructed_slot.kind());
        try testing.expectEqual(raw_slot.rawValue(), constructed_slot.rawValue());
        try testing.expectEqual(raw_slot.errorCode(), constructed_slot.errorCode());
    }
}
