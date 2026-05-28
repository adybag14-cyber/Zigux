const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_band_span = err_ptr.max_errno - 1;
const window_len = 174;
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

fn expectedRejectedPayload(even_residue: usize) usize {
    std.debug.assert((even_residue & 1) == 0);
    return rejected_payload_base + (even_residue >> 1);
}

fn buildRawWindow(
    left_residue: usize,
    raws: *[window_len]usize,
    slots: *[window_len]xarray_slot_view.SlotView,
) void {
    for (0..window_len) |idx| {
        const residue = left_residue + idx;
        raws[idx] = rawFromResidue(residue);
        slots[idx] = xarray_slot_view.fromRaw(raws[idx]);
    }
}

test "representative 174-raw err-band windows keep alias-err spacing exact" {
    const left_residues = [_]usize{ 0, 10, 930, 1968, 2950, 3920 };

    for (left_residues) |left_residue| {
        var raws: [window_len]usize = undefined;
        var slots: [window_len]xarray_slot_view.SlotView = undefined;
        buildRawWindow(left_residue, &raws, &slots);

        for (0..window_len) |idx| {
            const residue = left_residue + idx;
            try testing.expect(slots[idx].isErr());
            try testing.expectEqual(@as(?isize, expectedCode(residue)), slots[idx].errorCode());
            try testing.expectEqual(@as(usize, (residue + 1) & 1), raws[idx] & xa_value.value_tag_mask);
        }

        for (0..window_len - 1) |idx| {
            try testing.expectEqual(raws[idx] + 1, raws[idx + 1]);
        }

        const seam_sum = @as(u128, raws[center_left_index]) + @as(u128, raws[center_right_index]);
        for (0..center_right_index) |idx| {
            try testing.expectEqual(
                @as(u128, raws[idx]) + @as(u128, raws[window_len - 1 - idx]),
                seam_sum,
            );
        }

        const seam_payload_sum =
            expectedRejectedPayload(left_residue + center_left_payload_index) +
            expectedRejectedPayload(left_residue + center_right_payload_index);
        for (0..(window_len / 2)) |pair_idx| {
            const even_idx = pair_idx * 2;
            const payload = expectedRejectedPayload(left_residue + even_idx);
            try testing.expectEqual(raws[even_idx], (payload << 1) | xa_value.value_tag_mask);

            if (pair_idx > 0) {
                const previous_payload = expectedRejectedPayload(left_residue + even_idx - 2);
                try testing.expectEqual(previous_payload + 1, payload);
            }

            if (even_idx < center_left_payload_index or even_idx > center_right_payload_index) {
                const mirrored_idx = (window_len - 1) - even_idx;
                if ((mirrored_idx & 1) == 0) {
                    const mirrored_payload = expectedRejectedPayload(left_residue + mirrored_idx);
                    try testing.expectEqual(payload + mirrored_payload, seam_payload_sum);
                }
            }
        }
    }
}

test "every interior onehundredseventyfour window keeps consecutive codes and alternating constructor families" {
    var even_residue: usize = 0;
    while (even_residue + (window_len - 1) <= err_band_span) : (even_residue += 2) {
        var slots: [window_len]xarray_slot_view.SlotView = undefined;

        for (0..window_len) |idx| {
            const residue = even_residue + idx;
            slots[idx] = if ((idx & 1) == 0)
                xarray_slot_view.fromRaw(rawFromResidue(residue))
            else
                xarray_slot_view.fromErrorCode(expectedCode(residue));

            try testing.expectEqual(rawFromResidue(residue), slots[idx].rawValue());
        }

        for (0..window_len - 1) |idx| {
            try testing.expectEqual(slots[idx].errorCode().? + 1, slots[idx + 1].errorCode().?);
        }

        for (0..(window_len / 2)) |payload_idx| {
            const even_offset = payload_idx * 2;
            const payload = expectedRejectedPayload(even_residue + even_offset);
            try testing.expect(!xa_value.canRepresent(payload));
            try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(payload));
        }
    }
}

test "onehundredseventyfour windows preserve a split raw seam and a split payload seam" {
    var even_residue: usize = 0;
    while (even_residue + (window_len - 1) <= err_band_span) : (even_residue += 2) {
        const seam_code_sum =
            expectedCode(even_residue + center_left_index) +
            expectedCode(even_residue + center_right_index);
        const seam_raw_sum =
            @as(u128, rawFromResidue(even_residue + center_left_index)) +
            @as(u128, rawFromResidue(even_residue + center_right_index));
        for (0..center_right_index) |idx| {
            const left_residue = even_residue + idx;
            const right_residue = even_residue + (window_len - 1 - idx);

            try testing.expectEqual(
                expectedCode(left_residue) + expectedCode(right_residue),
                seam_code_sum,
            );
            try testing.expectEqual(
                @as(u128, rawFromResidue(left_residue)) + @as(u128, rawFromResidue(right_residue)),
                seam_raw_sum,
            );
        }

        try testing.expectEqual(
            expectedRejectedPayload(even_residue + center_left_payload_index) + 1,
            expectedRejectedPayload(even_residue + center_right_payload_index),
        );
        try testing.expectEqual(
            expectedCode(even_residue + center_left_index) + 1,
            expectedCode(even_residue + center_right_index),
        );
        try testing.expectEqual(
            rawFromResidue(even_residue + center_left_index) + 1,
            rawFromResidue(even_residue + center_right_index),
        );
    }
}
