const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_top = err_ptr.fromErrorCode(-1);
const err_band_span = err_ptr.max_errno - 1;
const anchor_count: usize = 2049;

fn anchorOffset(index: usize) usize {
    std.debug.assert(index < anchor_count);
    if (index == 0) {
        return 0;
    }
    if (index == anchor_count - 1) {
        return err_band_span;
    }
    return 1 + ((index - 1) * 2);
}

fn rawFromFloor(offset: usize) usize {
    std.debug.assert(offset <= err_band_span);
    return err_ptr.err_floor + offset;
}

fn expectedCode(offset: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(offset));
}

test "two-thousand-forty-eighth anchors decode to the expected err band milestones" {
    for (0..anchor_count) |index| {
        const offset = anchorOffset(index);
        const raw = rawFromFloor(offset);
        const code = expectedCode(offset);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(slot.isErr());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(raw, xarray_slot_view.fromErrorCode(code).rawValue());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }

    try testing.expectEqual(err_ptr.err_floor, rawFromFloor(anchorOffset(0)));
    try testing.expectEqual(err_top, rawFromFloor(anchorOffset(anchor_count - 1)));
}

test "two-thousand-forty-eighth anchors keep the err band's symmetric 1 then 2 cadence" {
    var raws: [anchor_count]usize = undefined;
    for (0..anchor_count) |index| {
        raws[index] = rawFromFloor(anchorOffset(index));
    }

    for (0..anchor_count - 1) |index| {
        const gap = raws[index + 1] - raws[index];
        const expected_gap: usize = if (index == 0 or index == anchor_count - 2) 1 else 2;

        try testing.expectEqual(expected_gap, gap);
        try testing.expectEqual(
            @as(usize, @intCast(expectedCode(anchorOffset(index + 1)) - expectedCode(anchorOffset(index)))),
            gap,
        );
        try testing.expectEqual(gap, raws[(anchor_count - 1) - index] - raws[(anchor_count - 2) - index]);
    }

    try testing.expectEqual(@as(usize, 3), raws[2] - raws[0]);
    try testing.expectEqual(@as(usize, 7), raws[4] - raws[0]);
    try testing.expectEqual(@as(usize, 15), raws[8] - raws[0]);
    try testing.expectEqual(@as(usize, 31), raws[16] - raws[0]);
    try testing.expectEqual(@as(usize, 63), raws[32] - raws[0]);
    try testing.expectEqual(@as(usize, 127), raws[64] - raws[0]);
    try testing.expectEqual(@as(usize, 255), raws[128] - raws[0]);
    try testing.expectEqual(@as(usize, 511), raws[256] - raws[0]);
    try testing.expectEqual(@as(usize, 1023), raws[512] - raws[0]);
    try testing.expectEqual(@as(usize, 2047), raws[1024] - raws[0]);
    try testing.expectEqual(@as(usize, 2047), raws[2048] - raws[1024]);
}

test "interior two-thousand-forty-eighth anchors stay even err raws bracketed by rejected aliases" {
    for (1..anchor_count - 1) |index| {
        const offset = anchorOffset(index);
        const raw = rawFromFloor(offset);
        const low_neighbor = raw - 1;
        const high_neighbor = raw + 1;
        const code = expectedCode(offset);
        const slot = xarray_slot_view.fromRaw(raw);
        const low_slot = xarray_slot_view.fromRaw(low_neighbor);
        const high_slot = xarray_slot_view.fromRaw(high_neighbor);

        try testing.expect(slot.isErr());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 1), low_neighbor & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 1), high_neighbor & xa_value.value_tag_mask);

        try testing.expect(low_slot.isErr());
        try testing.expect(high_slot.isErr());
        try testing.expectEqual(@as(?isize, code - 1), low_slot.errorCode());
        try testing.expectEqual(@as(?isize, code + 1), high_slot.errorCode());
        try testing.expect(!xa_value.isValue(low_neighbor));
        try testing.expect(!xa_value.isValue(high_neighbor));
        try testing.expect(!xa_value.canRepresent(low_neighbor >> 1));
        try testing.expect(!xa_value.canRepresent(high_neighbor >> 1));
    }
}
