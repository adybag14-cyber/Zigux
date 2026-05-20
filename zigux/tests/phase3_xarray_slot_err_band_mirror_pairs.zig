const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_top = err_ptr.fromErrorCode(-1);
const err_band_span = err_ptr.max_errno - 1;

fn rawFromFloor(offset: usize) usize {
    std.debug.assert(offset <= err_band_span);
    return err_ptr.err_floor + offset;
}

fn rawFromTop(offset: usize) usize {
    std.debug.assert(offset <= err_band_span);
    return err_top - offset;
}

test "mirrored err band offsets stay in the err lane and keep constant endpoint distance" {
    try testing.expectEqual(err_band_span, err_top - err_ptr.err_floor);

    const offsets = [_]usize{ 0, 1, 2, 17, 1023, 2047, 4093, 4094 };

    for (offsets) |offset| {
        const low_raw = rawFromFloor(offset);
        const high_raw = rawFromTop(offset);
        const low_slot = xarray_slot_view.fromRaw(low_raw);
        const high_slot = xarray_slot_view.fromRaw(high_raw);

        try testing.expect(low_slot.isErr());
        try testing.expect(high_slot.isErr());
        try testing.expect(!low_slot.isValue());
        try testing.expect(!high_slot.isValue());
        try testing.expect(!low_slot.isPointer());
        try testing.expect(!high_slot.isPointer());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(low_raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(high_raw));
        try testing.expectEqual(err_ptr.err_floor + offset, low_slot.rawValue());
        try testing.expectEqual(err_top - offset, high_slot.rawValue());

        const low_code = low_slot.errorCode().?;
        const high_code = high_slot.errorCode().?;

        try testing.expectEqual(-@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(offset)), low_code);
        try testing.expectEqual(-1 - @as(isize, @intCast(offset)), high_code);
        try testing.expectEqual(@as(isize, -(@as(isize, @intCast(err_ptr.max_errno)) + 1)), low_code + high_code);
    }
}

test "mirrored err band pairs preserve the same parity family at both ends" {
    const offsets = [_]usize{ 0, 1, 2, 3, 1022, 1023, 2046, 2047, 4094 };

    for (offsets) |offset| {
        const low_raw = rawFromFloor(offset);
        const high_raw = rawFromTop(offset);

        try testing.expectEqual(low_raw & xa_value.value_tag_mask, high_raw & xa_value.value_tag_mask);
        try testing.expect(!xa_value.isValue(low_raw));
        try testing.expect(!xa_value.isValue(high_raw));

        if ((low_raw & xa_value.value_tag_mask) != 0) {
            try testing.expect(!xa_value.canRepresent(low_raw >> 1));
            try testing.expect(!xa_value.canRepresent(high_raw >> 1));
        }
    }
}

test "mirrored err band pairs rebuild through fromErrorCode without raw drift" {
    const offsets = [_]usize{ 0, 5, 29, 511, 2047, 4090, 4094 };

    for (offsets) |offset| {
        const low_raw = rawFromFloor(offset);
        const high_raw = rawFromTop(offset);

        const low_slot = xarray_slot_view.fromRaw(low_raw);
        const high_slot = xarray_slot_view.fromRaw(high_raw);

        const low_rebuilt = xarray_slot_view.fromErrorCode(low_slot.errorCode().?);
        const high_rebuilt = xarray_slot_view.fromErrorCode(high_slot.errorCode().?);

        try testing.expectEqual(low_slot.kind(), low_rebuilt.kind());
        try testing.expectEqual(high_slot.kind(), high_rebuilt.kind());
        try testing.expectEqual(low_slot.rawValue(), low_rebuilt.rawValue());
        try testing.expectEqual(high_slot.rawValue(), high_rebuilt.rawValue());
    }
}
