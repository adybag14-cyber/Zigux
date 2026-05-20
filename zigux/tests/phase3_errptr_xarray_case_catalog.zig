const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

const ExpectedKind = enum {
    null,
    pointer_like,
    xa_value,
    err_ptr,
};

const Case = struct {
    name: []const u8,
    raw: usize,
    kind: ExpectedKind,
    decoded_error: ?isize = null,
    decoded_value: ?usize = null,
};

fn dumpCases() ![7]Case {
    return .{
        .{ .name = "null", .raw = 0, .kind = .null },
        .{ .name = "pointer_like", .raw = 64, .kind = .pointer_like },
        .{
            .name = "inline_small",
            .raw = try xa_value.makeValue(29),
            .kind = .xa_value,
            .decoded_value = 29,
        },
        .{
            .name = "inline_limit",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .xa_value,
            .decoded_value = xa_value.safe_inline_limit,
        },
        .{
            .name = "gap_before_err_floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer_like,
        },
        .{
            .name = "err_enomem",
            .raw = err_ptr.fromErrorCode(-12),
            .kind = .err_ptr,
            .decoded_error = -12,
        },
        .{
            .name = "err_max",
            .raw = err_ptr.fromErrorCode(-4095),
            .kind = .err_ptr,
            .decoded_error = -4095,
        },
    };
}

fn expectLane(case: Case) !void {
    switch (case.kind) {
        .null => {
            try std.testing.expectEqual(@as(usize, 0), case.raw);
            try std.testing.expect(!xa_value.isValue(case.raw));
            try std.testing.expect(!err_ptr.isErrValue(case.raw));
        },
        .pointer_like => {
            try std.testing.expect(err_ptr.isOkValue(case.raw));
            try std.testing.expect(!xa_value.isValue(case.raw));
            try std.testing.expect(!err_ptr.isErrValue(case.raw));
        },
        .xa_value => {
            try std.testing.expect(xa_value.isValue(case.raw));
            try std.testing.expect(!err_ptr.isErrValue(case.raw));
            try std.testing.expectEqual(case.decoded_value.?, xa_value.toValue(case.raw));
        },
        .err_ptr => {
            try std.testing.expect(err_ptr.isErrValue(case.raw));
            try std.testing.expect(!xa_value.isValue(case.raw));
            try std.testing.expectEqual(case.decoded_error.?, err_ptr.toErrorCode(case.raw));
        },
    }
}

test "current dump catalog keeps each representative raw in its expected lane" {
    const cases = try dumpCases();

    for (cases) |case| {
        try expectLane(case);
    }
}

test "current dump catalog keeps the cutoff triplet contiguous" {
    const cases = try dumpCases();
    const inline_limit = cases[3];
    const gap_before_err_floor = cases[4];
    const err_max = cases[6];

    try std.testing.expectEqual(xa_value.safe_inline_limit, inline_limit.decoded_value.?);
    try std.testing.expectEqual(err_ptr.err_floor - 2, inline_limit.raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, gap_before_err_floor.raw);
    try std.testing.expectEqual(err_ptr.err_floor, err_max.raw);
    try std.testing.expectEqual(@as(isize, -4095), err_max.decoded_error.?);
}

test "current dump catalog preserves the representative live witnesses" {
    const cases = try dumpCases();
    const pointer_like = cases[1];
    const inline_small = cases[2];
    const err_enomem = cases[5];

    try std.testing.expectEqual(@as(usize, 64), pointer_like.raw);
    try std.testing.expectEqual(@as(usize, 59), inline_small.raw);
    try std.testing.expectEqual(@as(usize, 29), inline_small.decoded_value.?);
    try std.testing.expectEqual(@as(isize, -12), err_enomem.decoded_error.?);
    try std.testing.expect(err_ptr.isErrValue(err_enomem.raw));
    try std.testing.expect(!xa_value.isValue(err_enomem.raw));
}
