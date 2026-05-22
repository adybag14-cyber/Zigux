const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "tagged odd raws stay xa_values until the err_ptr cutoff" {
    const accepted = [_]struct { raw: usize, value: usize }{
        .{ .raw = err_ptr.err_floor - 4, .value = xa_value.safe_inline_limit - 1 },
        .{ .raw = err_ptr.err_floor - 2, .value = xa_value.safe_inline_limit },
    };

    for (accepted) |entry| {
        const slot = xarray_slot_view.fromRaw(entry.raw);

        try testing.expect((entry.raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(entry.raw));
        try testing.expect(xa_value.isValue(entry.raw));
        try testing.expect(!err_ptr.isErrValue(entry.raw));
        try testing.expect(slot.isValue());
        try testing.expect(!slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?usize, entry.value), slot.value());
        try testing.expectEqual(@as(?isize, null), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "tagged odd raws flip into err aliases exactly at the cutoff" {
    const rejected = [_]struct { raw: usize, error_code: isize }{
        .{ .raw = err_ptr.err_floor, .error_code = -4095 },
        .{ .raw = err_ptr.err_floor + 2, .error_code = -4093 },
        .{ .raw = err_ptr.err_floor + 4, .error_code = -4091 },
    };

    for (rejected) |entry| {
        const slot = xarray_slot_view.fromRaw(entry.raw);

        try testing.expect((entry.raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(entry.raw));
        try testing.expect(!xa_value.isValue(entry.raw));
        try testing.expect(err_ptr.isErrValue(entry.raw));
        try testing.expect(!slot.isValue());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?isize, entry.error_code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "rejected tagged odd raws still reconstruct their overlapping inline payloads" {
    const overlapping_values = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        xa_value.safe_inline_limit + 3,
    };

    for (overlapping_values, 0..) |overlapping_value, index| {
        const raw = (overlapping_value << 1) | xa_value.value_tag_mask;
        const slot = xarray_slot_view.fromRaw(raw);
        const expected_error = -@as(isize, 4095) + @as(isize, @intCast(index * 2));

        try testing.expectEqual(raw, err_ptr.fromErrorCode(expected_error));
        try testing.expectEqual(overlapping_value, raw >> 1);
        try testing.expect(!xa_value.canRepresent(overlapping_value));
        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
        try testing.expect(slot.isErr());
        try testing.expectEqual(@as(?isize, expected_error), slot.errorCode());
    }
}
