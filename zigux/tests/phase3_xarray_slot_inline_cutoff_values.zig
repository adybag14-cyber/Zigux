const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const InlineCase = struct {
    value: usize,
    representable: bool,
    expected_kind: xarray_slot_view.SlotKind,
    expected_error: ?isize,
};

fn inlineCandidateRaw(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

fn buildInlineCases() [5]InlineCase {
    return .{
        .{
            .value = xa_value.safe_inline_limit - 1,
            .representable = true,
            .expected_kind = .value,
            .expected_error = null,
        },
        .{
            .value = xa_value.safe_inline_limit,
            .representable = true,
            .expected_kind = .value,
            .expected_error = null,
        },
        .{
            .value = xa_value.safe_inline_limit + 1,
            .representable = false,
            .expected_kind = .err,
            .expected_error = -4095,
        },
        .{
            .value = xa_value.safe_inline_limit + 2,
            .representable = false,
            .expected_kind = .err,
            .expected_error = -4093,
        },
        .{
            .value = xa_value.safe_inline_limit + 3,
            .representable = false,
            .expected_kind = .err,
            .expected_error = -4091,
        },
    };
}

test "inline source values partition cleanly across the cutoff" {
    const cases = buildInlineCases();

    for (cases) |case| {
        const raw = inlineCandidateRaw(case.value);
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(case.representable, xa_value.canRepresent(case.value));
        try testing.expectEqual(case.expected_kind, slot.kind());
        try testing.expect(!slot.isNull());
        try testing.expectEqual(case.expected_kind == .value, slot.isValue());
        try testing.expectEqual(case.expected_kind == .err, slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(raw, slot.rawValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

        if (case.representable) {
            const encoded = try xa_value.makeValue(case.value);
            try testing.expectEqual(raw, encoded);
            try testing.expect(xa_value.isValue(raw));
            try testing.expect(!err_ptr.isErrValue(raw));
            try testing.expectEqual(@as(?usize, case.value), slot.value());
            try testing.expectEqual(@as(?isize, null), slot.errorCode());
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        } else {
            try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(case.value));
            try testing.expect(!xa_value.isValue(raw));
            try testing.expect(err_ptr.isErrValue(raw));
            try testing.expectEqual(@as(?usize, null), slot.value());
            try testing.expectEqual(case.expected_error, slot.errorCode());
            try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        }
    }
}

test "inline candidate raws stay exact as representable values turn into err_ptr encodings" {
    const accepted_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const first_rejected_raw = inlineCandidateRaw(xa_value.safe_inline_limit + 1);
    const second_rejected_raw = inlineCandidateRaw(xa_value.safe_inline_limit + 2);
    const third_rejected_raw = inlineCandidateRaw(xa_value.safe_inline_limit + 3);
    const gap_before_err = err_ptr.err_floor - 1;

    try testing.expectEqual(err_ptr.err_floor - 2, accepted_limit_raw);
    try testing.expectEqual(err_ptr.err_floor, first_rejected_raw);
    try testing.expectEqual(err_ptr.err_floor + 2, second_rejected_raw);
    try testing.expectEqual(err_ptr.err_floor + 4, third_rejected_raw);

    try testing.expectEqual(@as(usize, 2), first_rejected_raw - accepted_limit_raw);
    try testing.expectEqual(@as(usize, 2), second_rejected_raw - first_rejected_raw);
    try testing.expectEqual(@as(usize, 2), third_rejected_raw - second_rejected_raw);

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, xarray_slot_view.fromRaw(gap_before_err).kind());
    try testing.expectEqual(@as(?usize, gap_before_err), xarray_slot_view.fromRaw(gap_before_err).pointerValue());
    try testing.expectEqual(@as(usize, 1), gap_before_err - accepted_limit_raw);
    try testing.expectEqual(@as(usize, 1), first_rejected_raw - gap_before_err);
}

test "rejected inline values reopen only as err_ptr and keep value decoding closed" {
    const rejected_values = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        xa_value.safe_inline_limit + 3,
        xa_value.safe_inline_limit + 4,
    };

    for (rejected_values, 0..) |value, index| {
        const raw = inlineCandidateRaw(value);
        const slot = xarray_slot_view.fromRaw(raw);
        const expected_error = -@as(isize, 4095) + @as(isize, @intCast(index * 2));

        try testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(value));
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expectEqual(@as(?isize, expected_error), slot.errorCode());
    }
}
