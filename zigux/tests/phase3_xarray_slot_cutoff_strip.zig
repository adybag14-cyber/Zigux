const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "cutoff strip keeps the top xa_values pointer gaps and first err raws in lane order" {
    const raws = [_]usize{
        err_ptr.err_floor - 4,
        err_ptr.err_floor - 3,
        err_ptr.err_floor - 2,
        err_ptr.err_floor - 1,
        err_ptr.err_floor,
        err_ptr.err_floor + 1,
        err_ptr.err_floor + 2,
    };
    const expected_kinds = [_]xarray_slot_view.SlotKind{
        .value,
        .pointer,
        .value,
        .pointer,
        .err,
        .err,
        .err,
    };

    for (raws, expected_kinds, 0..) |raw, expected_kind, index| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(expected_kind, slot.kind());
        try testing.expectEqual(raw, slot.rawValue());

        switch (expected_kind) {
            .value => {
                const expected_value = xa_value.safe_inline_limit - @divExact(2 - (raw - (err_ptr.err_floor - 4)), 2);
                try testing.expectEqual(@as(?usize, expected_value), slot.value());
                try testing.expectEqual(@as(?isize, null), slot.errorCode());
                try testing.expectEqual(@as(?usize, null), slot.pointerValue());
                try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
            },
            .pointer => {
                try testing.expectEqual(@as(?usize, null), slot.value());
                try testing.expectEqual(@as(?isize, null), slot.errorCode());
                try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
                try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
            },
            .err => {
                const expected_code = -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(index - 4));
                try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
                try testing.expectEqual(@as(?usize, null), slot.value());
                try testing.expectEqual(@as(?usize, null), slot.pointerValue());
                try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
                try testing.expectEqual(raw, xarray_slot_view.fromErrorCode(expected_code).rawValue());
            },
            .null => unreachable,
        }
    }
}

test "top inline constructors land on the first cutoff strip raws" {
    const penultimate_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit - 1);
    const top_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const low_gap = xarray_slot_view.fromPointer(err_ptr.err_floor - 3);
    const high_gap = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);

    try testing.expectEqual(err_ptr.err_floor - 4, penultimate_value.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 2, top_value.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 3, low_gap.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 1, high_gap.rawValue());

    try testing.expectEqual(xarray_slot_view.SlotKind.value, penultimate_value.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.value, top_value.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, low_gap.kind());
    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, high_gap.kind());

    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit - 1), penultimate_value.value());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), top_value.value());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 3), low_gap.pointerValue());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), high_gap.pointerValue());
}

test "first three err constructors continue the cutoff strip without reopening value lane" {
    const floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const next_slot = xarray_slot_view.fromErrorCode(-4094);
    const third_slot = xarray_slot_view.fromErrorCode(-4093);

    try testing.expectEqual(err_ptr.err_floor, floor_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor + 1, next_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor + 2, third_slot.rawValue());

    try testing.expectEqual(@as(?isize, -4095), floor_slot.errorCode());
    try testing.expectEqual(@as(?isize, -4094), next_slot.errorCode());
    try testing.expectEqual(@as(?isize, -4093), third_slot.errorCode());

    try testing.expect(!xa_value.isValue(floor_slot.rawValue()));
    try testing.expect(!xa_value.isValue(next_slot.rawValue()));
    try testing.expect(!xa_value.isValue(third_slot.rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(floor_slot.rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(next_slot.rawValue()));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(third_slot.rawValue()));
}
