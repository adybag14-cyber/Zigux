const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

fn rejectedValueRaw(offset: usize) usize {
    const rejected_value = xa_value.safe_inline_limit + 1 + offset;
    return (rejected_value << 1) | xa_value.value_tag_mask;
}

test "tagged rejected sequence walks odd err_ptr raws in order" {
    const tagged_err_count = (err_ptr.max_errno + 1) / 2;
    var previous_raw: ?usize = null;

    for (0..tagged_err_count) |offset| {
        const raw = rejectedValueRaw(offset);

        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expectEqual(xa_value.value_tag_mask, raw & xa_value.value_tag_mask);
        try testing.expectEqual(err_ptr.err_floor + (offset * 2), raw);
        try testing.expectEqual(-@as(isize, @intCast(err_ptr.max_errno - (offset * 2))), err_ptr.toErrorCode(raw));

        if (previous_raw) |prev| {
            try testing.expectEqual(prev + 2, raw);
        }
        previous_raw = raw;
    }
}

test "interleaved even err_ptr raws stay in-band but never decode as xa_values" {
    const sample_offsets = [_]usize{ 0, 1, 2, 2046 };

    for (sample_offsets) |offset| {
        const raw = rejectedValueRaw(offset) + 1;

        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
        try testing.expectEqual(err_ptr.err_floor + (offset * 2) + 1, raw);
        try testing.expectEqual(
            -@as(isize, @intCast(err_ptr.max_errno - ((offset * 2) + 1))),
            err_ptr.toErrorCode(raw),
        );
    }
}

test "last tagged rejected value lands on the top err_ptr raw" {
    const tagged_err_count = (err_ptr.max_errno + 1) / 2;
    const raw = rejectedValueRaw(tagged_err_count - 1);

    try testing.expectEqual(err_ptr.fromErrorCode(-1), raw);
    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expect(!xa_value.isValue(raw));
    try testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(raw));
}

test "next rejected value wraps back to inline zero raw" {
    const tagged_err_count = (err_ptr.max_errno + 1) / 2;
    const raw = rejectedValueRaw(tagged_err_count);

    try testing.expectEqual(try xa_value.makeValue(0), raw);
    try testing.expect(!err_ptr.isErrValue(raw));
    try testing.expect(xa_value.isValue(raw));
    try testing.expectEqual(@as(usize, 0), xa_value.toValue(raw));
}
