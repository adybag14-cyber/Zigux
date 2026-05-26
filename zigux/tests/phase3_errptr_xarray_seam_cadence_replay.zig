const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "tail xa_value raws advance by two and leave odd seam gaps pointer-like" {
    const tail_values = [_]usize{
        xa_value.safe_inline_limit - 3,
        xa_value.safe_inline_limit - 2,
        xa_value.safe_inline_limit - 1,
        xa_value.safe_inline_limit,
    };

    var previous_raw: ?usize = null;
    for (tail_values) |value| {
        const raw = try xa_value.makeValue(value);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(@as(?usize, value), slot.value());
        try testing.expectEqual(xarray_slot_view.SlotKind.value, slot.kind());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

        if (previous_raw) |prior| {
            try testing.expectEqual(prior + 2, raw);

            const gap_raw = prior + 1;
            const gap_slot = xarray_slot_view.fromRaw(gap_raw);
            try testing.expectEqual(raw - 1, gap_raw);
            try testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap_slot.kind());
            try testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());
            try testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));
        }

        previous_raw = raw;
    }
}

test "err raws above the floor stay contiguous and decode as the same arithmetic progression" {
    const err_codes = [_]isize{ -4095, -4094, -4093, -4092 };

    var previous_raw: ?usize = null;
    for (err_codes, 0..) |code, offset| {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(err_ptr.err_floor + offset, raw);
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

        if (previous_raw) |prior| {
            try testing.expectEqual(prior + 1, raw);
        }

        previous_raw = raw;
    }
}

test "the seam cadence stays aligned across tail values pointer gaps and the err floor" {
    const last_four_value_raws = [_]usize{
        try xa_value.makeValue(xa_value.safe_inline_limit - 3),
        try xa_value.makeValue(xa_value.safe_inline_limit - 2),
        try xa_value.makeValue(xa_value.safe_inline_limit - 1),
        try xa_value.makeValue(xa_value.safe_inline_limit),
    };

    try testing.expectEqual(err_ptr.err_floor - 8, last_four_value_raws[0]);
    try testing.expectEqual(err_ptr.err_floor - 6, last_four_value_raws[1]);
    try testing.expectEqual(err_ptr.err_floor - 4, last_four_value_raws[2]);
    try testing.expectEqual(err_ptr.err_floor - 2, last_four_value_raws[3]);

    for (last_four_value_raws, 0..) |raw, index| {
        const gap_raw = raw + 1;

        try testing.expectEqual(xarray_slot_view.SlotKind.value, xarray_slot_view.fromRaw(raw).kind());
        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, xarray_slot_view.fromRaw(gap_raw).kind());

        if (index != last_four_value_raws.len - 1) {
            try testing.expectEqual(gap_raw + 1, last_four_value_raws[index + 1]);
        } else {
            try testing.expectEqual(err_ptr.err_floor, gap_raw + 1);
        }
    }
}
