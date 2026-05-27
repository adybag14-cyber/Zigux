const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const OddAliasCase = struct {
    raw: usize,
    expected_error: isize,
};

const EvenErrCase = struct {
    raw: usize,
    expected_error: isize,
};

fn rejectedValueForOddErrRaw(raw: usize) usize {
    return raw >> 1;
}

fn candidateValueForEvenErrRaw(raw: usize) usize {
    return raw >> 1;
}

fn encodedRaw(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

test "odd err-band raws decode as errs and have rejected xa_value constructor preimages" {
    const cases = [_]OddAliasCase{
        .{ .raw = err_ptr.err_floor, .expected_error = -4095 },
        .{ .raw = err_ptr.fromErrorCode(-2047), .expected_error = -2047 },
        .{ .raw = err_ptr.fromErrorCode(-1), .expected_error = -1 },
    };

    for (cases) |case| {
        const rejected_value = rejectedValueForOddErrRaw(case.raw);
        const slot = xarray_slot_view.fromRaw(case.raw);

        try testing.expect((case.raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(err_ptr.isErrValue(case.raw));
        try testing.expectEqual(case.expected_error, err_ptr.toErrorCode(case.raw));
        try testing.expect(!xa_value.canRepresent(rejected_value));
        try testing.expect(rejected_value > xa_value.safe_inline_limit);
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
        try testing.expectEqual(case.raw, encodedRaw(rejected_value));

        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expectEqual(@as(?isize, case.expected_error), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
    }
}

test "even err-band raws stay in the err lane but have no xa_value constructor preimage" {
    const cases = [_]EvenErrCase{
        .{ .raw = err_ptr.err_floor + 1, .expected_error = -4094 },
        .{ .raw = err_ptr.fromErrorCode(-2048), .expected_error = -2048 },
        .{ .raw = err_ptr.fromErrorCode(-2), .expected_error = -2 },
    };

    for (cases) |case| {
        const candidate_value = candidateValueForEvenErrRaw(case.raw);
        const candidate_raw = encodedRaw(candidate_value);
        const slot = xarray_slot_view.fromRaw(case.raw);

        try testing.expect((case.raw & xa_value.value_tag_mask) == 0);
        try testing.expect(err_ptr.isErrValue(case.raw));
        try testing.expectEqual(case.expected_error, err_ptr.toErrorCode(case.raw));
        try testing.expect(candidate_value > xa_value.safe_inline_limit);
        try testing.expect(!xa_value.canRepresent(candidate_value));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(candidate_value));
        try testing.expectEqual(case.raw + 1, candidate_raw);
        try testing.expect(candidate_raw <= err_ptr.fromErrorCode(-1));
        try testing.expectEqual(err_ptr.toErrorCode(case.raw) + 1, err_ptr.toErrorCode(candidate_raw));

        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expectEqual(@as(?isize, case.expected_error), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
    }
}

test "adjacent even and odd err raws share the same rejected-value quotient but only the odd raw is reachable" {
    const pairs = [_]usize{
        err_ptr.err_floor + 1,
        err_ptr.fromErrorCode(-2048),
        err_ptr.fromErrorCode(-2),
    };

    for (pairs) |even_raw| {
        const odd_neighbor = even_raw + 1;
        const even_candidate = candidateValueForEvenErrRaw(even_raw);
        const odd_candidate = rejectedValueForOddErrRaw(odd_neighbor);

        try testing.expect((even_raw & xa_value.value_tag_mask) == 0);
        try testing.expect((odd_neighbor & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expectEqual(even_candidate, odd_candidate);
        try testing.expectEqual(encodedRaw(even_candidate), odd_neighbor);
        try testing.expectEqual(err_ptr.toErrorCode(even_raw) + 1, err_ptr.toErrorCode(odd_neighbor));
        try testing.expectEqual(xarray_slot_view.SlotKind.err, xarray_slot_view.fromRaw(even_raw).kind());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, xarray_slot_view.fromRaw(odd_neighbor).kind());
    }
}
