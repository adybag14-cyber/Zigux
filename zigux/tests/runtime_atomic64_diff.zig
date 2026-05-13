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

const IncNotZeroCase = struct {
    name: []const u8,
    seed: i64,
    previous: i64,
    final: i64,
    changed: bool,
};

const DecIfPositiveCase = struct {
    name: []const u8,
    seed: i64,
    result: i64,
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

pub const ThresholdReplaySummary = struct {
    iterations: usize,
    checksum: u64,
    final_counter: i64,
    final_stage: sample.ModuleStage,
    final_selftest_runs: usize,
    final_exit_runs: usize,
};

fn mixThresholdChecksum(checksum: *u64, value: u64) void {
    checksum.* = checksum.* *% 0x9e3779b185ebca87 +% value;
}

fn mixThresholdChecksumI64(checksum: *u64, value: i64) void {
    mixThresholdChecksum(checksum, @bitCast(value));
}

fn mixThresholdChecksumBool(checksum: *u64, value: bool) void {
    mixThresholdChecksum(checksum, @intFromBool(value));
}

fn mixThresholdChecksumUsize(checksum: *u64, value: usize) void {
    mixThresholdChecksum(checksum, @intCast(value));
}

pub fn runThresholdReplay(iterations: usize) !ThresholdReplaySummary {
    if (iterations == 0) return error.EmptyThresholdReplayBatch;

    var checksum: u64 = 0;
    var final_counter: i64 = 0;
    var final_stage = sample.ModuleStage.cold;
    var final_selftest_runs: usize = 0;
    var final_exit_runs: usize = 0;

    var iteration: usize = 0;
    while (iteration < iterations) : (iteration += 1) {
        const iteration_i64: i64 = @intCast(iteration);
        var module = sample.RuntimeAtomic64Sample{};
        const seed = 0x2aaa_3137_4001_500d + iteration_i64;
        try module.init(seed);

        const add_return = try module.addReturnCounter(0x1111_1111_2222_2222);
        const swapped = try module.swapCounter(-0x2152_4110_2150_3502 + iteration_i64);
        const compare = try module.compareSwapCounter(
            -0x2152_4110_2150_3502 + iteration_i64,
            -0x0531_5452_0ff2_0fff + iteration_i64,
        );
        const add_unless = try module.addUnlessCounter(3, std.math.minInt(i64));
        const and_previous = try module.andCounter(0x00ff_00ff_00ff_00ff);
        const or_previous = try module.orCounter(0x0100_0000_0000_0006);
        const xor_previous = try module.xorCounter(0x0000_ff00_0000_00ff);
        const summary = try module.runSelftest();
        try module.exit();

        mixThresholdChecksumI64(&checksum, seed);
        mixThresholdChecksumI64(&checksum, add_return);
        mixThresholdChecksumI64(&checksum, swapped);
        mixThresholdChecksumI64(&checksum, compare.previous);
        mixThresholdChecksumBool(&checksum, compare.stored);
        mixThresholdChecksumI64(&checksum, add_unless.previous);
        mixThresholdChecksumBool(&checksum, add_unless.changed);
        mixThresholdChecksumI64(&checksum, and_previous.previous);
        mixThresholdChecksumI64(&checksum, or_previous.previous);
        mixThresholdChecksumI64(&checksum, xor_previous.previous);
        mixThresholdChecksumUsize(&checksum, summary.operation_families.len);
        mixThresholdChecksumBool(&checksum, summary.checked_returning_paths);
        mixThresholdChecksumBool(&checksum, summary.checked_bitwise_paths);
        mixThresholdChecksumBool(&checksum, summary.checked_guard_paths);
        mixThresholdChecksumI64(&checksum, module.snapshotCounter());
        mixThresholdChecksumUsize(&checksum, module.selftest_runs);
        mixThresholdChecksumUsize(&checksum, module.exit_runs);

        final_counter = module.snapshotCounter();
        final_stage = module.stage();
        final_selftest_runs = module.selftest_runs;
        final_exit_runs = module.exit_runs;
    }

    return .{
        .iterations = iterations,
        .checksum = checksum,
        .final_counter = final_counter,
        .final_stage = final_stage,
        .final_selftest_runs = final_selftest_runs,
        .final_exit_runs = final_exit_runs,
    };
}

fn expectArithmeticCase(case: ArithmeticCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    _ = try module.addCounter(case.addend);
    try std.testing.expectEqual(case.after_add, module.snapshotCounter());

    _ = try module.subCounter(case.subtrahend);
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

fn expectIncNotZeroCase(case: IncNotZeroCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const result = try module.incNotZeroCounter();
    try std.testing.expectEqual(case.previous, result.previous);
    try std.testing.expectEqual(case.changed, result.changed);
    try std.testing.expectEqual(case.final, module.snapshotCounter());
}

fn expectDecIfPositiveCase(case: DecIfPositiveCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const result = try module.decIfPositiveCounter();
    try std.testing.expectEqual(case.result, result.result);
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

    try std.testing.expectEqual(case.previous, previous.previous);
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

test "runtime atomic64 diff gate keeps inc_not_zero and dec_if_positive guard paths explicit" {
    const inc_not_zero_cases = [_]IncNotZeroCase{
        .{
            .name = "inc_not_zero leaves a zero counter untouched",
            .seed = 0,
            .previous = 0,
            .final = 0,
            .changed = false,
        },
        .{
            .name = "inc_not_zero increments a live counter without hiding the previous value",
            .seed = 0x2aaa_3137_4001_500d,
            .previous = 0x2aaa_3137_4001_500d,
            .final = 0x2aaa_3137_4001_500e,
            .changed = true,
        },
    };

    for (inc_not_zero_cases) |case| {
        _ = case.name;
        try expectIncNotZeroCase(case);
    }

    const dec_if_positive_cases = [_]DecIfPositiveCase{
        .{
            .name = "dec_if_positive decrements a positive counter and stores the result",
            .seed = 3,
            .result = 2,
            .final = 2,
            .changed = true,
        },
        .{
            .name = "dec_if_positive reports the negative-one result while leaving zero unchanged",
            .seed = 0,
            .result = -1,
            .final = 0,
            .changed = false,
        },
        .{
            .name = "dec_if_positive keeps a negative counter unchanged while still reporting the decremented result",
            .seed = -5,
            .result = -6,
            .final = -5,
            .changed = false,
        },
    };

    for (dec_if_positive_cases) |case| {
        _ = case.name;
        try expectDecIfPositiveCase(case);
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

    const before_exit_snapshot = module.snapshotCounter();
    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(before_exit_snapshot, module.snapshotCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.andCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.compareSwapCounter(17, 19));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(1, 17));
}

test "runtime atomic64 diff gate rejects an empty threshold replay batch" {
    try std.testing.expectError(error.EmptyThresholdReplayBatch, runThresholdReplay(0));
}

test "runtime atomic64 diff gate keeps a deterministic threshold replay batch ready for future perf baselines" {
    const single = try runThresholdReplay(1);
    const repeated = try runThresholdReplay(4);

    try std.testing.expectEqual(@as(usize, 1), single.iterations);
    try std.testing.expectEqual(@as(usize, 4), repeated.iterations);
    try std.testing.expectEqual(sample.ModuleStage.exited, single.final_stage);
    try std.testing.expectEqual(sample.ModuleStage.exited, repeated.final_stage);
    try std.testing.expectEqual(@as(usize, 1), single.final_selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), repeated.final_selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), single.final_exit_runs);
    try std.testing.expectEqual(@as(usize, 1), repeated.final_exit_runs);
    try std.testing.expectEqual(@as(i64, 130322557735600377), single.final_counter);
    try std.testing.expectEqual(@as(i64, 130322557735600376), repeated.final_counter);
    try std.testing.expectEqual(@as(u64, 3626254113632800175), single.checksum);
    try std.testing.expectEqual(@as(u64, 9210681150676220922), repeated.checksum);
    try std.testing.expectEqualDeep(repeated, try runThresholdReplay(4));
    try std.testing.expect(repeated.checksum != single.checksum);
}
