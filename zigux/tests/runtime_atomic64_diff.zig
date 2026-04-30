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
    const add_cases = []AddCase{
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

    const sub_cases = []SubCase{