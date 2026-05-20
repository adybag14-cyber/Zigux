const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_top = err_ptr.fromErrorCode(-1);
const err_band_span = err_ptr.max_errno - 1;

const octant_offsets = [_]usize{
    0,
    511,
    1023,
    1535,
    2047,
    2559,
    3071,
    3583,
    err_band_span,
};

const octant_codes = [_]isize{
    -4095,
    -3584,
    -3072,
    -2560,
    -2048,
    -1536,
    -1024,
    -512,
    -1,
};

fn rawFromFloor(offset: usize) usize {
    std.debug.assert(offset <= err_band_span);
    return err_ptr.err_floor + offset;
}

test "octant anchors decode to the expected err band milestones" {
    for (octant_offsets, octant_codes) |offset, expected_code| {
        const raw = rawFromFloor(offset);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(slot.isErr());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(raw, xarray_slot_view.fromErrorCode(expected_code).rawValue());
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }

    try testing.expectEqual(err_ptr.err_floor, rawFromFloor(octant_offsets[0]));
    try testing.expectEqual(err_top, rawFromFloor(octant_offsets[8]));
}

test "octant anchors keep the err band's symmetric 511 then 512 cadence" {
    const raws = [_]usize{
        rawFromFloor(octant_offsets[0]),
        rawFromFloor(octant_offsets[1]),
        rawFromFloor(octant_offsets[2]),
        rawFromFloor(octant_offsets[3]),
        rawFromFloor(octant_offsets[4]),
        rawFromFloor(octant_offsets[5]),
        rawFromFloor(octant_offsets[6]),
        rawFromFloor(octant_offsets[7]),
        rawFromFloor(octant_offsets[8]),
    };
    const expected_gaps = [_]usize{ 511, 512, 512, 512, 512, 512, 512, 511 };

    for (expected_gaps, 0..) |expected_gap, index| {
        try testing.expectEqual(expected_gap, raws[index + 1] - raws[index]);
        try testing.expectEqual(
            @as(usize, @intCast(octant_codes[index + 1] - octant_codes[index])),
            raws[index + 1] - raws[index],
        );
    }

    try testing.expectEqual(raws[1] - raws[0], raws[8] - raws[7]);
    try testing.expectEqual(raws[2] - raws[1], raws[7] - raws[6]);
    try testing.expectEqual(raws[3] - raws[2], raws[6] - raws[5]);
    try testing.expectEqual(raws[4] - raws[3], raws[5] - raws[4]);
}

test "interior octant anchors stay even err raws bracketed by rejected aliases" {
    for (octant_offsets[1..8], octant_codes[1..8]) |offset, expected_code| {
        const raw = rawFromFloor(offset);
        const low_neighbor = raw - 1;
        const high_neighbor = raw + 1;
        const slot = xarray_slot_view.fromRaw(raw);
        const low_slot = xarray_slot_view.fromRaw(low_neighbor);
        const high_slot = xarray_slot_view.fromRaw(high_neighbor);

        try testing.expect(slot.isErr());
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 1), low_neighbor & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 1), high_neighbor & xa_value.value_tag_mask);

        try testing.expect(low_slot.isErr());
        try testing.expect(high_slot.isErr());
        try testing.expectEqual(@as(?isize, expected_code - 1), low_slot.errorCode());
        try testing.expectEqual(@as(?isize, expected_code + 1), high_slot.errorCode());
        try testing.expect(!xa_value.isValue(low_neighbor));
        try testing.expect(!xa_value.isValue(high_neighbor));
        try testing.expect(!xa_value.canRepresent(low_neighbor >> 1));
        try testing.expect(!xa_value.canRepresent(high_neighbor >> 1));
    }
}
