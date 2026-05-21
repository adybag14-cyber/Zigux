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

test "representative err-band quintets keep alias-err-alias-err-alias spacing exact" {
    const left_residues = [_]usize{ 0, 2, 1020, 2044, 3068, 4090 };

    for (left_residues) |left_residue| {
        const residues = [_]usize{
            left_residue,
            left_residue + 1,
            left_residue + 2,
            left_residue + 3,
            left_residue + 4,
        };

        var raws: [5]usize = undefined;
        var slots: [5]xarray_slot_view.SlotView = undefined;

        for (residues, 0..) |residue, idx| {
            raws[idx] = rawFromResidue(residue);
            slots[idx] = xarray_slot_view.fromRaw(raws[idx]);

            try testing.expect(slots[idx].isErr());
            try testing.expectEqual(@as(?isize, expectedCode(residue)), slots[idx].errorCode());
            try testing.expectEqual(@as(usize, (residue + 1) & 1), raws[idx] & xa_value.value_tag_mask);
        }

        try testing.expectEqual(raws[0] + 1, raws[1]);
        try testing.expectEqual(raws[1] + 1, raws[2]);
        try testing.expectEqual(raws[2] + 1, raws[3]);
        try testing.expectEqual(raws[3] + 1, raws[4]);

        try testing.expectEqual(
            @as(u128, raws[0]) + @as(u128, raws[4]),
            @as(u128, raws[2]) * 2,
        );
        try testing.expectEqual(
            @as(u128, raws[1]) + @as(u128, raws[3]),
            @as(u128, raws[2]) * 2,
        );

        const first_payload = expectedRejectedPayload(left_residue);
        const third_payload = expectedRejectedPayload(left_residue + 2);
        const fifth_payload = expectedRejectedPayload(left_residue + 4);
        try testing.expectEqual(first_payload + 1, third_payload);
        try testing.expectEqual(third_payload + 1, fifth_payload);
        try testing.expectEqual(raws[0], (first_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(raws[2], (third_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(raws[4], (fifth_payload << 1) | xa_value.value_tag_mask);
    }
}

test "every interior quintet keeps consecutive codes and alternating constructor families" {
    var even_residue: usize = 0;
    while (even_residue + 4 <= err_band_span) : (even_residue += 2) {
        const first_payload = expectedRejectedPayload(even_residue);
        const third_payload = expectedRejectedPayload(even_residue + 2);
        const fifth_payload = expectedRejectedPayload(even_residue + 4);

        const first_slot = xarray_slot_view.fromRaw(rawFromResidue(even_residue));
        const second_slot = xarray_slot_view.fromErrorCode(expectedCode(even_residue + 1));
        const third_slot = xarray_slot_view.fromRaw(rawFromResidue(even_residue + 2));
        const fourth_slot = xarray_slot_view.fromErrorCode(expectedCode(even_residue + 3));
        const fifth_slot = xarray_slot_view.fromRaw(rawFromResidue(even_residue + 4));

        try testing.expectEqual(rawFromResidue(even_residue), first_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 1), second_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 2), third_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 3), fourth_slot.rawValue());
        try testing.expectEqual(rawFromResidue(even_residue + 4), fifth_slot.rawValue());

        try testing.expectEqual(first_slot.errorCode().? + 1, second_slot.errorCode().?);
        try testing.expectEqual(second_slot.errorCode().? + 1, third_slot.errorCode().?);
        try testing.expectEqual(third_slot.errorCode().? + 1, fourth_slot.errorCode().?);
        try testing.expectEqual(fourth_slot.errorCode().? + 1, fifth_slot.errorCode().?);

        try testing.expect(!xa_value.canRepresent(first_payload));
        try testing.expect(!xa_value.canRepresent(third_payload));
        try testing.expect(!xa_value.canRepresent(fifth_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(first_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(third_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(fifth_payload));
    }
}

test "quintet windows preserve centered code and payload equations" {
    var even_residue: usize = 0;
    while (even_residue + 4 <= err_band_span) : (even_residue += 2) {
        const codes = [_]isize{
            expectedCode(even_residue),
            expectedCode(even_residue + 1),
            expectedCode(even_residue + 2),
            expectedCode(even_residue + 3),
            expectedCode(even_residue + 4),
        };

        const first_payload = expectedRejectedPayload(even_residue);
        const third_payload = expectedRejectedPayload(even_residue + 2);
        const fifth_payload = expectedRejectedPayload(even_residue + 4);

        try testing.expectEqual(codes[0] + codes[4], codes[2] * 2);
        try testing.expectEqual(codes[1] + codes[3], codes[2] * 2);
        try testing.expectEqual(first_payload + fifth_payload, third_payload * 2);
        try testing.expectEqual(first_payload + 2, fifth_payload);
        try testing.expectEqual(
            @as(u128, rawFromResidue(even_residue)) + @as(u128, rawFromResidue(even_residue + 4)),
            @as(u128, rawFromResidue(even_residue + 2)) * 2,
        );
        try testing.expectEqual(
            @as(u128, rawFromResidue(even_residue + 1)) + @as(u128, rawFromResidue(even_residue + 3)),
            @as(u128, rawFromResidue(even_residue + 2)) * 2,
        );
    }
}
