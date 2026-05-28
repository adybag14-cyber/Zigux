const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn projectRejectedSource(source: usize) usize {
    return (source << 1) | xa_value.value_tag_mask;
}

test "wrapped-high aliases leave even err_ptr raws between rejected sources" {
    const max = std.math.maxInt(usize);
    const cases = [_]struct {
        offset: usize,
        upper_code: isize,
        middle_code: isize,
        lower_code: isize,
    }{
        .{ .offset = 0, .upper_code = -1, .middle_code = -2, .lower_code = -3 },
        .{ .offset = 1, .upper_code = -3, .middle_code = -4, .lower_code = -5 },
        .{ .offset = 2, .upper_code = -5, .middle_code = -6, .lower_code = -7 },
        .{ .offset = 31, .upper_code = -63, .middle_code = -64, .lower_code = -65 },
    };

    for (cases) |case| {
        const upper_source = max - case.offset;
        const lower_source = upper_source - 1;
        const upper_raw = projectRejectedSource(upper_source);
        const lower_raw = projectRejectedSource(lower_source);
        const middle_raw = upper_raw - 1;
        const middle_slot = xarray_slot_view.fromRaw(middle_raw);

        try testing.expect(!xa_value.canRepresent(upper_source));
        try testing.expect(!xa_value.canRepresent(lower_source));
        try testing.expectEqual(@as(usize, 2), upper_raw - lower_raw);
        try testing.expectEqual(upper_raw - 1, middle_raw);
        try testing.expectEqual(lower_raw + 1, middle_raw);

        try testing.expectEqual(err_ptr.fromErrorCode(case.upper_code), upper_raw);
        try testing.expectEqual(err_ptr.fromErrorCode(case.middle_code), middle_raw);
        try testing.expectEqual(err_ptr.fromErrorCode(case.lower_code), lower_raw);
        try testing.expectEqual(@as(usize, 0), middle_raw & xa_value.value_tag_mask);

        try testing.expect(middle_slot.isErr());
        try testing.expect(!middle_slot.isValue());
        try testing.expect(!middle_slot.isPointer());
        try testing.expectEqual(@as(?isize, case.middle_code), middle_slot.errorCode());
        try testing.expectEqual(@as(?usize, null), middle_slot.value());
    }
}

test "even err_ptr neighbors remain tagged internal entries without value provenance" {
    const cases = [_]isize{ -2, -4, -64, -4094 };

    for (cases) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "final even err_ptr neighbor sits before the pointer gap handoff" {
    const max = std.math.maxInt(usize);
    const penultimate_odd_offset = (err_ptr.max_errno - 3) / 2;
    const upper_source = max - penultimate_odd_offset;
    const floor_source = upper_source - 1;

    const upper_raw = projectRejectedSource(upper_source);
    const middle_raw = upper_raw - 1;
    const floor_raw = projectRejectedSource(floor_source);
    const pointer_gap = floor_raw - 1;

    try testing.expect(!xa_value.canRepresent(upper_source));
    try testing.expect(!xa_value.canRepresent(floor_source));
    try testing.expectEqual(err_ptr.fromErrorCode(-4093), upper_raw);
    try testing.expectEqual(err_ptr.fromErrorCode(-4094), middle_raw);
    try testing.expectEqual(err_ptr.err_floor, floor_raw);
    try testing.expectEqual(err_ptr.err_floor - 1, pointer_gap);

    try testing.expect(xarray_slot_view.fromRaw(upper_raw).isErr());
    try testing.expect(xarray_slot_view.fromRaw(middle_raw).isErr());
    try testing.expect(xarray_slot_view.fromRaw(floor_raw).isErr());
    try testing.expect(xarray_slot_view.fromRaw(pointer_gap).isPointer());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_gap));
}
