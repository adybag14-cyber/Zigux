const std = @import("std");
const sample = @import("runtime_atomic64_sample");

const DiffCase = struct {
    name: []const u8,
    seed: i64,
    next: i64,
};

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

test "runtime atomic64 diff gate replays bounded atomic64_test.c exchange expectations" {
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
        try expectExchangeCase(case);
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
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
}
