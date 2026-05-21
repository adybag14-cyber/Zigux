const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectInteriorTaggedErrTriplet(center_code: isize) !void {
    const lower_code = center_code - 1;
    const upper_code = center_code + 1;

    const lower_raw = err_ptr.fromErrorCode(lower_code);
    const center_raw = err_ptr.fromErrorCode(center_code);
    const upper_raw = err_ptr.fromErrorCode(upper_code);

    const lower_slot = xarray_slot_view.fromRaw(lower_raw);
    const center_slot = xarray_slot_view.fromRaw(center_raw);
    const upper_slot = xarray_slot_view.fromRaw(upper_raw);
    const rejected_payload = center_raw >> 1;

    try testing.expect((lower_raw & xa_value.value_tag_mask) == 0);
    try testing.expect((center_raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    try testing.expect((upper_raw & xa_value.value_tag_mask) == 0);

    try testing.expectEqual(lower_raw + 1, center_raw);
    try testing.expectEqual(center_raw + 1, upper_raw);
    try testing.expectEqual(lower_raw + 2, upper_raw);

    try testing.expect(lower_slot.isErr());
    try testing.expect(center_slot.isErr());
    try testing.expect(upper_slot.isErr());

    try testing.expect(!lower_slot.isValue());
    try testing.expect(!center_slot.isValue());
    try testing.expect(!upper_slot.isValue());

    try testing.expect(!lower_slot.isPointer());
    try testing.expect(!center_slot.isPointer());
    try testing.expect(!upper_slot.isPointer());

    try testing.expectEqual(@as(?isize, lower_code), lower_slot.errorCode());
    try testing.expectEqual(@as(?isize, center_code), center_slot.errorCode());
    try testing.expectEqual(@as(?isize, upper_code), upper_slot.errorCode());

    try testing.expectEqual(@as(?usize, null), lower_slot.value());
    try testing.expectEqual(@as(?usize, null), center_slot.value());
    try testing.expectEqual(@as(?usize, null), upper_slot.value());

    try testing.expect(xarray_slot_view.isTaggedInternalEntry(lower_raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(center_raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(upper_raw));

    try testing.expectEqual(lower_raw, xarray_slot_view.fromErrorCode(lower_code).rawValue());
    try testing.expectEqual(center_raw, xarray_slot_view.fromErrorCode(center_code).rawValue());
    try testing.expectEqual(upper_raw, xarray_slot_view.fromErrorCode(upper_code).rawValue());

    try testing.expectEqual(center_raw, (rejected_payload << 1) | xa_value.value_tag_mask);
    try testing.expect(!xa_value.canRepresent(rejected_payload));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_payload));
}

test "interior tagged err_ptr raws stay sandwiched between direct even err neighbors" {
    const center_codes = [_]isize{ -4093, -2049, -3 };

    for (center_codes) |center_code| {
        try expectInteriorTaggedErrTriplet(center_code);
    }
}

test "top interior tagged err raw keeps both even neighbors in the err lane" {
    try expectInteriorTaggedErrTriplet(-3);
}
