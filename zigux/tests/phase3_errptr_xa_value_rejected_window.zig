const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

fn rejectedValueCount() usize {
    return (err_ptr.max_errno + 1) / 2;
}

fn rejectedValueAt(offset: usize) usize {
    std.debug.assert(offset < rejectedValueCount());
    return xa_value.safe_inline_limit + 1 + offset;
}

fn aliasedRawAt(offset: usize) usize {
    return (rejectedValueAt(offset) << 1) | xa_value.value_tag_mask;
}

fn expectedErrorCodeAt(offset: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(offset * 2));
}

fn expectRejectedAlias(offset: usize) !void {
    const rejected_value = rejectedValueAt(offset);
    const raw = aliasedRawAt(offset);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expect(!xa_value.isValue(raw));
    try testing.expectEqual(xa_value.value_tag_mask, raw & xa_value.value_tag_mask);
    try testing.expectEqual(expectedErrorCodeAt(offset), err_ptr.toErrorCode(raw));
}

test "rejected xa_value window reaches the first and last tagged err_ptr raws" {
    const count = rejectedValueCount();
    const first_raw = aliasedRawAt(0);
    const last_raw = aliasedRawAt(count - 1);

    try testing.expectEqual(@as(usize, 2048), count);
    try testing.expectEqual(err_ptr.err_floor, first_raw);
    try testing.expectEqual(err_ptr.fromErrorCode(-1), last_raw);
    try testing.expectEqual(rejectedValueAt(count - 1), xa_value.safe_inline_limit + count);
    try expectRejectedAlias(0);
    try expectRejectedAlias(count - 1);
}

test "rejected xa_value aliases cover the tagged err_ptr band with stride-two spacing" {
    const count = rejectedValueCount();

    for (0..count) |offset| {
        const raw = aliasedRawAt(offset);

        try expectRejectedAlias(offset);
        try testing.expectEqual(err_ptr.err_floor + (offset * 2), raw);
    }
}

test "even err_ptr raws stay between rejected aliases and outside the xa_value lane" {
    const first_tagged_raw = aliasedRawAt(0);
    const second_tagged_raw = aliasedRawAt(1);
    const even_raw = first_tagged_raw + 1;

    try testing.expectEqual(first_tagged_raw + 2, second_tagged_raw);
    try testing.expect(err_ptr.isErrValue(even_raw));
    try testing.expect(!xa_value.isValue(even_raw));
    try testing.expectEqual(@as(usize, 0), even_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(isize, -4094), err_ptr.toErrorCode(even_raw));
}
