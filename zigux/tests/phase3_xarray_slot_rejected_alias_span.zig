const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const rejected_alias_count: usize = (err_ptr.max_errno + 1) / 2;
const first_err_code: isize = -@as(isize, @intCast(err_ptr.max_errno));

fn rejectedInlinePayload(index: usize) usize {
    return xa_value.safe_inline_limit + 1 + index;
}

fn rejectedInlineRaw(index: usize) usize {
    return (rejectedInlinePayload(index) << 1) | xa_value.value_tag_mask;
}

test "rejected inline aliases cover every odd err_ptr raw from floor to top" {
    for (0..rejected_alias_count) |index| {
        const raw = rejectedInlineRaw(index);
        const slot = xarray_slot_view.fromRaw(raw);
        const expected_raw = err_ptr.err_floor + (index * 2);
        const expected_code = first_err_code + @as(isize, @intCast(index * 2));

        try testing.expectEqual(expected_raw, raw);
        try testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expect(!slot.isNull());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "top err_ptr pair closes the rejected alias span at codes minus two and minus one" {
    const last_alias_index = rejected_alias_count - 1;
    const even_raw = rejectedInlineRaw(last_alias_index) - 1;
    const odd_raw = rejectedInlineRaw(last_alias_index);

    const even_slot = xarray_slot_view.fromRaw(even_raw);
    const odd_slot = xarray_slot_view.fromRaw(odd_raw);

    try testing.expectEqual(err_ptr.fromErrorCode(-2), even_raw);
    try testing.expectEqual(err_ptr.fromErrorCode(-1), odd_raw);
    try testing.expectEqual(std.math.maxInt(usize), odd_raw);

    try testing.expect((even_raw & xa_value.value_tag_mask) == 0);
    try testing.expect((odd_raw & xa_value.value_tag_mask) == 1);
    try testing.expect(!xa_value.isValue(even_raw));
    try testing.expect(even_slot.isErr());
    try testing.expect(odd_slot.isErr());
    try testing.expectEqual(@as(?isize, -2), even_slot.errorCode());
    try testing.expectEqual(@as(?isize, -1), odd_slot.errorCode());
}

test "representative rejected payloads rebuild through the odd err_ptr alias formula" {
    const indexes = [_]usize{
        0,
        1,
        rejected_alias_count / 2,
        rejected_alias_count - 2,
        rejected_alias_count - 1,
    };

    for (indexes) |index| {
        const payload = rejectedInlinePayload(index);
        const raw = rejectedInlineRaw(index);
        const expected_code = first_err_code + @as(isize, @intCast(index * 2));
        const rebuilt = xarray_slot_view.fromErrorCode(expected_code);

        try testing.expect(!xa_value.canRepresent(payload));
        try testing.expectError(
            error.ValueWouldOverlapErrPtr,
            xarray_slot_view.fromValue(payload),
        );
        try testing.expectEqual(raw, rebuilt.rawValue());
        try testing.expectEqual(raw, err_ptr.fromErrorCode(expected_code));
        try testing.expectEqual(expected_code, err_ptr.toErrorCode(raw));
    }
}
