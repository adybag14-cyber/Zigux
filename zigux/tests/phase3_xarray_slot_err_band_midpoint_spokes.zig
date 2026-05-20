const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_top = err_ptr.fromErrorCode(-1);
const err_band_span = err_ptr.max_errno - 1;
const midpoint_offset = err_band_span / 2;
const midpoint_code: isize = -@as(isize, @intCast((err_ptr.max_errno + 1) / 2));
const midpoint_raw = err_ptr.err_floor + midpoint_offset;

test "err band has a unique direct-error midpoint between the mirrored endpoints" {
    const midpoint = xarray_slot_view.fromRaw(midpoint_raw);

    try testing.expectEqual(err_band_span, err_top - err_ptr.err_floor);
    try testing.expectEqual(midpoint_raw, err_top - midpoint_offset);
    try testing.expectEqual(midpoint_offset, midpoint_raw - err_ptr.err_floor);
    try testing.expectEqual(midpoint_offset, err_top - midpoint_raw);

    try testing.expect(!midpoint.isNull());
    try testing.expect(!midpoint.isValue());
    try testing.expect(midpoint.isErr());
    try testing.expect(!midpoint.isPointer());
    try testing.expectEqual(@as(?isize, midpoint_code), midpoint.errorCode());
    try testing.expectEqual(@as(usize, 0), midpoint_raw & xa_value.value_tag_mask);
    try testing.expect(!xa_value.isValue(midpoint_raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(midpoint_raw));
}

test "midpoint neighbors stay rejected aliases on both sides of the band center" {
    const lower_raw = midpoint_raw - 1;
    const upper_raw = midpoint_raw + 1;
    const raws = [_]usize{ lower_raw, upper_raw };
    const expected_codes = [_]isize{ midpoint_code - 1, midpoint_code + 1 };

    for (raws, expected_codes) |raw, expected_code| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(!xa_value.canRepresent(raw >> 1));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try testing.expectEqual(raw, xarray_slot_view.fromErrorCode(expected_code).rawValue());
    }
}

test "equal midpoint spokes preserve code symmetry and switch family by distance parity" {
    const deltas = [_]usize{ 0, 1, 2, 17, 255, 1023, 2047 };

    for (deltas) |delta| {
        const low_raw = midpoint_raw - delta;
        const high_raw = midpoint_raw + delta;
        const low_slot = xarray_slot_view.fromRaw(low_raw);
        const high_slot = xarray_slot_view.fromRaw(high_raw);

        try testing.expect(low_slot.isErr());
        try testing.expect(high_slot.isErr());
        try testing.expectEqual(delta, midpoint_raw - low_raw);
        try testing.expectEqual(delta, high_raw - midpoint_raw);

        const low_code = low_slot.errorCode().?;
        const high_code = high_slot.errorCode().?;

        try testing.expectEqual(midpoint_code - @as(isize, @intCast(delta)), low_code);
        try testing.expectEqual(midpoint_code + @as(isize, @intCast(delta)), high_code);
        try testing.expectEqual(midpoint_code * 2, low_code + high_code);

        if ((delta & 1) == 0) {
            try testing.expectEqual(@as(usize, 0), low_raw & xa_value.value_tag_mask);
            try testing.expectEqual(@as(usize, 0), high_raw & xa_value.value_tag_mask);
        } else {
            try testing.expectEqual(@as(usize, 1), low_raw & xa_value.value_tag_mask);
            try testing.expectEqual(@as(usize, 1), high_raw & xa_value.value_tag_mask);
            try testing.expect(!xa_value.canRepresent(low_raw >> 1));
            try testing.expect(!xa_value.canRepresent(high_raw >> 1));
        }

        try testing.expect(!xa_value.isValue(low_raw));
        try testing.expect(!xa_value.isValue(high_raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(low_raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(high_raw));
    }
}
