const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_band_span = err_ptr.max_errno - 1;
const half_span = err_band_span / 2;
const rejected_payload_base = xa_value.safe_inline_limit + 1;

fn rawFromResidue(residue: usize) usize {
    std.debug.assert(residue <= err_band_span);
    return err_ptr.err_floor + residue;
}

fn mirroredResidue(residue: usize) usize {
    std.debug.assert(residue <= err_band_span);
    return err_band_span - residue;
}

fn expectedCode(residue: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(residue));
}

fn expectedRejectedPayload(residue: usize) usize {
    std.debug.assert((residue & 1) == 0);
    return rejected_payload_base + (residue >> 1);
}

test "representative err-band fold pairs keep edge distances and code sums exact" {
    const residues = [_]usize{ 0, 1, 2, 3, 1023, 1024, 1025, 1535, 1536, 2047 };
    const err_top = err_ptr.fromErrorCode(-1);

    for (residues) |low_residue| {
        const high_residue = mirroredResidue(low_residue);
        const low_raw = rawFromResidue(low_residue);
        const high_raw = rawFromResidue(high_residue);
        const low_code = expectedCode(low_residue);
        const high_code = expectedCode(high_residue);
        const low_slot = xarray_slot_view.fromRaw(low_raw);
        const high_slot = xarray_slot_view.fromRaw(high_raw);

        try testing.expect(low_slot.isErr());
        try testing.expect(high_slot.isErr());
        try testing.expectEqual(@as(?isize, low_code), low_slot.errorCode());
        try testing.expectEqual(@as(?isize, high_code), high_slot.errorCode());
        try testing.expectEqual(@as(isize, -4096), low_code + high_code);
        try testing.expectEqual(low_residue, low_raw - err_ptr.err_floor);
        try testing.expectEqual(low_residue, err_top - high_raw);
        try testing.expectEqual(high_residue - low_residue, high_raw - low_raw);
        try testing.expectEqual(low_raw & xa_value.value_tag_mask, high_raw & xa_value.value_tag_mask);
        try testing.expectEqual(low_residue & 1, high_residue & 1);
    }
}

test "folded even residues stay rejected aliases with a fixed payload-sum equation" {
    for (0..(half_span + 1)) |index| {
        const low_residue = index * 2;
        const high_residue = mirroredResidue(low_residue);
        const low_raw = rawFromResidue(low_residue);
        const high_raw = rawFromResidue(high_residue);
        const low_payload = expectedRejectedPayload(low_residue);
        const high_payload = expectedRejectedPayload(high_residue);

        try testing.expectEqual(@as(usize, 1), low_raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 1), high_raw & xa_value.value_tag_mask);
        try testing.expectEqual(low_raw, (low_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(high_raw, (high_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 2) * rejected_payload_base + half_span, low_payload + high_payload);
        try testing.expectEqual(@as(usize, 0), low_payload - rejected_payload_base - index);
        try testing.expectEqual(@as(usize, 0), high_payload - rejected_payload_base - (half_span - index));
        try testing.expect(!xa_value.canRepresent(low_payload));
        try testing.expect(!xa_value.canRepresent(high_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(low_payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(high_payload));
    }
}

test "folded odd residues stay direct err entries between mirrored rejected aliases" {
    for (0..half_span) |index| {
        const low_residue = (index * 2) + 1;
        const high_residue = mirroredResidue(low_residue);
        const low_raw = rawFromResidue(low_residue);
        const high_raw = rawFromResidue(high_residue);

        try testing.expectEqual(@as(usize, 0), low_raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 0), high_raw & xa_value.value_tag_mask);
        try testing.expectEqual(low_raw - 1, rawFromResidue(low_residue - 1));
        try testing.expectEqual(low_raw + 1, rawFromResidue(low_residue + 1));
        try testing.expectEqual(high_raw - 1, rawFromResidue(high_residue - 1));
        try testing.expectEqual(high_raw + 1, rawFromResidue(high_residue + 1));
        try testing.expectEqual(expectedCode(low_residue), xarray_slot_view.fromRaw(low_raw).errorCode().?);
        try testing.expectEqual(expectedCode(high_residue), xarray_slot_view.fromRaw(high_raw).errorCode().?);
        try testing.expectEqual(@as(isize, -4096), expectedCode(low_residue) + expectedCode(high_residue));
    }
}
