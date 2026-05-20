const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

const Kind = enum {
    null_value,
    pointer_like,
    xa_value,
    err_ptr,
};

const Case = struct {
    name: []const u8,
    raw: usize,
    kind: Kind,
    decoded_value: ?usize = null,
    decoded_error: ?isize = null,
};

fn classify(raw: usize) Kind {
    if (raw == 0) {
        return .null_value;
    }
    if (xa_value.isValue(raw)) {
        return .xa_value;
    }
    if (err_ptr.isErrValue(raw)) {
        return .err_ptr;
    }
    return .pointer_like;
}

fn representativeCases() ![9]Case {
    return .{
        .{ .name = "null", .raw = 0, .kind = .null_value },
        .{ .name = "inline_zero", .raw = try xa_value.makeValue(0), .kind = .xa_value, .decoded_value = 0 },
        .{ .name = "inline_small", .raw = try xa_value.makeValue(29), .kind = .xa_value, .decoded_value = 29 },
        .{ .name = "pointer_gap_low", .raw = 2, .kind = .pointer_like },
        .{
            .name = "inline_limit",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .xa_value,
            .decoded_value = xa_value.safe_inline_limit,
        },
        .{ .name = "gap_before_err_floor", .raw = err_ptr.err_floor - 1, .kind = .pointer_like },
        .{ .name = "err_floor", .raw = err_ptr.err_floor, .kind = .err_ptr, .decoded_error = -4095 },
        .{ .name = "err_next", .raw = err_ptr.err_floor + 1, .kind = .err_ptr, .decoded_error = -4094 },
        .{ .name = "err_top", .raw = err_ptr.fromErrorCode(-1), .kind = .err_ptr, .decoded_error = -1 },
    };
}

test "representative raws stay in exactly one lane" {
    const cases = try representativeCases();

    for (cases) |case| {
        const is_null = case.raw == 0;
        const is_value = xa_value.isValue(case.raw);
        const is_err = err_ptr.isErrValue(case.raw);
        const match_count: usize =
            @intFromBool(is_null) +
            @intFromBool(is_value) +
            @intFromBool(is_err) +
            @intFromBool(!is_null and !is_value and !is_err);

        try testing.expectEqual(@as(usize, 1), match_count);
        try testing.expectEqual(case.kind, classify(case.raw));
    }
}

test "representative raws decode only on their own lane" {
    const cases = try representativeCases();

    for (cases) |case| {
        switch (case.kind) {
            .null_value, .pointer_like => {
                try testing.expectEqual(@as(?usize, null), case.decoded_value);
                try testing.expectEqual(@as(?isize, null), case.decoded_error);
                try testing.expect(!xa_value.isValue(case.raw));
                try testing.expect(!err_ptr.isErrValue(case.raw));
            },
            .xa_value => {
                try testing.expectEqual(case.decoded_value, xa_value.toValue(case.raw));
                try testing.expectEqual(@as(?isize, null), case.decoded_error);
            },
            .err_ptr => {
                try testing.expectEqual(case.decoded_error, err_ptr.toErrorCode(case.raw));
                try testing.expectEqual(@as(?usize, null), case.decoded_value);
            },
        }
    }
}

test "constructor-backed boundary raws preserve the lane transition order" {
    const inline_zero = try xa_value.makeValue(0);
    const pointer_gap_low: usize = 2;
    const inline_one = try xa_value.makeValue(1);
    const inline_limit = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_before_err_floor = err_ptr.err_floor - 1;
    const err_floor = err_ptr.fromErrorCode(-4095);
    const err_top = err_ptr.fromErrorCode(-1);

    try testing.expectEqual(@as(usize, 0), 0);
    try testing.expect(0 < inline_zero);
    try testing.expect(inline_zero < pointer_gap_low);
    try testing.expect(pointer_gap_low < inline_one);
    try testing.expect(inline_one < inline_limit);
    try testing.expect(inline_limit < gap_before_err_floor);
    try testing.expect(gap_before_err_floor < err_floor);
    try testing.expect(err_floor < err_top);

    try testing.expectEqual(Kind.null_value, classify(0));
    try testing.expectEqual(Kind.xa_value, classify(inline_zero));
    try testing.expectEqual(Kind.pointer_like, classify(pointer_gap_low));
    try testing.expectEqual(Kind.xa_value, classify(inline_one));
    try testing.expectEqual(Kind.xa_value, classify(inline_limit));
    try testing.expectEqual(Kind.pointer_like, classify(gap_before_err_floor));
    try testing.expectEqual(Kind.err_ptr, classify(err_floor));
    try testing.expectEqual(Kind.err_ptr, classify(err_top));
}
