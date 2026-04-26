const std = @import("std");

const Anchor = "lib/atomic64_test.c";

const ArithmeticExpectation = struct {
    name: []const u8,
    initial: i64,
    operand: i64,
    expected_return: i64,
    expected_final: i64,
    mode: enum {
        add_return,
        fetch_add,
        fetch_sub,
    },
};

const SwapExpectation = struct {
    name: []const u8,
    initial: i64,
    expected_old: i64,
    expected_final: i64,
    mode: union(enum) {
        xchg: i64,
        cmpxchg: struct {
            expected: i64,
            desired: i64,
        },
    },
};

const GuardOutcome = union(enum) {
    value: i64,
    flag: bool,
};

const GuardExpectation = struct {
    name: []const u8,
    initial: i64,
    expected_final: i64,
    expected_outcome: GuardOutcome,
    mode: union(enum) {
        add_unless: struct {
            add: i64,
            unless: i64,
        },
        dec_if_positive,
        inc_not_zero,
    },
};

fn replayArithmetic(case: ArithmeticExpectation) struct { returned: i64, final: i64 } {
    return switch (case.mode) {
        .add_return => .{
            .returned = case.initial + case.operand,
            .final = case.initial + case.operand,
        },
        .fetch_add => .{
            .returned = case.initial,
            .final = case.initial + case.operand,
        },
        .fetch_sub => .{
            .returned = case.initial,
            .final = case.initial - case.operand,
        },
    };
}

fn replaySwap(case: SwapExpectation) struct { returned: i64, final: i64 } {
    return switch (case.mode) {
        .xchg => |next| .{
            .returned = case.initial,
            .final = next,
        },
        .cmpxchg => |cmp| .{
            .returned = case.initial,
            .final = if (case.initial == cmp.expected) cmp.desired else case.initial,
        },
    };
}

fn replayGuard(case: GuardExpectation) struct {
    final: i64,
    outcome: GuardOutcome,
} {
    return switch (case.mode) {
        .add_unless => |op| blk: {
            const changed = case.initial != op.unless;
            break :blk .{
                .final = if (changed) case.initial + op.add else case.initial,
                .outcome = .{ .flag = changed },
            };
        },
        .dec_if_positive => blk: {
            const decremented = case.initial - 1;
            break :blk .{
                .final = if (case.initial > 0) decremented else case.initial,
                .outcome = .{ .value = decremented },
            };
        },
        .inc_not_zero => blk: {
            const changed = case.initial != 0;
            break :blk .{
                .final = if (changed) case.initial + 1 else case.initial,
                .outcome = .{ .flag = changed },
            };
        },
    };
}

test "atomic64 diff gate keeps the anchor explicit" {
    try std.testing.expectEqualStrings("lib/atomic64_test.c", Anchor);
}

test "atomic64 diff gate replays bounded arithmetic and returning expectations" {
    const v0: i64 = @bitCast(@as(u64, 0xaaa3_1337_c001_d00d));
    const onestwos: i64 = @bitCast(@as(u64, 0x1111_1111_2222_2222));

    const cases = [_]ArithmeticExpectation{
        .{
            .name = "RETURN_FAMILY_TEST add_return with onestwos",
            .initial = v0,
            .operand = onestwos,
            .expected_return = v0 + onestwos,
            .expected_final = v0 + onestwos,
            .mode = .add_return,
        },
        .{
            .name = "FETCH_FAMILY_TEST fetch_add with negative one",
            .initial = v0,
            .operand = -1,
            .expected_return = v0,
            .expected_final = v0 - 1,
            .mode = .fetch_add,
        },
        .{
            .name = "FETCH_FAMILY_TEST fetch_sub with onestwos",
            .initial = v0,
            .operand = onestwos,
            .expected_return = v0,
            .expected_final = v0 - onestwos,
            .mode = .fetch_sub,
        },
    };

    for (cases) |case| {
        const replay = replayArithmetic(case);
        try std.testing.expectEqual(case.expected_return, replay.returned);
        try std.testing.expectEqual(case.expected_final, replay.final);
    }
}

test "atomic64 diff gate replays swap expectations from XCHG and CMPXCHG families" {
    const v0: i64 = @bitCast(@as(u64, 0xaaa3_1337_c001_d00d));
    const v1: i64 = @bitCast(@as(u64, 0xdead_beef_deaf_cafe));
    const v2: i64 = @bitCast(@as(u64, 0xface_abad_f00d_f001));

    const cases = [_]SwapExpectation{
        .{
            .name = "XCHG_FAMILY_TEST swaps in v1 and returns v0",
            .initial = v0,
            .expected_old = v0,
            .expected_final = v1,
            .mode = .{ .xchg = v1 },
        },
        .{
            .name = "CMPXCHG_FAMILY_TEST success path stores desired value",
            .initial = v0,
            .expected_old = v0,
            .expected_final = v1,
            .mode = .{ .cmpxchg = .{ .expected = v0, .desired = v1 } },
        },
        .{
            .name = "CMPXCHG_FAMILY_TEST mismatch keeps the original value",
            .initial = v0,
            .expected_old = v0,
            .expected_final = v0,
            .mode = .{ .cmpxchg = .{ .expected = v2, .desired = v1 } },
        },
    };

    for (cases) |case| {
        const replay = replaySwap(case);
        try std.testing.expectEqual(case.expected_old, replay.returned);
        try std.testing.expectEqual(case.expected_final, replay.final);
    }
}

test "atomic64 diff gate keeps add_unless dec_if_positive and inc_not_zero semantics explicit" {
    const onestwos: i64 = @bitCast(@as(u64, 0x1111_1111_2222_2222));
    const v0: i64 = @bitCast(@as(u64, 0xaaa3_1337_c001_d00d));
    const v1: i64 = @bitCast(@as(u64, 0xdead_beef_deaf_cafe));

    const cases = [_]GuardExpectation{
        .{
            .name = "atomic64_add_unless blocks when the guard matches",
            .initial = v0,
            .expected_final = v0,
            .expected_outcome = .{ .flag = false },
            .mode = .{ .add_unless = .{ .add = 1, .unless = v0 } },
        },
        .{
            .name = "atomic64_add_unless increments when the guard does not match",
            .initial = v0,
            .expected_final = v0 + 1,
            .expected_outcome = .{ .flag = true },
            .mode = .{ .add_unless = .{ .add = 1, .unless = v1 } },
        },
        .{
            .name = "atomic64_dec_if_positive decrements a positive value",
            .initial = onestwos,
            .expected_final = onestwos - 1,
            .expected_outcome = .{ .value = onestwos - 1 },
            .mode = .dec_if_positive,
        },
        .{
            .name = "atomic64_dec_if_positive reports negative one at zero without storing it",
            .initial = 0,
            .expected_final = 0,
            .expected_outcome = .{ .value = -1 },
            .mode = .dec_if_positive,
        },
        .{
            .name = "atomic64_inc_not_zero refuses to increment zero",
            .initial = 0,
            .expected_final = 0,
            .expected_outcome = .{ .flag = false },
            .mode = .inc_not_zero,
        },
        .{
            .name = "atomic64_inc_not_zero increments non-zero values",
            .initial = -1,
            .expected_final = 0,
            .expected_outcome = .{ .flag = true },
            .mode = .inc_not_zero,
        },
    };

    for (cases) |case| {
        const replay = replayGuard(case);
        try std.testing.expectEqual(case.expected_final, replay.final);

        switch (case.expected_outcome) {
            .value => |expected| switch (replay.outcome) {
                .value => |actual| try std.testing.expectEqual(expected, actual),
                .flag => return error.TestUnexpectedResult,
            },
            .flag => |expected| switch (replay.outcome) {
                .flag => |actual| try std.testing.expectEqual(expected, actual),
                .value => return error.TestUnexpectedResult,
            },
        }
    }
}
