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

fn expectedRejectedPayload(residue: usize) usize {
    std.debug.assert((residue & 1) == 0);
    return rejected_payload_base + (residue >> 1);
}

test "representative err-band residues keep the raw-to-code equations exact" {
    const residues = [_]usize{ 0, 1, 2, 3, 1023, 1024, 1025, 2047, 2048, 2049, 4092, 4093, 4094 };

    for (residues) |residue| {
        const raw = rawFromResidue(residue);
        const code = expectedCode(residue);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(slot.isErr());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(raw, xarray_slot_view.fromErrorCode(code).rawValue());
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

        if ((residue & 1) == 1) {
            try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
        } else {
            const payload = expectedRejectedPayload(residue);
            try testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
            try testing.expectEqual(raw, (payload << 1) | xa_value.value_tag_mask);
            try testing.expectEqual(payload, raw >> 1);
            try testing.expect(!xa_value.canRepresent(payload));
            try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(payload));
        }
    }
}

test "even err-band residues follow the rejected-payload affine equations" {
    for (0..(err_ptr.max_errno / 2)) |index| {
        const residue = index * 2;
        const raw = rawFromResidue(residue);
        const code = expectedCode(residue);
        const payload = expectedRejectedPayload(residue);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(slot.isErr());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(raw, (payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(payload, raw >> 1);
        try testing.expectEqual(rejected_payload_base + index, payload);
        try testing.expectEqual(err_ptr.err_floor + residue, raw);
        try testing.expect(!xa_value.canRepresent(payload));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(payload));
    }

    try testing.expectEqual(err_ptr.err_floor, rawFromResidue(0));
    try testing.expectEqual(err_ptr.fromErrorCode(-1), rawFromResidue(err_band_span));
}

test "odd interior err-band residues stay direct err entries between consecutive rejected aliases" {
    for (1..(err_ptr.max_errno / 2)) |index| {
        const residue = (index * 2) - 1;
        const raw = rawFromResidue(residue);
        const low_raw = raw - 1;
        const high_raw = raw + 1;
        const code = expectedCode(residue);
        const low_payload = expectedRejectedPayload(residue - 1);
        const high_payload = expectedRejectedPayload(residue + 1);

        try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 1), low_raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 1), high_raw & xa_value.value_tag_mask);

        try testing.expectEqual(@as(?isize, code), xarray_slot_view.fromRaw(raw).errorCode());
        try testing.expectEqual(low_raw, (low_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(high_raw, (high_payload << 1) | xa_value.value_tag_mask);
        try testing.expectEqual(low_payload + 1, high_payload);
        try testing.expectEqual(low_raw + 1, raw);
        try testing.expectEqual(raw + 1, high_raw);
        try testing.expectEqual(@as(isize, 1), expectedCode(residue + 1) - code);
        try testing.expectEqual(@as(isize, 1), code - expectedCode(residue - 1));
        try testing.expect(!xa_value.canRepresent(low_payload));
        try testing.expect(!xa_value.canRepresent(high_payload));
    }
}
