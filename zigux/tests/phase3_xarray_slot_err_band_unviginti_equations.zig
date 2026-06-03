const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_band_span = err_ptr.max_errno - 1;
const rejected_payload_base = xa_value.safe_inline_limit + 1;
const window_width = 21;

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

test "representative err-band unvigintis keep the centered raw equation explicit" {
    const left_residues = [_]usize{ 0, 2, 1008, 2036, 3060, 4074 };

    for (left_residues) |left_residue| {
        var raws: [window_width]usize = undefined;
        var codes: [window_width]isize = undefined;

        for (&raws, &codes, 0..) |*raw, *code, idx| {
            const residue = left_residue + idx;
            const slot = xarray_slot_view.fromRaw(rawFromResidue(residue));

            raw.* = slot.rawValue();
            code.* = slot.errorCode().?;

            try testing.expect(slot.isErr());
            try testing.expect(!slot.isValue());
            try testing.expect(!slot.isPointer());
            try testing.expectEqual(@as(?isize, expectedCode(residue)), slot.errorCode());
            try testing.expectEqual(@as(?usize, null), slot.value());
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
            try testing.expectEqual(@as(usize, (residue + 1) & 1), raw.* & xa_value.value_tag_mask);
        }

        inline for (0..20) |idx| {
            try testing.expectEqual(raws[idx] + 1, raws[idx + 1]);
            try testing.expectEqual(codes[idx] + 1, codes[idx + 1]);
        }

        const center_raw = raws[10];
        const center_code = codes[10];
        inline for (0..10) |idx| {
            try testing.expectEqual(
                @as(u128, raws[idx]) + @as(u128, raws[20 - idx]),
                @as(u128, center_raw) * 2,
            );
            try testing.expectEqual(codes[idx] + codes[20 - idx], center_code * 2);
        }

        const center_payload = expectedRejectedPayload(left_residue + 10);
        try testing.expectEqual(center_raw, (center_payload << 1) | xa_value.value_tag_mask);
        try testing.expect(!xa_value.canRepresent(center_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(center_payload));
    }
}

test "every interior unviginti keeps alternating raw and constructor families" {
    var even_residue: usize = 0;
    while (even_residue + 20 <= err_band_span) : (even_residue += 2) {
        var slots: [window_width]xarray_slot_view.SlotView = undefined;

        for (&slots, 0..) |*slot, idx| {
            const residue = even_residue + idx;
            slot.* = if ((idx & 1) == 0)
                xarray_slot_view.fromRaw(rawFromResidue(residue))
            else
                xarray_slot_view.fromErrorCode(expectedCode(residue));

            try testing.expectEqual(rawFromResidue(residue), slot.rawValue());
            try testing.expectEqual(@as(?isize, expectedCode(residue)), slot.errorCode());
        }

        inline for (0..10) |payload_idx| {
            const residue = even_residue + (payload_idx * 2);
            const payload = expectedRejectedPayload(residue);
            const raw = rawFromResidue(residue);

            try testing.expectEqual(raw, (payload << 1) | xa_value.value_tag_mask);
            try testing.expect(!xa_value.canRepresent(payload));
            try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(payload));
        }

        const center_payload = expectedRejectedPayload(even_residue + 10);
        try testing.expectEqual(slots[10].rawValue(), (center_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(slots[10].errorCode().?, slots[0].errorCode().? + 10);
        try testing.expectEqual(slots[20].errorCode().?, slots[10].errorCode().? + 10);
    }
}

test "unviginti windows keep rejected payloads centered around the middle alias" {
    var even_residue: usize = 0;
    while (even_residue + 20 <= err_band_span) : (even_residue += 2) {
        const payloads = [_]usize{
            expectedRejectedPayload(even_residue),
            expectedRejectedPayload(even_residue + 2),
            expectedRejectedPayload(even_residue + 4),
            expectedRejectedPayload(even_residue + 6),
            expectedRejectedPayload(even_residue + 8),
            expectedRejectedPayload(even_residue + 10),
            expectedRejectedPayload(even_residue + 12),
            expectedRejectedPayload(even_residue + 14),
            expectedRejectedPayload(even_residue + 16),
            expectedRejectedPayload(even_residue + 18),
            expectedRejectedPayload(even_residue + 20),
        };

        inline for (0..10) |idx| {
            try testing.expectEqual(payloads[idx] + 1, payloads[idx + 1]);
            try testing.expectEqual(payloads[idx] + payloads[10 - idx], payloads[5] * 2);
        }

        try testing.expectEqual(payloads[0] + 5, payloads[5]);
        try testing.expectEqual(payloads[5] + 5, payloads[10]);
        try testing.expectEqual(rawFromResidue(even_residue + 10), (payloads[5] << 1) | xa_value.value_tag_mask);
    }
}
