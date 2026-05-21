const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_band_span = err_ptr.max_errno - 1;
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

test "representative err-band sexdecets keep alias-err spacing exact" {
    const left_residues = [_]usize{ 0, 2, 1016, 2044, 3060, 4078 };

    for (left_residues) |left_residue| {
        const residues = [_]usize{
            left_residue,
            left_residue + 1,
            left_residue + 2,
            left_residue + 3,
            left_residue + 4,
            left_residue + 5,
            left_residue + 6,
            left_residue + 7,
            left_residue + 8,
            left_residue + 9,
            left_residue + 10,
            left_residue + 11,
            left_residue + 12,
            left_residue + 13,
            left_residue + 14,
            left_residue + 15,
        };

        var raws: [16]usize = undefined;
        var slots: [16]xarray_slot_view.SlotView = undefined;

        for (residues, 0..) |residue, idx| {
            raws[idx] = rawFromResidue(residue);
            slots[idx] = xarray_slot_view.fromRaw(raws[idx]);

            try testing.expect(slots[idx].isErr());
            try testing.expectEqual(@as(?isize, expectedCode(residue)), slots[idx].errorCode());
            try testing.expectEqual(@as(usize, (residue + 1) & 1), raws[idx] & xa_value.value_tag_mask);
        }

        inline for (0..15) |idx| {
            try testing.expectEqual(raws[idx] + 1, raws[idx + 1]);
        }

        const sum_015 = @as(u128, raws[0]) + @as(u128, raws[15]);
        const sum_114 = @as(u128, raws[1]) + @as(u128, raws[14]);
        const sum_213 = @as(u128, raws[2]) + @as(u128, raws[13]);
        const sum_312 = @as(u128, raws[3]) + @as(u128, raws[12]);
        const sum_411 = @as(u128, raws[4]) + @as(u128, raws[11]);
        const sum_510 = @as(u128, raws[5]) + @as(u128, raws[10]);
        const sum_69 = @as(u128, raws[6]) + @as(u128, raws[9]);
        const sum_78 = @as(u128, raws[7]) + @as(u128, raws[8]);
        try testing.expectEqual(sum_015, sum_114);
        try testing.expectEqual(sum_114, sum_213);
        try testing.expectEqual(sum_213, sum_312);
        try testing.expectEqual(sum_312, sum_411);
        try testing.expectEqual(sum_411, sum_510);
        try testing.expectEqual(sum_510, sum_69);
        try testing.expectEqual(sum_69, sum_78);

        const first_payload = expectedRejectedPayload(left_residue);
        const third_payload = expectedRejectedPayload(left_residue + 2);
        const fifth_payload = expectedRejectedPayload(left_residue + 4);
        const seventh_payload = expectedRejectedPayload(left_residue + 6);
        const ninth_payload = expectedRejectedPayload(left_residue + 8);
        const eleventh_payload = expectedRejectedPayload(left_residue + 10);
        const thirteenth_payload = expectedRejectedPayload(left_residue + 12);
        const fifteenth_payload = expectedRejectedPayload(left_residue + 14);
        try testing.expectEqual(first_payload + 1, third_payload);
        try testing.expectEqual(third_payload + 1, fifth_payload);
        try testing.expectEqual(fifth_payload + 1, seventh_payload);
        try testing.expectEqual(seventh_payload + 1, ninth_payload);
        try testing.expectEqual(ninth_payload + 1, eleventh_payload);
        try testing.expectEqual(eleventh_payload + 1, thirteenth_payload);
        try testing.expectEqual(thirteenth_payload + 1, fifteenth_payload);
        try testing.expectEqual(first_payload + fifteenth_payload, third_payload + thirteenth_payload);
        try testing.expectEqual(third_payload + thirteenth_payload, fifth_payload + eleventh_payload);
        try testing.expectEqual(fifth_payload + eleventh_payload, seventh_payload + ninth_payload);
        try testing.expectEqual(raws[0], (first_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(raws[2], (third_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(raws[4], (fifth_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(raws[6], (seventh_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(raws[8], (ninth_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(raws[10], (eleventh_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(raws[12], (thirteenth_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(raws[14], (fifteenth_payload << 1) | xa_value.value_tag_mask);
    }
}

test "every interior sexdecet keeps consecutive codes and alternating constructor families" {
    var even_residue: usize = 0;
    while (even_residue + 15 <= err_band_span) : (even_residue += 2) {
        const first_payload = expectedRejectedPayload(even_residue);
        const third_payload = expectedRejectedPayload(even_residue + 2);
        const fifth_payload = expectedRejectedPayload(even_residue + 4);
        const seventh_payload = expectedRejectedPayload(even_residue + 6);
        const ninth_payload = expectedRejectedPayload(even_residue + 8);
        const eleventh_payload = expectedRejectedPayload(even_residue + 10);
        const thirteenth_payload = expectedRejectedPayload(even_residue + 12);
        const fifteenth_payload = expectedRejectedPayload(even_residue + 14);

        const first_slot = xarray_slot_view.fromRaw(rawFromResidue(even_residue));
        const second_slot = xarray_slot_view.fromErrorCode(expectedCode(even_residue + 1));
        const third_slot = xarray_slot_view.fromRaw(rawFromResidue(even_residue + 2));
        const fourth_slot = xarray_slot_view.fromErrorCode(expectedCode(even_residue + 3));
        const fifth_slot = xarray_slot_view.fromRaw(rawFromResidue(even_residue + 4));
        const sixth_slot = xarray_slot_view.fromErrorCode(expectedCode(even_residue + 5));
        const seventh_slot = xarray_slot_view.fromRaw(rawFromResidue(even_residue + 6));
        const eighth_slot = xarray_slot_view.fromErrorCode(expectedCode(even_residue + 7));
        const ninth_slot = xarray_slot_view.fromRaw(rawFromResidue(even_residue + 8));
        const tenth_slot = xarray_slot_view.fromErrorCode(expectedCode(even_residue + 9));
        const eleventh_slot = xarray_slot_view.fromRaw(rawFromResidue(even_residue + 10));
        const twelfth_slot = xarray_slot_view.fromErrorCode(expectedCode(even_residue + 11));
        const thirteenth_slot = xarray_slot_view.fromRaw(rawFromResidue(even_residue + 12));
        const fourteenth_slot = xarray_slot_view.fromErrorCode(expectedCode(even_residue + 13));
        const fifteenth_slot = xarray_slot_view.fromRaw(rawFromResidue(even_residue + 14));
        const sixteenth_slot = xarray_slot_view.fromErrorCode(expectedCode(even_residue + 15));

        try testing.expectEqual(rawFromResidue(even_residue), first_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 1), second_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 2), third_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 3), fourth_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 4), fifth_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 5), sixth_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 6), seventh_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 7), eighth_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 8), ninth_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 9), tenth_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 10), eleventh_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 11), twelfth_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 12), thirteenth_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 13), fourteenth_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 14), fifteenth_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 15), sixteenth_slot.rawValue());

        try testing.expectEqual(first_slot.errorCode().? + 1, second_slot.errorCode().?);
        try testing.expectEqual(second_slot.errorCode().? + 1, third_slot.errorCode().?);
        try testing.expectEqual(third_slot.errorCode().? + 1, fourth_slot.errorCode().?);
        try testing.expectEqual(fourth_slot.errorCode().? + 1, fifth_slot.errorCode().?);
        try testing.expectEqual(fifth_slot.errorCode().? + 1, sixth_slot.errorCode().?);
        try testing.expectEqual(sixth_slot.errorCode().? + 1, seventh_slot.errorCode().?);
        try testing.expectEqual(seventh_slot.errorCode().? + 1, eighth_slot.errorCode().?);
        try testing.expectEqual(eighth_slot.errorCode().? + 1, ninth_slot.errorCode().?);
        try testing.expectEqual(ninth_slot.errorCode().? + 1, tenth_slot.errorCode().?);
        try testing.expectEqual(tenth_slot.errorCode().? + 1, eleventh_slot.errorCode().?);
        try testing.expectEqual(eleventh_slot.errorCode().? + 1, twelfth_slot.errorCode().?);
        try testing.expectEqual(twelfth_slot.errorCode().? + 1, thirteenth_slot.errorCode().?);
        try testing.expectEqual(thirteenth_slot.errorCode().? + 1, fourteenth_slot.errorCode().?);
        try testing.expectEqual(fourteenth_slot.errorCode().? + 1, fifteenth_slot.errorCode().?);
        try testing.expectEqual(fifteenth_slot.errorCode().? + 1, sixteenth_slot.errorCode().?);

        try testing.expect(!xa_value.canRepresent(first_payload));
        try testing.expect(!xa_value.canRepresent(third_payload));
        try testing.expect(!xa_value.canRepresent(fifth_payload));
        try testing.expect(!xa_value.canRepresent(seventh_payload));
        try testing.expect(!xa_value.canRepresent(ninth_payload));
        try testing.expect(!xa_value.canRepresent(eleventh_payload));
        try testing.expect(!xa_value.canRepresent(thirteenth_payload));
        try testing.expect(!xa_value.canRepresent(fifteenth_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(first_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(third_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(fifth_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(seventh_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(ninth_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(eleventh_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(thirteenth_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(fifteenth_payload));
    }
}

test "sexdecet windows preserve centered equations across the middle seam" {
    var even_residue: usize = 0;
    while (even_residue + 15 <= err_band_span) : (even_residue += 2) {
        const codes = [_]isize{
            expectedCode(even_residue),
            expectedCode(even_residue + 1),
            expectedCode(even_residue + 2),
            expectedCode(even_residue + 3),
            expectedCode(even_residue + 4),
            expectedCode(even_residue + 5),
            expectedCode(even_residue + 6),
            expectedCode(even_residue + 7),
            expectedCode(even_residue + 8),
            expectedCode(even_residue + 9),
            expectedCode(even_residue + 10),
            expectedCode(even_residue + 11),
            expectedCode(even_residue + 12),
            expectedCode(even_residue + 13),
            expectedCode(even_residue + 14),
            expectedCode(even_residue + 15),
        };

        const first_payload = expectedRejectedPayload(even_residue);
        const third_payload = expectedRejectedPayload(even_residue + 2);
        const fifth_payload = expectedRejectedPayload(even_residue + 4);
        const seventh_payload = expectedRejectedPayload(even_residue + 6);
        const ninth_payload = expectedRejectedPayload(even_residue + 8);
        const eleventh_payload = expectedRejectedPayload(even_residue + 10);
        const thirteenth_payload = expectedRejectedPayload(even_residue + 12);
        const fifteenth_payload = expectedRejectedPayload(even_residue + 14);

        try testing.expectEqual(codes[0] + codes[15], codes[1] + codes[14]);
        try testing.expectEqual(codes[1] + codes[14], codes[2] + codes[13]);
        try testing.expectEqual(codes[2] + codes[13], codes[3] + codes[12]);
        try testing.expectEqual(codes[3] + codes[12], codes[4] + codes[11]);
        try testing.expectEqual(codes[4] + codes[11], codes[5] + codes[10]);
        try testing.expectEqual(codes[5] + codes[10], codes[6] + codes[9]);
        try testing.expectEqual(codes[6] + codes[9], codes[7] + codes[8]);
        try testing.expectEqual(first_payload + fifteenth_payload, third_payload + thirteenth_payload);
        try testing.expectEqual(third_payload + thirteenth_payload, fifth_payload + eleventh_payload);
        try testing.expectEqual(fifth_payload + eleventh_payload, seventh_payload + ninth_payload);
        try testing.expectEqual(first_payload + 7, fifteenth_payload);
        try testing.expectEqual(
            @as(u128, rawFromResidue(even_residue)) + @as(u128, rawFromResidue(even_residue + 15)),
            @as(u128, rawFromResidue(even_residue + 1)) + @as(u128, rawFromResidue(even_residue + 14)),
        );
        try testing.expectEqual(
            @as(u128, rawFromResidue(even_residue + 1)) + @as(u128, rawFromResidue(even_residue + 14)),
            @as(u128, rawFromResidue(even_residue + 2)) + @as(u128, rawFromResidue(even_residue + 13)),
        );
        try testing.expectEqual(
            @as(u128, rawFromResidue(even_residue + 2)) + @as(u128, rawFromResidue(even_residue + 13)),
            @as(u128, rawFromResidue(even_residue + 3)) + @as(u128, rawFromResidue(even_residue + 12)),
        );
        try testing.expectEqual(
            @as(u128, rawFromResidue(even_residue + 3)) + @as(u128, rawFromResidue(even_residue + 12)),
            @as(u128, rawFromResidue(even_residue + 4)) + @as(u128, rawFromResidue(even_residue + 11)),
        );
        try testing.expectEqual(
            @as(u128, rawFromResidue(even_residue + 4)) + @as(u128, rawFromResidue(even_residue + 11)),
            @as(u128, rawFromResidue(even_residue + 5)) + @as(u128, rawFromResidue(even_residue + 10)),
        );
        try testing.expectEqual(
            @as(u128, rawFromResidue(even_residue + 5)) + @as(u128, rawFromResidue(even_residue + 10)),
            @as(u128, rawFromResidue(even_residue + 6)) + @as(u128, rawFromResidue(even_residue + 9)),
        );
        try testing.expectEqual(
            @as(u128, rawFromResidue(even_residue + 6)) + @as(u128, rawFromResidue(even_residue + 9)),
            @as(u128, rawFromResidue(even_residue + 7)) + @as(u128, rawFromResidue(even_residue + 8)),
        );
    }
}
