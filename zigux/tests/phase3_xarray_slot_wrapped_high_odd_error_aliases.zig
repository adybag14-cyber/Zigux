const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn projectRejectedSource(source: usize) usize {
    return (source << 1) | xa_value.value_tag_mask;
}

test "wrapped-high rejected sources alias the top odd err_ptr codes" {
    const max = std.math.maxInt(usize);
    const cases = [_]struct {
        offset: usize,
        expected_code: isize,
    }{
        .{ .offset = 0, .expected_code = -1 },
        .{ .offset = 1, .expected_code = -3 },
        .{ .offset = 2, .expected_code = -5 },
        .{ .offset = 3, .expected_code = -7 },
        .{ .offset = 7, .expected_code = -15 },
    };

    for (cases) |case| {
        const source = max - case.offset;
        const raw = projectRejectedSource(source);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(!xa_value.canRepresent(source));
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, case.expected_code), slot.errorCode());
        try testing.expectEqual(err_ptr.fromErrorCode(case.expected_code), raw);
    }
}

test "wrapped-high odd-error aliases descend by one source step and two raw steps" {
    const max = std.math.maxInt(usize);
    const upper_source = max - 12;
    const lower_source = max - 13;
    const upper_raw = projectRejectedSource(upper_source);
    const lower_raw = projectRejectedSource(lower_source);
    const upper_slot = xarray_slot_view.fromRaw(upper_raw);
    const lower_slot = xarray_slot_view.fromRaw(lower_raw);

    try testing.expect(!xa_value.canRepresent(upper_source));
    try testing.expect(!xa_value.canRepresent(lower_source));
    try testing.expect(upper_slot.isErr());
    try testing.expect(lower_slot.isErr());
    try testing.expectEqual(@as(usize, 2), upper_raw - lower_raw);
    try testing.expectEqual(@as(?isize, -25), upper_slot.errorCode());
    try testing.expectEqual(@as(?isize, -27), lower_slot.errorCode());
}

test "wrapped-high alias ladder ends at err_floor before returning to the top inline value" {
    const max = std.math.maxInt(usize);
    const last_err_offset = (err_ptr.max_errno - 1) / 2;
    const err_source = max - last_err_offset;
    const value_source = err_source - 1;

    const err_raw = projectRejectedSource(err_source);
    const value_raw = projectRejectedSource(value_source);
    const err_slot = xarray_slot_view.fromRaw(err_raw);
    const value_slot = xarray_slot_view.fromRaw(value_raw);

    try testing.expect(!xa_value.canRepresent(err_source));
    try testing.expect(!xa_value.canRepresent(value_source));

    try testing.expectEqual(err_ptr.err_floor, err_raw);
    try testing.expect(err_slot.isErr());
    try testing.expectEqual(@as(?isize, -4095), err_slot.errorCode());

    try testing.expectEqual(try xa_value.makeValue(xa_value.safe_inline_limit), value_raw);
    try testing.expect(value_slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), value_slot.value());
    try testing.expect(!value_slot.isErr());
}
