const std = @import("std");
const runtime_atomic64_sample = @import("runtime_atomic64_sample");

const ModuleStage = runtime_atomic64_sample.ModuleStage;
const RuntimeAtomic64Sample = runtime_atomic64_sample.RuntimeAtomic64Sample;
const Summary = runtime_atomic64_sample.Summary;

const LoadPlan = struct {
    name: []const u8,
    seed: i64,
    expected_selftest_anchor: []const u8,
};

const load_plan = LoadPlan{
    .name = "runtime_atomic64",
    .seed = 0x2aaa_3137_4001_500d,
    .expected_selftest_anchor = "lib/atomic64_test.c",
};

fn expectCounterAndInitStable(before: Summary, after: Summary) !void {
    try std.testing.expectEqual(before.counter_snapshot, after.counter_snapshot);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
}

fn expectBlockedPublicationAndDepmodFieldsExcluded(comptime T: type) !void {
    const blocked_publication_fields = [_][]const u8{
        "modinfo",
        "module_alias",
        "module_aliases",
        "modules_alias_path",
        "module_install_root",
        "modules_order_path",
        "modules_builtin_path",
        "module_symvers_path",
        "depmod_script",
        "depmod_manifest",
        "depmod_aliases",
    };

    inline for (blocked_publication_fields) |field| {
        try std.testing.expect(!@hasField(T, field));
    }
}

test "runtime atomic64 loader keeps blocked publication and depmod surfaces out of the loader-facing payload" {
    try expectBlockedPublicationAndDepmodFieldsExcluded(LoadPlan);
}

test "runtime atomic64 loader keeps loader-facing seed and descriptor explicit" {
    const descriptor = RuntimeAtomic64Sample.descriptor();
    try std.testing.expectEqualStrings(load_plan.name, descriptor.name);
    try std.testing.expectEqualStrings(load_plan.expected_selftest_anchor, descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var module = RuntimeAtomic64Sample{};
    try module.init(load_plan.seed);

    const summary = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(load_plan.seed, summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.exit_runs);
}

test "runtime atomic64 loader keeps loaded seed stable through selftest and exit" {
    var module = RuntimeAtomic64Sample{};
    try module.init(load_plan.seed);

    const initialized = module.summary();
    const selftest = try module.runSelftest();
    try std.testing.expectEqualStrings(load_plan.expected_selftest_anchor, selftest.anchor);
    try std.testing.expectEqual(@as(usize, 5), selftest.operation_families.len);
    try std.testing.expect(selftest.checked_returning_paths);
    try std.testing.expect(selftest.checked_bitwise_paths);
    try std.testing.expect(selftest.checked_guard_paths);

    const after_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try expectCounterAndInitStable(initialized, after_selftest);
    try std.testing.expectEqual(@as(usize, 1), after_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), after_selftest.exit_runs);

    try module.exit();
    const after_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(initialized.counter_snapshot, after_exit.counter_snapshot);
    try std.testing.expectEqual(initialized.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
}

test "runtime atomic64 loader keeps direct exit without selftest explicit" {
    var module = RuntimeAtomic64Sample{};
    try module.init(-17);

    const before_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(i64, -17), before_exit.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);

    try module.exit();
    const after_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try expectCounterAndInitStable(before_exit, after_exit);
    try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
}

test "runtime atomic64 loader keeps post-selftest mutation explicit before exit" {
    var module = RuntimeAtomic64Sample{};
    try module.init(load_plan.seed);
    _ = try module.runSelftest();
    _ = try module.addCounter(9);

    const before_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(load_plan.seed + 9, before_exit.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);

    try module.exit();
    const after_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try expectCounterAndInitStable(before_exit, after_exit);
    try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
}

test "runtime atomic64 loader rejects re-init without disturbing summaries" {
    var initialized_module = RuntimeAtomic64Sample{};
    try initialized_module.init(91);

    const before_initialized_reinit = initialized_module.summary();
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init(7));
    const after_initialized_reinit = initialized_module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_module.stage());
    try expectCounterAndInitStable(before_initialized_reinit, after_initialized_reinit);
    try std.testing.expectEqual(
        before_initialized_reinit.selftest_runs,
        after_initialized_reinit.selftest_runs,
    );
    try std.testing.expectEqual(before_initialized_reinit.exit_runs, after_initialized_reinit.exit_runs);

    var selftested_module = RuntimeAtomic64Sample{};
    try selftested_module.init(-12);
    _ = try selftested_module.runSelftest();

    const before_selftested_reinit = selftested_module.summary();
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init(5));
    const after_selftested_reinit = selftested_module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftested_module.stage());
    try expectCounterAndInitStable(before_selftested_reinit, after_selftested_reinit);
    try std.testing.expectEqual(
        before_selftested_reinit.selftest_runs,
        after_selftested_reinit.selftest_runs,
    );
    try std.testing.expectEqual(before_selftested_reinit.exit_runs, after_selftested_reinit.exit_runs);

    var exited_module = RuntimeAtomic64Sample{};
    try exited_module.init(33);
    _ = try exited_module.runSelftest();
    try exited_module.exit();

    const before_exited_reinit = exited_module.summary();
    try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init(2));
    const after_exited_reinit = exited_module.summary();
    try std.testing.expectEqual(ModuleStage.exited, exited_module.stage());
    try expectCounterAndInitStable(before_exited_reinit, after_exited_reinit);
    try std.testing.expectEqual(before_exited_reinit.selftest_runs, after_exited_reinit.selftest_runs);
    try std.testing.expectEqual(before_exited_reinit.exit_runs, after_exited_reinit.exit_runs);
}

test "runtime atomic64 loader rejects re-selftest without disturbing summaries" {
    var module = RuntimeAtomic64Sample{};
    try module.init(23);
    _ = try module.runSelftest();

    const before_rejected_selftest = module.summary();
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    const after_rejected_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try expectCounterAndInitStable(before_rejected_selftest, after_rejected_selftest);
    try std.testing.expectEqual(before_rejected_selftest.selftest_runs, after_rejected_selftest.selftest_runs);
    try std.testing.expectEqual(before_rejected_selftest.exit_runs, after_rejected_selftest.exit_runs);

    try module.exit();
    const before_rejected_exit_selftest = module.summary();
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    const after_rejected_exit_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try expectCounterAndInitStable(before_rejected_exit_selftest, after_rejected_exit_selftest);
    try std.testing.expectEqual(
        before_rejected_exit_selftest.selftest_runs,
        after_rejected_exit_selftest.selftest_runs,
    );
    try std.testing.expectEqual(
        before_rejected_exit_selftest.exit_runs,
        after_rejected_exit_selftest.exit_runs,
    );
}

test "runtime atomic64 loader rejects re-exit without disturbing exited summaries" {
    var initialized_module = RuntimeAtomic64Sample{};
    try initialized_module.init(17);
    try initialized_module.exit();

    const before_initialized_reexit = initialized_module.summary();
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.exit());
    const after_initialized_reexit = initialized_module.summary();
    try std.testing.expectEqual(ModuleStage.exited, initialized_module.stage());
    try expectCounterAndInitStable(before_initialized_reexit, after_initialized_reexit);
    try std.testing.expectEqual(before_initialized_reexit.selftest_runs, after_initialized_reexit.selftest_runs);
    try std.testing.expectEqual(before_initialized_reexit.exit_runs, after_initialized_reexit.exit_runs);

    var selftested_module = RuntimeAtomic64Sample{};
    try selftested_module.init(-8);
    _ = try selftested_module.runSelftest();
    try selftested_module.exit();

    const before_selftested_reexit = selftested_module.summary();
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.exit());
    const after_selftested_reexit = selftested_module.summary();
    try std.testing.expectEqual(ModuleStage.exited, selftested_module.stage());
    try expectCounterAndInitStable(before_selftested_reexit, after_selftested_reexit);
    try std.testing.expectEqual(before_selftested_reexit.selftest_runs, after_selftested_reexit.selftest_runs);
    try std.testing.expectEqual(before_selftested_reexit.exit_runs, after_selftested_reexit.exit_runs);
}
