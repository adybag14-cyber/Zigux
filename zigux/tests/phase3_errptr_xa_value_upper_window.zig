const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

fn acceptedWindowStart() usize {
    return xa_value.safe_inline_limit - 3;
}

fn acceptedValueAt(offset: usize) usize {
    std.debug.assert(offset < 4);
    return acceptedWindowStart() + offset;
}

fn rejectedValueAt(offset: usize) usize {
    std.debug.assert(offset < 3);
    return xa_value.safe_inline_limit + 1 + offset;
}

test "top accepted xa_value window stays packed directly below the pointer gap" {
    const gap_raw = err_ptr.err_floor - 1;
    var previous_raw: ?usize = null;

    for (0..4) |offset| {
        const value = acceptedValueAt(offset);
        const raw = try xa_value.makeValue(value);

        try testing.expectEqual(value, xa_value.toValue(raw));
        try testing.expect(xa_value.isValue(raw));
        try testing.expect(!err_ptr.isErrValue(raw));

        if (previous_raw) |prior| {
            try testing.expectEqual(prior + 2, raw);
        }
        previous_raw = raw;
    }

    const highest_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    try testing.expectEqual(gap_raw - 1, highest_raw);
    try testing.expect(!xa_value.isValue(gap_raw));
    try testing.expect(err_ptr.isOkValue(gap_raw));
}

test "first rejected tagged xa_values land on alternating err_ptr raws" {
    for (0..3) |offset| {
        const rejected_value = rejectedValueAt(offset);
        const rejected_raw = (rejected_value << 1) | xa_value.value_tag_mask;
        const even_err_raw = rejected_raw + 1;
        const expected_tagged_code = -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(offset * 2));
        const expected_even_code = expected_tagged_code + 1;

        try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
        try testing.expect(err_ptr.isErrValue(rejected_raw));
        try testing.expect(!xa_value.isValue(rejected_raw));
        try testing.expectEqual(xa_value.value_tag_mask, rejected_raw & xa_value.value_tag_mask);
        try testing.expectEqual(expected_tagged_code, err_ptr.toErrorCode(rejected_raw));

        try testing.expect(err_ptr.isErrValue(even_err_raw));
        try testing.expect(!xa_value.isValue(even_err_raw));
        try testing.expectEqual(@as(usize, 0), even_err_raw & xa_value.value_tag_mask);
        try testing.expectEqual(expected_even_code, err_ptr.toErrorCode(even_err_raw));
    }
}
