const std = @import("std");
const sample = @import("runtime_atomic64_sample");

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

const AddCase = struct {
    name: []const u8,
    seed: i64,
    addend: i64,
    previous: i64,
    final: i64,
};

const SubCase = struct {
    name: []const u8,
    seed: i64,
    subtrahend: i64,
    previous: i64,
    final: i64,
};

const BitwiseCase = struct {
    name: []const u8,
    seed: i64,
    operand: i64,
    previous: i64,
    final: i64,
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

fn signed(bits: u64) i64 {
    return @bitCast(bits);
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

fn expectAddCase(case: AddCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const result = try module.addCounter(case.addend);
    try std.testing.expectEqual(case.previous, result.previous);
    try std.testing.expectEqual(case.final, result.final);
    try std.testing.expectEqual(case.final, module.snapshotCounter());
}

fn expectSubCase(case: SubCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const result = try module.subCounter(case.subtrahend);
    try std.testing.expectEqual(case.previous, result.previous);
    try std.testing.expectEqual(case.final, result.final);
    try std.testing.expectEqual(case.final, module.snapshotCounter());
}

fn expectOrCase(case: BitwiseCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const result = try module.orCounter(case.operand);
    try std.testing.expectEqual(case.previous, result.previous);
    try std.testing.expectEqual(case.final, result.final);
    try std.testing.expectEqual(case.final, module.snapshotCounter());
}

fn expectAndCase(case: BitwiseCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const result = try module.andCounter(case.operand);
    try std.testing.expectEqual(case.previous, result.previous);
    try std.testing.expectEqual(case.final, result.final);
    try std.testing.expectEqual(case.final, module.snapshotCounter());
}

fn expectXorCase(case: BitwiseCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const result = try module.xorCounter(case.operand);
    try std.testing.expectEqual(case.previous, result.previous);
    try std.testing.expectEqual(case.final, result.final);
    try std.testing.expectEqual(case.final, module.snapshotCounter());
}

fn expectAndNotCase(case: BitwiseCase) !void {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(case.seed);

    const result = try module.andNotCounter(case.operand);
    try std.testing.expectEqual(case.previous, result.previous);
    try std.testing.expectEqual(case.final, result.final);
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

test "runtime atomic64 diff gate replays bounded atomic64_test.c add, sub, bitwise, exchange, cmpxchg, add_unless, inc_not_zero, and dec_if_positive expectations" {
    const v0 = signed(0xaaa3_1337_c001_d00d);
    const v1 = signed(0xdead_beef_deaf_cafe);
    const v2 = signed(0xface_abad_f00d_f001);
    const onestwos = signed(0x1111_1111_2222_2222);

    const add_cases = [_]AddCase{
        .{
            .name = "add grows the starter counter by the onestwos constant from atomic64_test.c",
            .seed = v0,
            .addend = onestwos,
            .previous = v0,
            .final = signed(0xbbb4_2448_e223_f22f),
        },
        .{
            .name = "add accepts the negative one decrement path from atomic64_test.c",
            .seed = v0,
            .addend = -1,
            .previous = v0,
            .final = signed(0xaaa3_1337_c001_d00c),
        },
    };

    for (add_cases) |case| {
        try expectAddCase(case);
    }

    const sub_cases = [_]SubCase{
        .{
            .name = "sub matches the wide onestwos decrement from atomic64_test.c",
            .seed = v0,
            .subtrahend = onestwos,
            .previous = v0,
            .final = signed(0x9992_0226_9ddf_adeb),
        },
        .{
            .name = "sub accepts the negative one increment path from atomic64_test.c",
            .seed = v0,
            .subtrahend = -1,
            .previous = v0,
            .final = signed(0xaaa3_1337_c001_d00e),
        },
    };

    for (sub_cases) |case| {
        try expectSubCase(case);
    }

    const or_cases = [_]BitwiseCase{
        .{
            .name = "or matches the v0|v1 family from atomic64_test.c",
            .seed = v0,
            .operand = v1,
            .previous = v0,
            .final = signed(0xfeaf_bfff_deaf_daff),
        },
    };

    for (or_cases) |case| {
        try expectOrCase(case);
    }

    const and_cases = [_]BitwiseCase{
        .{
            .name = "and matches the v0&v1 family from atomic64_test.c",
            .seed = v0,
            .operand = v1,
            .previous = v0,
            .final = signed(0x8aa1_1227_c001_c00c),
        },
    };

    for (and_cases) |case| {
        try expectAndCase(case);
    }

    const xor_cases = [_]BitwiseCase{
        .{
            .name = "xor matches the v0^v1 family from atomic64_test.c",
            .seed = v0,
            .operand = v1,
            .previous = v0,
            .final = signed(0x740e_add8_1eae_1af3),
        },
    };

    for (xor_cases) |case| {
        try expectXorCase(case);
    }

    const andnot_cases = [_]BitwiseCase{
        .{
            .name = "andnot matches the v0&~v1 family from atomic64_test.c",
            .seed = v0,
            .operand = v1,
            .previous = v0,
            .final = signed(0x2002_0110_0000_1001),
        },
    };

    for (andnot_cases) |case| {
        try expectAndNotCase(case);
    }

    const exchange_cases = [_]DiffCase{
        .{
            .name = "v0 to v1 keeps the original counter visible as the exchange return value",
            .seed = v0,
            .next = v1,
        },
        .{
            .name = "v1 to v2 keeps wide negative and positive 64-bit values distinct",
            .seed = v1,
            .next = v2,
        },
        .{
            .name = "high-bit starter from atomic64_test.c still round-trips through exchange",
            .seed = std.math.minInt(i64),
            .next = -1,
        },
    };

    for (exchange_cases) |case| {
        try expectExchangeCase(case);
    }

    const compare_swap_cases = [_]CompareSwapCase{
        .{
            .name = "cmpxchg success path stores the desired value when the expected value matches",
            .seed = v0,
            .expected = v0,
            .desired = v1,
            .previous = v0,
            .final = v1,
            .stored = true,
        },
        .{
            .name = "cmpxchg mismatch keeps the original value visible",
            .seed = v0,
            .expected = v2,
            .desired = v1,
            .previous = v0,
            .final = v0,
            .stored = false,
        },
    };

    for (compare_swap_cases) |case| {
        try expectCompareSwapCase(case);
    }

    // Keep the exact add_unless, inc_not_zero, and dec_if_positive expectations marker live for review.
    const add_unless_cases = [_]AddUnlessCase{
        .{
            .name = "add_unless leaves the counter untouched when it already matches the blocked value",
            .seed = v0,
            .addend = 1,
            .unless_value = v0,
            .previous = v0,
            .final = v0,
            .changed = false,
        },
        .{
            .name = "add_unless applies the addend when the current value differs from the blocked value",
            .seed = v0,
            .addend = 1,
            .unless_value = v1,
            .previous = v0,
            .final = signed(0xaaa3_1337_c001_d00e),
            .changed = true,
        },
    };

    for (add_unless_cases) |case| {
        try expectAddUnlessCase(case);
    }

    const inc_not_zero_cases = [_]IncNotZeroCase{
        .{
            .name = "inc_not_zero increments a positive non-zero counter",
            .seed = onestwos,
            .previous = onestwos,
            .final = 0x1111_1111_2222_2223,
            .changed = true,
        },
        .{
            .name = "inc_not_zero leaves zero unchanged",
            .seed = 0,
            .previous = 0,
            .final = 0,
            .changed = false,
        },
        .{
            .name = "inc_not_zero still increments -1 back to zero",
            .seed = -1,
            .previous = -1,
            .final = 0,
            .changed = true,
        },
        .{
            .name = "inc_not_zero keeps the high-bit atomic64_test.c sentinel nonzero while incrementing it",
            .seed = std.math.minInt(i64),
            .previous = std.math.minInt(i64),
            .final = std.math.minInt(i64) + 1,
            .changed = true,
        },
    };

    for (inc_not_zero_cases) |case| {
        try expectIncNotZeroCase(case);
    }

    const dec_if_positive_cases = [_]DecIfPositiveCase{
        .{
            .name = "dec_if_positive decrements a positive counter and returns the decremented value",
            .seed = onestwos,
            .result = 0x1111_1111_2222_2221,
            .final = 0x1111_1111_2222_2221,
            .changed = true,
        },
        .{
            .name = "dec_if_positive returns -1 for zero without changing storage",
            .seed = 0,
            .result = -1,
            .final = 0,
            .changed = false,
        },
        .{
            .name = "dec_if_positive returns seed minus one for negative inputs without storing it",
            .seed = -1,
            .result = -2,
            .final = -1,
            .changed = false,
        },
    };

    for (dec_if_positive_cases) |case| {
        try expectDecIfPositiveCase(case);
    }
}

test "runtime atomic64 diff gate keeps selftest family coverage explicit" {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(std.math.minInt(i64));

    const summary = try module.runSelftest();
    try std.testing.expectEqualStrings("lib/atomic64_test.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), summary.operation_families.len);
    try std.testing.expectEqual(sample.OperationFamily.arithmetic, summary.operation_families[0]);
    try std.testing.expectEqual(sample.OperationFamily.bitwise, summary.operation_families[1]);
    try std.testing.expectEqual(sample.OperationFamily.returning_ops, summary.operation_families[2]);
    try std.testing.expectEqual(sample.OperationFamily.swap_ops, summary.operation_families[3]);
    try std.testing.expectEqual(sample.OperationFamily.guard_ops, summary.operation_families[4]);
    try std.testing.expect(summary.checked_returning_paths);
    try std.testing.expect(summary.checked_guard_paths);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(std.math.minInt(i64), module.snapshotCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.subCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.compareSwapCounter(std.math.minInt(i64), 7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.orCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.andCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.xorCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.andNotCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(
        1,
        std.math.minInt(i64),
    ));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.incNotZeroCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.decIfPositiveCounter());
}

test "runtime atomic64 diff gate keeps lifecycle transitions single-shot" {
    var cold_module = sample.RuntimeAtomic64Sample{};
    try std.testing.expectError(error.InvalidLifecycleTransition, cold_module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, cold_module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, cold_module.incNotZeroCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, cold_module.decIfPositiveCounter());

    var module = sample.RuntimeAtomic64Sample{};
    try module.init(7);
    const initialized_summary = module.summary();
    try std.testing.expectEqual(@as(i64, 7), initialized_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init(11));

    _ = try module.runSelftest();
    const post_selftest_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(i64, 7), post_selftest_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), post_selftest_summary.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init(13));

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(i64, 7), exited_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init(17));
    try std.testing.expectEqual(@as(i64, 7), module.snapshotCounter());
}

test "runtime atomic64 diff gate keeps post-selftest replay explicit" {
    var module = sample.RuntimeAtomic64Sample{};
    const seed = 0x1111_2222_3333_4444;

    try module.init(seed);
    _ = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());

    const add_result = try module.addCounter(0x12);
    try std.testing.expectEqual(seed, add_result.previous);
    try std.testing.expectEqual(seed + 0x12, add_result.final);
    try std.testing.expectEqual(seed + 0x12, module.snapshotCounter());

    const sub_result = try module.subCounter(0x10);
    try std.testing.expectEqual(seed + 0x12, sub_result.previous);
    try std.testing.expectEqual(seed + 0x02, sub_result.final);
    try std.testing.expectEqual(seed + 0x02, module.snapshotCounter());

    const or_result = try module.orCounter(0x0000_0000_0000_00ff);
    try std.testing.expectEqual(seed + 0x02, or_result.previous);
    try std.testing.expectEqual(0x1111_2222_3333_44ff, or_result.final);
    try std.testing.expectEqual(0x1111_2222_3333_44ff, module.snapshotCounter());

    const and_result = try module.andCounter(0x0fff_ffff_ffff_ff0f);
    try std.testing.expectEqual(0x1111_2222_3333_44ff, and_result.previous);
    try std.testing.expectEqual(0x0111_2222_3333_440f, and_result.final);
    try std.testing.expectEqual(0x0111_2222_3333_440f, module.snapshotCounter());

    const xor_result = try module.xorCounter(0x0000_00ff_0000_00f0);
    try std.testing.expectEqual(0x0111_2222_3333_440f, xor_result.previous);
    try std.testing.expectEqual(0x0111_22dd_3333_44ff, xor_result.final);
    try std.testing.expectEqual(0x0111_22dd_3333_44ff, module.snapshotCounter());

    const andnot_result = try module.andNotCounter(0x0000_0000_0000_00ff);
    try std.testing.expectEqual(0x0111_22dd_3333_44ff, andnot_result.previous);
    try std.testing.expectEqual(0x0111_22dd_3333_4400, andnot_result.final);
    try std.testing.expectEqual(0x0111_22dd_3333_4400, module.snapshotCounter());

    const swapped = try module.swapCounter(seed + 1);
    try std.testing.expectEqual(0x0111_22dd_3333_4400, swapped);
    try std.testing.expectEqual(seed + 1, module.snapshotCounter());

    const compare_swap = try module.compareSwapCounter(seed + 1, seed + 2);
    try std.testing.expectEqual(seed + 1, compare_swap.previous);
    try std.testing.expect(compare_swap.stored);
    try std.testing.expectEqual(seed + 2, module.snapshotCounter());

    const compare_swap_mismatch = try module.compareSwapCounter(seed + 1, seed + 9);
    try std.testing.expectEqual(seed + 2, compare_swap_mismatch.previous);
    try std.testing.expect(!compare_swap_mismatch.stored);
    try std.testing.expectEqual(seed + 2, module.snapshotCounter());

    const add_unless = try module.addUnlessCounter(3, 0);
    try std.testing.expectEqual(seed + 2, add_unless.previous); try std.testing.expect(add_unless.changed); try std.testing.expectEqual(seed + 5, module.snapshotCounter());

    const inc_not_zero = try module.incNotZeroCounter();
    try std.testing.expectEqual(seed + 5, inc_not_zero.previous); try std.testing.expect(inc_not_zero.changed); try std.testing.expectEqual(seed + 6, module.snapshotCounter());

    const dec_if_positive = try module.decIfPositiveCounter();
    try std.testing.expectEqual(seed + 5, dec_if_positive.result); try std.testing.expect(dec_if_positive.changed); try std.testing.expectEqual(seed + 5, module.snapshotCounter());

    const rewind_to_zero = try module.addUnlessCounter(-(seed + 5), -1);
    try std.testing.expectEqual(seed + 5, rewind_to_zero.previous); try std.testing.expect(rewind_to_zero.changed); try std.testing.expectEqual(@as(i64, 0), module.snapshotCounter());

    const blocked_add_unless = try module.addUnlessCounter(3, 0);
    try std.testing.expectEqual(@as(i64, 0), blocked_add_unless.previous); try std.testing.expect(!blocked_add_unless.changed); try std.testing.expectEqual(@as(i64, 0), module.snapshotCounter());

    const zero_inc_not_zero = try module.incNotZeroCounter(); const zero_dec_if_positive = try module.decIfPositiveCounter();
    try std.testing.expectEqual(@as(i64, 0), zero_inc_not_zero.previous); try std.testing.expect(!zero_inc_not_zero.changed); try std.testing.expectEqual(@as(i64, -1), zero_dec_if_positive.result); try std.testing.expect(!zero_dec_if_positive.changed); try std.testing.expectEqual(@as(i64, 0), module.snapshotCounter());

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
}
