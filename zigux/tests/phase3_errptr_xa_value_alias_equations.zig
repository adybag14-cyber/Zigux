const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

const rejected_alias_count: usize = (err_ptr.max_errno + 1) / 2;
const first_rejected_value: usize = xa_value.safe_inline_limit + 1;
const top_tagged_err_raw: usize = err_ptr.fromErrorCode(-1);

fn aliasValue(index: usize) usize {
    std.debug.assert(index < rejected_alias_count);
    return first_rejected_value + index;
}

fn aliasRaw(index: usize) usize {
    return (aliasValue(index) << 1) | xa_value.value_tag_mask;
}

fn aliasErrorCode(index: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(index * 2));
}

test "rejected xa_value aliases obey the same raw and error-code equations across the band" {
    const samples = [_]usize{
        0,
        1,
        rejected_alias_count / 2,
        rejected_alias_count - 2,
        rejected_alias_count - 1,
    };

    for (samples) |index| {
        const raw = aliasRaw(index);

        try testing.expectEqual(err_ptr.err_floor + (index * 2), raw);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expectEqual(aliasErrorCode(index), err_ptr.toErrorCode(raw));
        try testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
    }
}

test "rejected aliases cover the tagged half of the err_ptr band exactly once" {
    var index: usize = 0;
    var previous_raw: ?usize = null;

    while (index < rejected_alias_count) : (index += 1) {
        const raw = aliasRaw(index);

        if (previous_raw) |prior| {
            try testing.expectEqual(prior + 2, raw);
        }
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        previous_raw = raw;
    }

    try testing.expectEqual(err_ptr.err_floor, aliasRaw(0));
    try testing.expectEqual(top_tagged_err_raw, aliasRaw(rejected_alias_count - 1));
}

test "interleaved even err_ptr raws stay between neighboring rejected aliases" {
    const samples = [_]usize{ 0, 1, rejected_alias_count / 2, rejected_alias_count - 2 };

    for (samples) |index| {
        const low_alias = aliasRaw(index);
        const even_raw = low_alias + 1;
        const high_alias = aliasRaw(index + 1);

        try testing.expectEqual(low_alias + 1, even_raw);
        try testing.expectEqual(even_raw + 1, high_alias);
        try testing.expect(err_ptr.isErrValue(even_raw));
        try testing.expect(!xa_value.isValue(even_raw));
        try testing.expectEqual(@as(usize, 0), even_raw & xa_value.value_tag_mask);
        try testing.expectEqual(aliasErrorCode(index) + 1, err_ptr.toErrorCode(even_raw));
    }
}
