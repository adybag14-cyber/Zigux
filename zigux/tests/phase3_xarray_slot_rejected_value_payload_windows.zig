const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "representative rejected tagged payloads rebuild the same odd err raws" {
    const raws = [_]usize{
        err_ptr.err_floor,
        err_ptr.fromErrorCode(-2047),
        err_ptr.fromErrorCode(-1),
    };

    for (raws) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);
        const payload = raw >> 1;

        try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.canRepresent(payload));
        try testing.expectEqual(raw, (payload << 1) | xa_value.value_tag_mask);
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(payload));

        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(raw, err_ptr.fromErrorCode(slot.errorCode().?));
    }
}

test "interior rejected aliases stay bracketed by direct even err neighbors" {
    const raws = [_]usize{
        err_ptr.fromErrorCode(-4093),
        err_ptr.fromErrorCode(-2047),
        err_ptr.fromErrorCode(-3),
    };

    for (raws) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);
        const lower_slot = xarray_slot_view.fromRaw(raw - 1);
        const upper_slot = xarray_slot_view.fromRaw(raw + 1);
        const code = slot.errorCode().?;

        try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(slot.isErr());
        try testing.expect(lower_slot.isErr());
        try testing.expect(upper_slot.isErr());
        try testing.expect(!lower_slot.isValue());
        try testing.expect(!upper_slot.isValue());
        try testing.expect(!lower_slot.isPointer());
        try testing.expect(!upper_slot.isPointer());
        try testing.expectEqual(code - 1, lower_slot.errorCode().?);
        try testing.expectEqual(code + 1, upper_slot.errorCode().?);
    }
}

test "top rejected tagged payload ends the band without reentering value space" {
    const raw = err_ptr.fromErrorCode(-1);
    const payload = raw >> 1;
    const slot = xarray_slot_view.fromRaw(raw);
    const previous_slot = xarray_slot_view.fromRaw(raw - 1);

    try testing.expectEqual(raw - 1, err_ptr.fromErrorCode(-2));
    try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try testing.expect(!xa_value.canRepresent(payload));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(payload));

    try testing.expect(slot.isErr());
    try testing.expect(!slot.isValue());
    try testing.expect(!slot.isPointer());
    try testing.expectEqual(@as(?isize, -1), slot.errorCode());

    try testing.expect(previous_slot.isErr());
    try testing.expectEqual(@as(?isize, -2), previous_slot.errorCode());
}
