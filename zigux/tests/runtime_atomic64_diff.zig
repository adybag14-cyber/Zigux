const std = @import("std");
const sample = @import("runtime_atomic64_sample");

const ArithmeticCase = struct {
    name: []const u8,
    seed: i64,
    addend: i64,
    subtrahend: i64,
    after_add: i64,
    after_sub: i64,
    add_return: i64,
    sub_return: i64,
    inc_return: i64,
    dec_return: i64,
};

const DiffCase = struct {
    name: []const u8,
    seed: i64,
    next: i64,
};

const CompareSwapCase = struct {
    name: []const u8,
    seed: i64,
    expected: i64,
    desired: i64,
    previous: i64,
    final: i64,
    stored: bool,
};

const AddUnlessCase = struct {
    name: []const u8,
    seed: i64,
    addend: i64,
    unless_value: i64,
    previous: i64,
    final: i64,
    changed: bool,
};

const BitwiseOp = enum {
    and_mask,
    or_mask,
    xor_mask,
};

const BitwiseCase = struct {
    name: []const u8,
    op: BitwiseOp,
    seed: i64,
    mask: i64,
    previous: i64,
    final: i64,
};

fn expectArithmeticCase(case: ArithmeticCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    try module.addCounter(case.addend);
    try std.testing.expectEqual(case.after_add, module.snapshotCounter());

    try module.subCounter(case.subtrahend);
    try std.testing.expectEqual(case.after_sub, module.snapshotCounter());

    try std.testing.expectEqual(case.add_return, try module.addReturnCounter(case.subtrahend));
    try std.testing.expectEqual(case.add_return, module.snapshotCounter());

    try std.testing.expectEqual(case.sub_return, try module.subReturnCounter(case.subtrahend));
    try std.testing.expectEqual(case.sub_return, module.snapshotCounter());

    try std.testing.expectEqual(case.inc_return, try module.incReturnCounter());
    try std.testing.expectEqual(case.inc_return, module.snapshotCounter());

    try std.testing.expectEqual(case.dec_return, try module.decReturnCounter());
    try std.testing.expectEqual(case.dec_return, module.snapshotCounter());
}

fn expectExchangeCase(case: DiffCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const previous = try module.swapCounter(case.next);
    try std.testing.expectEqual(case.seed, previous);
    try std.testing.expectEqual(case.next, module.snapshotCounter());

    const restored = try module.swapCounter(case.seed);
    try std.testing.expectEqual(case.next, restored);
    try std.testing.expectEqual(case.seed, module.snapshotCounter());
}

fn expectCompareSwapCase(case: CompareSwapCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const result = try module.compareSwapCounter(case.expected, case.desired);
    try std.testing.expectEqual(case.previous, result.previous);
    try std.testing.expectEqual(case.stored, result.stored);
    try std.testing.expectEqual(case.final, module.snapshotCounter());
}

fn expectAddUnlessCase(case: AddUnlessCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const result = try module.addUnlessCounter(case.addend, case.unless_value);
    try std.testing.expectEqual(case.previous, result.previous);
    try std.testing.expectEqual(case.changed, result.changed);
    try std.testing.expectEqual(case.final, module.snapshotCounter());
}

fn expectBitwiseCase(case: BitwiseCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const previous = switch (case.op) {
        .and_mask => try module.andCounter(case.mask),
        .or_mask => try module.orCounter(case.mask),
        .xor_mask => try module.xorCounter(case.mask),
    };

    try std.testing.expectEqual(case.previous, previous);
    try std.testing.expectEqual(case.final, module.snapshotCounter());
}

test "runtime atomic64 diff gate replays bounded atomic64_test.c arithmetic, exchange, cmpxchg, add_unless, and bitwise expectations" {
    const arithmetic_cases = [_]ArithmeticCase{
        .{
            .name = "v0 arithmetic path mirrors add/sub/add_return/sub_return/inc_return/dec_return sequencing",
            .seed = 0x2aaa_3137_4001_500d,
            .addend = 0x1111_1111_2222_2222,
            .subtrahend = 0x1111_1111_2222_2222,
            .after_add = 0x3bbb_4248_6223_722f,
            .after_sub = 0x2aaa_3137_4001_500d,
            .add_return = 0x3bbb_4248_6223_722f,
            .sub_return = 0x2aaa_3137_4001_500d,
            .inc_return = 0x2aaa_3137_4001_500e,
            .dec_return = 0x2aaa_3137_4001_500d,
        },
        .{
            .name = "negative-one arithmetic path keeps decrement-style updates visible",
            .seed = 0x2aaa_3137_4001_500d,
            .addend = -1,
            .subtrahend = -1,
            .after_add = 0x2aaa_3137_4001_500c,
            .after_sub = 0x2aaa_3137_4001_500d,
            .add_return = 0x2aaa_3137_4001_500c,
            .sub_return = 0x2aaa_3137_4001_500d,
            .inc_return = 0x2aaa_3137_4001_500e,
            .dec_return = 0x2aaa_3137_4001_500d,
        },
    };

    for (arithmetic_cases) |case| {
        _ = case.name;
        try expectArithmeticCase(case);
    }

    const cases = [_]DiffCase{
        .{
            .name = "v0 to v1 keeps the original counter visible as the exchange return value",
            .seed = 0x2aaa_3137_4001_500d,
            .next = -0x2152_4110_2150_3502,
        },
        .{
            .name = "v1 to v2 keeps wide negative and positive 64-bit values distinct",
            .seed = -0x2152_4110_2150_3502,
            .next = -0x0531_5452_0ff2_0fff,
        },
        .{
            .name = "high-bit starter from atomic64_test.c still round-trips through exchange",
            .seed = std.math.minInt(i64),
            .next = -1,
        },
    };

    for (cases) |case| {
        _ = case.name;
        try expectExchangeCase(case);
    }

    const compare_swap_cases = [_]CompareSwapCase{
        .{
            .name = "cmpxchg success path stores the desired value when the expected value matches",
            .seed = 0x2aaa_3137_4001_500d,
            .expected = 0x2aaa_3137_4001_500d,
            .desired = -0x2152_4110_2150_3502,
            .previous = 0x2aaa_3137_4001_500d,
            .final = -0x2152_4110_2150_3502,
            .stored = true,
        },
        .{
            .name = "cmpxchg mismatch keeps the original value visible",
            .seed = 0x2aaa_3137_4001_500d,
            .expected = -0x0531_5452_0ff2_0fff,
            .desired = -0x2152_4110_2150_3502,
            .previous = 0x2aaa_3137_4001_500d,
            .final = 0x2aaa_3137_4001_500d,
            .stored = false,
        },
    };

    for (compare_swap_cases) |case| {
        _ = case.name;
        try expectCompareSwapCase(case);
    }

    const add_unless_cases = [_]AddUnlessCase{
        .{
            .name = "add_unless leaves the counter untouched when it already matches the blocked value",
            .seed = 0x2aaa_3137_4001_500d,
            .addend = 1,
            .unless_value = 0x2aaa_3137_4001_500d,
            .previous = 0x2aaa_3137_4001_500d,
            .final = 0x2aaa_3137_4001_500d,
            .changed = false,
        },
        .{
            .name = "add_unless applies the addend when the current value differs from the blocked value",
            .seed = 0x2aaa_3137_4001_500d,
            .addend = 1,
            .unless_value = -0x2152_4110_2150_3502,
            .previous = 0x2aaa_3137_4001_500d,
            .final = 0x2aaa_3137_4001_500e,
            .changed = true,
        },
    };

    for (add_unless_cases) |case| {
        _ = case.name;
        try expectAddUnlessCase(case);
    }

    const bitwise_cases = [_]BitwiseCase{
        .{
            .name = "and preserves only the masked bits from an all-ones starter",
            .op = .and_mask,
            .seed = -1,
            .mask = 0x00ff_00ff_00ff_00ff,
            .previous = -1,
            .final = 0x00ff_00ff_00ff_00ff,
        },
        .{
            .name = "or lifts high and low flags into the running counter",
            .op = .or_mask,
            .seed = 0x2000_0000_0000_0001,
            .mask = 0x0100_0000_0000_0006,
            .previous = 0x2000_0000_0000_0001,
            .final = 0x2100_0000_0000_0007,
        },
        .{
            .name = "xor toggles separated flag groups without losing the wide value shape",
            .op = .xor_mask,
            .seed = 0x00ff_0000_00ff_0000,
            .mask = 0x0000_ff00_0000_00ff,
            .previous = 0x00ff_0000_00ff_0000,
            .final = 0x00ff_ff00_00ff_00ff,
        },
    };

    for (bitwise_cases) |case| {
        _ = case.name;
        try expectBitwiseCase(case);
    }
}

test "runtime atomic64 diff gate keeps selftest family coverage explicit" {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(std.math.minInt(i64));

    const added = try module.addReturnCounter(1);
    try std.testing.expectEqual(std.math.minInt(i64) + 1, added);

    const summary = try module.runSelftest();
    try std.testing.expectEqualStrings("lib/atomic64_test.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), summary.operation_families.len);
    try std.testing.expectEqual(sample.OperationFamily.arithmetic, summary.operation_families[0]);
    try std.testing.expectEqual(sample.OperationFamily.bitwise, summary.operation_families[1]);
    try std.testing.expectEqual(sample.OperationFamily.returning_ops, summary.operation_families[2]);
    try std.testing.expectEqual(sample.OperationFamily.swap_ops, summary.operation_families[3]);
    try std.testing.expectEqual(sample.OperationFamily.guard_ops, summary.operation_families[4]);
    try std.testing.expect(summary.checked_returning_paths);
    try std.testing.expect(summary.checked_bitwise_paths);
    try std.testing.expect(summary.checked_guard_paths);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.andCounter(7));
}
