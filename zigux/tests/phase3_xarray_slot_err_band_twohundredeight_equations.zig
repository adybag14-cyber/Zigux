const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_band_span = err_ptr.max_errno - 1;
const window_len = 208;
const center_left_index = (window_len / 2) - 1;
const center_right_index = window_len / 2;
const center_left_payload_index = center_left_index - (center_left_index & 1);
const center_right_payload_index = center_right_index + (center_right_index & 1);
const rejected_payload_base = xa_value.safe_inline_limit + 1;

fn rawFromResidue(residue: usize) usize {
    std.debug.assert(residue <= err_band_span);
    return err_ptr.err_floor + residue;
}

fn expectedCode(residue: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(residue));
}

fn rejectedPayload(even_residue: usize) usize {
    std.debug.assert((even_residue & 1) == 0);
    return rejected_payload_base + (even_residue >> 1);
}

test "twohundredeight raw windows keep err spacing and low-bit aliases exact" {
    const left_residues = [_]usize{ 0, 52, 982, 2020, 3000, 3886 };

    for (left_residues) |left_residue| {
        var raws: [window_len]usize = undefined;
        for (0..window_len) |idx| {
            const residue = left_residue + idx;
            const slot = xarray_slot_view.fromRaw(rawFromResidue(residue));
            raws[idx] = slot.rawValue();

            try testing.expect(slot.isErr());
            try testing.expectEqual(@as(?isize, expectedCode(residue)), slot.errorCode());
            try testing.expectEqual(@as(usize, (residue + 1) & 1), raws[idx] & xa_value.value_tag_mask);
            if (idx > 0) try testing.expectEqual(raws[idx - 1] + 1, raws[idx]);
        }

        const center_raw_sum = @as(u128, raws[center_left_index]) + @as(u128, raws[center_right_index]);
        for (0..center_right_index) |idx| {
            try testing.expectEqual(
                @as(u128, raws[idx]) + @as(u128, raws[window_len - 1 - idx]),
                center_raw_sum,
            );
        }
    }
}

test "twohundredeight constructor windows keep consecutive codes and reject aliased values" {
    var even_residue: usize = 0;
    while (even_residue + (window_len - 1) <= err_band_span) : (even_residue += 2) {
        var previous_code: ?isize = null;
        for (0..window_len) |idx| {
            const residue = even_residue + idx;
            const slot = if ((idx & 1) == 0)
                xarray_slot_view.fromRaw(rawFromResidue(residue))
            else
                xarray_slot_view.fromErrorCode(expectedCode(residue));

            try testing.expectEqual(rawFromResidue(residue), slot.rawValue());
            if (previous_code) |code| try testing.expectEqual(code + 1, slot.errorCode().?);
            previous_code = slot.errorCode().?;

            if ((idx & 1) == 0) {
                const payload = rejectedPayload(residue);
                try testing.expect(!xa_value.canRepresent(payload));
                try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(payload));
            }
        }
    }
}

test "twohundredeight keeps split raw and payload centers adjacent" {
    var even_residue: usize = 0;
    while (even_residue + (window_len - 1) <= err_band_span) : (even_residue += 2) {
        try testing.expectEqual(
            rawFromResidue(even_residue + center_left_index) + 1,
            rawFromResidue(even_residue + center_right_index),
        );
        try testing.expectEqual(
            expectedCode(even_residue + center_left_index) + 1,
            expectedCode(even_residue + center_right_index),
        );
        try testing.expectEqual(
            rejectedPayload(even_residue + center_left_payload_index) + 1,
            rejectedPayload(even_residue + center_right_payload_index),
        );
    }
}
