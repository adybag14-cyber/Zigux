const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_band_span = err_ptr.max_errno - 1;
const window_len = 131;
const center_index = window_len / 2;
const center_payload_left_index = center_index - 1;
const center_payload_right_index = center_index + 1;
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

test "representative 131-raw err-band windows keep alias-err spacing exact" {
    const left_residues = [_]usize{ 0, 2, 934, 1972, 2972, 3964 };

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

        for (0..center_index) |idx| {
            try testing.expectEqual(
                @as(u128, raws[idx]) + @as(u128, raws[window_len - 1 - idx]),
                @as(u128, raws[center_index]) * 2,
            );
        }

        const seam_payload_sum =
            expectedRejectedPayload(left_residue + center_payload_left_index) +
            expectedRejectedPayload(left_residue + center_payload_right_index);
        for (0..((window_len + 1) / 2)) |pair_idx| {
            const even_idx = pair_idx * 2;
            const payload = expectedRejectedPayload(left_residue + even_idx);
            try testing.expectEqual(raws[even_idx], (payload << 1) | xa_value.value_tag_mask);

            if (pair_idx > 0) {
                const previous_payload = expectedRejectedPayload(left_residue + even_idx - 2);
                try testing.expectEqual(previous_payload + 1, payload);
            }

            if (even_idx < center_index) {
                const mirrored_payload = expectedRejectedPayload(left_residue + ((window_len - 1) - even_idx));
                try testing.expectEqual(payload + mirrored_payload, seam_payload_sum);
            }
        }
    }
}

test "every interior onehundredthirtyone window keeps consecutive codes and alternating constructor families" {
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

        for (0..((window_len + 1) / 2)) |payload_idx| {
            const even_offset = payload_idx * 2;
            const payload = expectedRejectedPayload(even_residue + even_offset);
            try testing.expect(!xa_value.canRepresent(payload));
            try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(payload));
        }
    }
}

test "onehundredthirtyone windows preserve a centered raw equation and a split payload seam" {
    var even_residue: usize = 0;
    while (even_residue + (window_len - 1) <= err_band_span) : (even_residue += 2) {
        const center_residue = even_residue + center_index;
        const seam_payload_sum =
            expectedRejectedPayload(even_residue + center_payload_left_index) +
            expectedRejectedPayload(even_residue + center_payload_right_index);

        for (0..center_index) |idx| {
            const left_residue = even_residue + idx;
            const right_residue = even_residue + (window_len - 1 - idx);

            try testing.expectEqual(
                expectedCode(left_residue) + expectedCode(right_residue),
                expectedCode(center_residue) * 2,
            );
            try testing.expectEqual(
                @as(u128, rawFromResidue(left_residue)) + @as(u128, rawFromResidue(right_residue)),
                @as(u128, rawFromResidue(center_residue)) * 2,
            );
        }

        for (0..(center_index / 2)) |pair_idx| {
            const left_payload_residue = even_residue + (pair_idx * 2);
            const right_payload_residue = even_residue + ((window_len - 1) - (pair_idx * 2));
            try testing.expectEqual(
                expectedRejectedPayload(left_payload_residue) +
                    expectedRejectedPayload(right_payload_residue),
                seam_payload_sum,
            );
        }

        try testing.expectEqual(
            expectedRejectedPayload(even_residue + center_payload_left_index - 2) + 1,
            expectedRejectedPayload(even_residue + center_payload_left_index),
        );
        try testing.expectEqual(
            expectedRejectedPayload(even_residue + center_payload_left_index) + 1,
            expectedRejectedPayload(even_residue + center_payload_right_index),
        );
        try testing.expectEqual(
            expectedRejectedPayload(even_residue + center_payload_right_index) + 1,
            expectedRejectedPayload(even_residue + center_payload_right_index + 2),
        );
        try testing.expectEqual(
            expectedCode(center_residue - 1) + 1,
            expectedCode(center_residue),
        );
        try testing.expectEqual(
            expectedCode(center_residue),
            err_ptr.toErrorCode(rawFromResidue(center_residue)),
        );
    }
}
