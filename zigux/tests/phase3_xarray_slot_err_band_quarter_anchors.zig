const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_top = err_ptr.fromErrorCode(-1);
const err_band_span = err_ptr.max_errno - 1;
const lower_quarter_offset = (err_ptr.max_errno - 3) / 4;
const midpoint_offset = err_band_span / 2;
const upper_quarter_offset = err_band_span - lower_quarter_offset;

const anchor_offsets = [_]usize{
    0,
    lower_quarter_offset,
    midpoint_offset,
    upper_quarter_offset,
    err_band_span,
};

const anchor_codes = [_]isize{
    -@as(isize, @intCast(err_ptr.max_errno)),
    -3072,
    -2048,
    -1024,
    -1,
};

fn rawFromFloor(offset: usize) usize {
    std.debug.assert(offset <= err_band_span);
    return err_ptr.err_floor + offset;
}

test "quarter anchors decode to the expected err band milestones" {
    for (anchor_offsets, anchor_codes) |offset, expected_code| {
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

    try testing.expectEqual(err_ptr.err_floor, rawFromFloor(anchor_offsets[0]));
    try testing.expectEqual(err_top, rawFromFloor(anchor_offsets[4]));
}

test "quarter anchors split the err band into symmetric outer and inner gaps" {
    const raws = [_]usize{
        rawFromFloor(anchor_offsets[0]),
        rawFromFloor(anchor_offsets[1]),
        rawFromFloor(anchor_offsets[2]),
        rawFromFloor(anchor_offsets[3]),
        rawFromFloor(anchor_offsets[4]),
    };

    const expected_gaps = [_]usize{ 1023, 1024, 1024, 1023 };

    for (expected_gaps, 0..) |expected_gap, index| {
        try testing.expectEqual(expected_gap, raws[index + 1] - raws[index]);
        try testing.expectEqual(
            @as(usize, @intCast(anchor_codes[index + 1] - anchor_codes[index])),
            raws[index + 1] - raws[index],
        );
    }

    try testing.expectEqual(raws[1] - raws[0], raws[4] - raws[3]);
    try testing.expectEqual(raws[2] - raws[1], raws[3] - raws[2]);
    try testing.expectEqual(midpoint_offset, raws[2] - raws[0]);
    try testing.expectEqual(midpoint_offset, raws[4] - raws[2]);
}

test "interior quarter anchors are even err raws bracketed by rejected aliases" {
    const interior_offsets = [_]usize{
        lower_quarter_offset,
        midpoint_offset,
        upper_quarter_offset,
    };
    const interior_codes = [_]isize{ -3072, -2048, -1024 };

    for (interior_offsets, interior_codes) |offset, expected_code| {
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
