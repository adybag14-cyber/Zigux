const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_band_span = err_ptr.max_errno - 1;
const window_len = 120;
const center_left_index = (window_len / 2) - 1;
const center_right_index = window_len / 2;
const center_payload_index = center_right_index - 1;
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

test "representative 120-raw err-band windows keep alias-err spacing exact" {
    const left_residues = [_]usize{ 1, 5, 933, 1975, 2977, 3975 };

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

        const center_payload = expectedRejectedPayload(left_residue + center_payload_index);
        for (0..(window_len / 2)) |pair_idx| {
            const odd_idx = (pair_idx * 2) + 1;
            const payload = expectedRejectedPayload(left_residue + odd_idx);
            try testing.expectEqual(raws[odd_idx], (payload << 1) | xa_value.value_tag_mask);

            if (pair_idx > 0) {
                const previous_payload = expectedRejectedPayload(left_residue + odd_idx - 2);
                try testing.expectEqual(previous_payload + 1, payload);
            }

            if (odd_idx < center_payload_index) {
                const mirrored_payload = expectedRejectedPayload(left_residue + ((window_len - 2) - odd_idx));
                try testing.expectEqual(payload + mirrored_payload, center_payload * 2);
            }
        }
    }
}

test "every interior onehundredtwenty window keeps consecutive codes and alternating constructor families" {
    var odd_residue: usize = 1;
    while (odd_residue + (window_len - 1) <= err_band_span) : (odd_residue += 2) {
        var slots: [window_len]xarray_slot_view.SlotView = undefined;

        for (0..window_len) |idx| {
            const residue = odd_residue + idx;
            slots[idx] = if ((idx & 1) == 0)
                xarray_slot_view.fromErrorCode(expectedCode(residue))
            else
                xarray_slot_view.fromRaw(rawFromResidue(residue));

            try testing.expectEqual(rawFromResidue(residue), slots[idx].rawValue());
        }

        for (0..window_len - 1) |idx| {
            try testing.expectEqual(slots[idx].errorCode().? + 1, slots[idx + 1].errorCode().?);
        }

        for (0..(window_len / 2)) |payload_idx| {
            const odd_offset = (payload_idx * 2) + 1;
            const payload = expectedRejectedPayload(odd_residue + odd_offset);
            try testing.expect(!xa_value.canRepresent(payload));
            try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(payload));
        }
    }
}

test "onehundredtwenty windows preserve a dual-center raw seam and a centered payload lane" {
    var odd_residue: usize = 1;
    while (odd_residue + (window_len - 1) <= err_band_span) : (odd_residue += 2) {
        const seam_code_sum =
            expectedCode(odd_residue + center_left_index) +
            expectedCode(odd_residue + center_right_index);
        const seam_raw_sum =
            @as(u128, rawFromResidue(odd_residue + center_left_index)) +
            @as(u128, rawFromResidue(odd_residue + center_right_index));
        const center_payload = expectedRejectedPayload(odd_residue + center_payload_index);

        for (0..center_right_index) |idx| {
            const left_residue = odd_residue + idx;
            const right_residue = odd_residue + (window_len - 1 - idx);

            try testing.expectEqual(
                expectedCode(left_residue) + expectedCode(right_residue),
                seam_code_sum,
            );
            try testing.expectEqual(
                @as(u128, rawFromResidue(left_residue)) + @as(u128, rawFromResidue(right_residue)),
                seam_raw_sum,
            );
        }

        for (0..(center_left_index / 2)) |pair_idx| {
            const left_odd_residue = odd_residue + ((pair_idx * 2) + 1);
            const right_odd_residue = odd_residue + ((window_len - 2) - ((pair_idx * 2) + 1));
            try testing.expectEqual(
                expectedRejectedPayload(left_odd_residue) + expectedRejectedPayload(right_odd_residue),
                center_payload * 2,
            );
        }

        try testing.expectEqual(
            expectedRejectedPayload(odd_residue + 1) + center_left_index,
            expectedRejectedPayload(odd_residue + (window_len - 1)),
        );
        try testing.expectEqual(
            expectedRejectedPayload(odd_residue + center_payload_index - 2) + 1,
            center_payload,
        );
        try testing.expectEqual(
            center_payload + 1,
            expectedRejectedPayload(odd_residue + center_payload_index + 2),
        );
        try testing.expectEqual(
            expectedCode(odd_residue + center_left_index) + 1,
            expectedCode(odd_residue + center_right_index),
        );
    }
}
