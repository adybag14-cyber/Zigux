const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn rejectedInlineRaw(offset: usize) usize {
    const payload = xa_value.safe_inline_limit + 1 + offset;
    return (payload << 1) | xa_value.value_tag_mask;
}

test "rejected inline payloads climb the odd err_ptr ladder in lockstep" {
    const start_code = -@as(isize, @intCast(err_ptr.max_errno));

    inline for (0..5) |offset| {
        const payload = xa_value.safe_inline_limit + 1 + offset;
        const raw = rejectedInlineRaw(offset);
        const slot = xarray_slot_view.fromRaw(raw);
        const expected_code = start_code + @as(isize, @intCast(offset * 2));

        try testing.expect(!xa_value.canRepresent(payload));
        try testing.expectEqual(err_ptr.err_floor + offset * 2, raw);
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "even err_ptr raws stay between adjacent rejected inline aliases" {
    const start_code = -@as(isize, @intCast(err_ptr.max_errno - 1));

    inline for (0..4) |offset| {
        const lower_alias_raw = rejectedInlineRaw(offset);
        const even_raw = lower_alias_raw + 1;
        const upper_alias_raw = rejectedInlineRaw(offset + 1);
        const slot = xarray_slot_view.fromRaw(even_raw);
        const expected_code = start_code + @as(isize, @intCast(offset * 2));

        try testing.expectEqual(lower_alias_raw + 1, even_raw);
        try testing.expectEqual(upper_alias_raw - 1, even_raw);
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect((even_raw & xa_value.value_tag_mask) == 0);
        try testing.expect(!xa_value.isValue(even_raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(even_raw));
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "rebuilding from aliased odd err_ptr codes reproduces the rejected raws exactly" {
    const start_code = -@as(isize, @intCast(err_ptr.max_errno));

    inline for (0..5) |offset| {
        const payload = xa_value.safe_inline_limit + 1 + offset;
        const expected_code = start_code + @as(isize, @intCast(offset * 2));
        const rebuilt = xarray_slot_view.fromErrorCode(expected_code);
        const raw = rejectedInlineRaw(offset);

        try testing.expectError(
            error.ValueWouldOverlapErrPtr,
            xarray_slot_view.fromValue(payload),
        );
        try testing.expectEqual(raw, rebuilt.rawValue());
        try testing.expectEqual(raw, err_ptr.fromErrorCode(expected_code));
        try testing.expectEqual(expected_code, err_ptr.toErrorCode(raw));
    }
}
