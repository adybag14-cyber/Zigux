const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_top = err_ptr.fromErrorCode(-1);
const err_band_span = err_ptr.max_errno - 1;

const hexadecant_offsets = [_]usize{
    0,
    255,
    511,
    767,
    1023,
    1279,
    1535,
    1791,
    2047,
    2303,
    2559,
    2815,
    3071,
    3327,
    3583,
    3839,
    err_band_span,
};

const hexadecant_codes = [_]isize{
    -4095,
    -3840,
    -3584,
    -3328,
    -3072,
    -2816,
    -2560,
    -2304,
    -2048,
    -1792,
    -1536,
    -1280,
    -1024,
    -768,
    -512,
    -256,
    -1,
};

fn rawFromFloor(offset: usize) usize {
    std.debug.assert(offset <= err_band_span);
    return err_ptr.err_floor + offset;
}

test "hexadecant anchors decode to the expected err band milestones" {
    for (hexadecant_offsets, hexadecant_codes) |offset, expected_code| {
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

    try testing.expectEqual(err_ptr.err_floor, rawFromFloor(hexadecant_offsets[0]));
    try testing.expectEqual(err_top, rawFromFloor(hexadecant_offsets[16]));
}

test "hexadecant anchors keep the err band's symmetric 255 then 256 cadence" {
    var raws: [hexadecant_offsets.len]usize = undefined;
    for (hexadecant_offsets, 0..) |offset, index| {
        raws[index] = rawFromFloor(offset);
    }

    for (0..16) |index| {
        const gap = raws[index + 1] - raws[index];
        const expected_gap: usize = if (index == 0 or index == 15) 255 else 256;

        try testing.expectEqual(expected_gap, gap);
        try testing.expectEqual(
            @as(usize, @intCast(hexadecant_codes[index + 1] - hexadecant_codes[index])),
            gap,
        );
        try testing.expectEqual(gap, raws[16 - index] - raws[15 - index]);
    }

    try testing.expectEqual(@as(usize, 511), raws[2] - raws[0]);
    try testing.expectEqual(@as(usize, 1023), raws[4] - raws[0]);
    try testing.expectEqual(@as(usize, 2047), raws[8] - raws[0]);
    try testing.expectEqual(@as(usize, 2047), raws[16] - raws[8]);
}

test "interior hexadecant anchors stay even err raws bracketed by rejected aliases" {
    for (hexadecant_offsets[1..16], hexadecant_codes[1..16]) |offset, expected_code| {
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
