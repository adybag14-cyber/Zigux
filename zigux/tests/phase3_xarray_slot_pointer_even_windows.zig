const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "representative even raws between tagged values stay pointer-like" {
    const half_limit_raw = (try xa_value.makeValue(xa_value.safe_inline_limit / 2)) + 1;
    const upper_window_raw = err_ptr.err_floor - 3;
    const raws = [_]usize{
        2,
        0x1000,
        half_limit_raw,
        upper_window_raw,
    };

    for (raws) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);
        const lower_slot = xarray_slot_view.fromRaw(raw - 1);
        const upper_slot = xarray_slot_view.fromRaw(raw + 1);

        try testing.expect(raw != 0);
        try testing.expect((raw & xa_value.value_tag_mask) == 0);
        try testing.expect(raw < err_ptr.err_floor - 1);
        try testing.expect(!err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));

        try testing.expect(slot.isPointer());
        try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());

        try testing.expect(lower_slot.isValue());
        try testing.expect(upper_slot.isValue());
        try testing.expectEqual(raw - 1, try xa_value.makeValue(lower_slot.value().?));
        try testing.expectEqual(raw + 1, try xa_value.makeValue(upper_slot.value().?));
        try testing.expectEqual(lower_slot.value().? + 1, upper_slot.value().?);
    }
}

test "cutoff separator raw stays pointer-like between the last value and first err" {
    const highest_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const separator_raw = err_ptr.err_floor - 1;
    const first_err_raw = err_ptr.err_floor;

    const value_slot = xarray_slot_view.fromRaw(highest_value_raw);
    const separator_slot = xarray_slot_view.fromRaw(separator_raw);
    const err_slot = xarray_slot_view.fromRaw(first_err_raw);

    try testing.expectEqual(highest_value_raw + 1, separator_raw);
    try testing.expectEqual(separator_raw + 1, first_err_raw);

    try testing.expect(value_slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());

    try testing.expect(separator_slot.isPointer());
    try testing.expectEqual(@as(?usize, separator_raw), separator_slot.pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(separator_raw));

    try testing.expect(err_slot.isErr());
    try testing.expectEqual(@as(?isize, -4095), err_slot.errorCode());
}

test "pointer constructor roundtrips representative even raws across low mid and cutoff windows" {
    const half_limit_raw = (try xa_value.makeValue(xa_value.safe_inline_limit / 2)) + 1;
    const raws = [_]usize{
        2,
        half_limit_raw,
        err_ptr.err_floor - 3,
        err_ptr.err_floor - 1,
    };

    for (raws) |raw| {
        const constructed = xarray_slot_view.fromPointer(raw);
        const reread = xarray_slot_view.fromRaw(constructed.rawValue());

        try testing.expectEqual(raw, constructed.rawValue());
        try testing.expectEqual(raw, reread.rawValue());
        try testing.expect(constructed.isPointer());
        try testing.expect(reread.isPointer());
        try testing.expectEqual(@as(?usize, raw), constructed.pointerValue());
        try testing.expectEqual(@as(?usize, raw), reread.pointerValue());
        try testing.expectEqual(@as(?usize, null), reread.value());
        try testing.expectEqual(@as(?isize, null), reread.errorCode());
    }
}
