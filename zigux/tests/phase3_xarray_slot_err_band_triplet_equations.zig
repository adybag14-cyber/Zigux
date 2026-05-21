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

test "representative err-band triplets keep alias-err-alias spacing exact" {
    const left_residues = [_]usize{ 0, 2, 1022, 2046, 2048, 3070, 4092 };

    for (left_residues) |left_residue| {
        const middle_residue = left_residue + 1;
        const right_residue = left_residue + 2;

        const left_raw = rawFromResidue(left_residue);
        const middle_raw = rawFromResidue(middle_residue);
        const right_raw = rawFromResidue(right_residue);

        const left_payload = expectedRejectedPayload(left_residue);
        const right_payload = expectedRejectedPayload(right_residue);

        const left_slot = xarray_slot_view.fromRaw(left_raw);
        const middle_slot = xarray_slot_view.fromRaw(middle_raw);
        const right_slot = xarray_slot_view.fromRaw(right_raw);

        try testing.expect(left_slot.isErr());
        try testing.expect(middle_slot.isErr());
        try testing.expect(right_slot.isErr());

        try testing.expectEqual(@as(usize, 1), left_raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 0), middle_raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 1), right_raw & xa_value.value_tag_mask);

        try testing.expectEqual(left_raw + 1, middle_raw);
        try testing.expectEqual(middle_raw + 1, right_raw);
        try testing.expectEqual(left_raw + 2, right_raw);
        try testing.expectEqual(
            (@as(u128, middle_raw) * 2),
            (@as(u128, left_raw) + @as(u128, right_raw)),
        );

        try testing.expectEqual(left_raw, (left_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(right_raw, (right_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(left_payload + 1, right_payload);

        try testing.expectEqual(@as(?isize, expectedCode(left_residue)), left_slot.errorCode());
        try testing.expectEqual(@as(?isize, expectedCode(middle_residue)), middle_slot.errorCode());
        try testing.expectEqual(@as(?isize, expectedCode(right_residue)), right_slot.errorCode());
    }
}

test "every interior triplet keeps consecutive decoded error codes and rejected side payloads" {
    var even_residue: usize = 0;
    while (even_residue + 2 <= err_band_span) : (even_residue += 2) {
        const middle_residue = even_residue + 1;
        const right_residue = even_residue + 2;

        const left_raw = rawFromResidue(even_residue);
        const middle_raw = rawFromResidue(middle_residue);
        const right_raw = rawFromResidue(right_residue);

        const left_code = xarray_slot_view.fromRaw(left_raw).errorCode().?;
        const middle_code = xarray_slot_view.fromRaw(middle_raw).errorCode().?;
        const right_code = xarray_slot_view.fromRaw(right_raw).errorCode().?;

        const left_payload = expectedRejectedPayload(even_residue);
        const right_payload = expectedRejectedPayload(right_residue);

        try testing.expectEqual(left_code + 1, middle_code);
        try testing.expectEqual(middle_code + 1, right_code);
        try testing.expectEqual(expectedCode(middle_residue), middle_code);

        try testing.expectEqual(left_payload + 1, right_payload);
        try testing.expect(!xa_value.canRepresent(left_payload));
        try testing.expect(!xa_value.canRepresent(right_payload));
        try testing.expectEqual(left_raw, (left_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(right_raw, (right_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(middle_raw - left_raw, right_raw - middle_raw);
    }
}

test "triplet centers round-trip through fromErrorCode between rejected constructor payloads" {
    var even_residue: usize = 0;
    while (even_residue + 2 <= err_band_span) : (even_residue += 2) {
        const middle_residue = even_residue + 1;
        const middle_code = expectedCode(middle_residue);

        const left_payload = expectedRejectedPayload(even_residue);
        const right_payload = expectedRejectedPayload(even_residue + 2);

        const middle_slot = xarray_slot_view.fromErrorCode(middle_code);

        try testing.expectEqual(rawFromResidue(middle_residue), middle_slot.rawValue());
        try testing.expect(middle_slot.isErr());
        try testing.expectEqual(@as(?isize, middle_code), middle_slot.errorCode());

        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(left_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(right_payload));
    }
}
