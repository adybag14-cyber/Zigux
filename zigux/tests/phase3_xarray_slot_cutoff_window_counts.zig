const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const WindowCase = struct {
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
};

test "cutoff window keeps the expected lane census and closed accessors" {
    const last_value = xa_value.safe_inline_limit;
    const cases = [_]WindowCase{
        .{
            .raw = try xa_value.makeValue(last_value - 2),
            .kind = .value,
            .value = last_value - 2,
            .error_code = null,
            .pointer = null,
        },
        .{
            .raw = try xa_value.makeValue(last_value - 1),
            .kind = .value,
            .value = last_value - 1,
            .error_code = null,
            .pointer = null,
        },
        .{
            .raw = try xa_value.makeValue(last_value),
            .kind = .value,
            .value = last_value,
            .error_code = null,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .raw = err_ptr.err_floor,
            .kind = .err,
            .value = null,
            .error_code = -4095,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor + 1,
            .kind = .err,
            .value = null,
            .error_code = -4094,
            .pointer = null,
        },
        .{
            .raw = err_ptr.err_floor + 2,
            .kind = .err,
            .value = null,
            .error_code = -4093,
            .pointer = null,
        },
    };

    var value_count: usize = 0;
    var pointer_count: usize = 0;
    var err_count: usize = 0;

    try testing.expectEqual(cases[0].raw + 2, cases[1].raw);
    try testing.expectEqual(cases[1].raw + 2, cases[2].raw);
    try testing.expectEqual(cases[2].raw + 1, cases[3].raw);
    try testing.expectEqual(cases[3].raw + 1, cases[4].raw);
    try testing.expectEqual(cases[4].raw + 1, cases[5].raw);
    try testing.expectEqual(cases[5].raw + 1, cases[6].raw);

    for (cases) |case| {
        const slot = xarray_slot_view.fromRaw(case.raw);

        try testing.expectEqual(case.kind, slot.kind());
        try testing.expectEqual(case.raw, slot.rawValue());
        try testing.expectEqual(case.value, slot.value());
        try testing.expectEqual(case.error_code, slot.errorCode());
        try testing.expectEqual(case.pointer, slot.pointerValue());

        switch (case.kind) {
            .value => value_count += 1,
            .pointer => pointer_count += 1,
            .err => err_count += 1,
            .null => unreachable,
        }
    }

    try testing.expectEqual(@as(usize, 3), value_count);
    try testing.expectEqual(@as(usize, 1), pointer_count);
    try testing.expectEqual(@as(usize, 3), err_count);
}

test "cutoff window leaves only the separator outside the tagged-entry census" {
    const raws = [_]usize{
        try xa_value.makeValue(xa_value.safe_inline_limit - 2),
        try xa_value.makeValue(xa_value.safe_inline_limit - 1),
        try xa_value.makeValue(xa_value.safe_inline_limit),
        err_ptr.err_floor - 1,
        err_ptr.err_floor,
        err_ptr.err_floor + 1,
        err_ptr.err_floor + 2,
    };

    var tagged_count: usize = 0;
    var odd_count: usize = 0;

    for (raws) |raw| {
        if (xarray_slot_view.isTaggedInternalEntry(raw)) {
            tagged_count += 1;
        }
        if ((raw & 1) == 1) {
            odd_count += 1;
        }
    }

    try testing.expectEqual(@as(usize, 6), tagged_count);
    try testing.expectEqual(@as(usize, 5), odd_count);
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(err_ptr.err_floor - 1));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(err_ptr.err_floor));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(err_ptr.err_floor + 1));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(err_ptr.err_floor + 2));
}
