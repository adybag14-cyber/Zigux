const std = @import("std");
const sample = @import("runtime_kretprobe_sample");

const OverlapCase = struct {
    name: []const u8,
    entries: [2]i64,
    inner_retval: i32,
    inner_return_timestamp_ns: i64,
    inner_expected_duration_ns: i64,
    outer_retval: i32,
    outer_return_timestamp_ns: i64,
    outer_expected_duration_ns: i64,
};

pub const ThresholdReplaySummary = struct {
    iterations: usize,
    checksum: u64,
    final_stage: sample.ModuleStage,
    final_completed_instances: usize,
    final_last_retval: ?i32,
    final_registration_runs: usize,
    final_unregistration_runs: usize,
    final_exit_runs: usize,
};

fn mixChecksum(checksum: *u64, value: u64) void {
    checksum.* = checksum.* *% 0x9e37_79b1_85eb_ca87 +% value;
}

fn mixChecksumI64(checksum: *u64, value: i64) void {
    mixChecksum(checksum, @bitCast(value));
}

fn mixChecksumI32(checksum: *u64, value: i32) void {
    mixChecksum(checksum, @bitCast(@as(i64, value)));
}

fn mixChecksumUsize(checksum: *u64, value: usize) void {
    mixChecksum(checksum, @intCast(value));
}

fn expectSnapshotStable(
    before: sample.LifecycleSnapshot,
    after: sample.LifecycleSnapshot,
) !void {
    try std.testing.expectEqual(before.stage, after.stage);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
    try std.testing.expectEqual(before.selftest_runs, after.selftest_runs);
    try std.testing.expectEqual(before.exit_runs, after.exit_runs);
    try std.testing.expectEqual(before.registration_runs, after.registration_runs);
    try std.testing.expectEqual(before.unregistration_runs, after.unregistration_runs);
    try std.testing.expectEqual(before.probe_registered, after.probe_registered);
    try std.testing.expectEqual(before.active_instances, after.active_instances);
    try std.testing.expectEqual(before.completed_instances, after.completed_instances);
    try std.testing.expectEqual(before.last_retval, after.last_retval);
    try std.testing.expectEqual(before.last_entry_timestamp_ns, after.last_entry_timestamp_ns);
    try std.testing.expectEqual(before.last_return_timestamp_ns, after.last_return_timestamp_ns);
    try std.testing.expectEqual(before.last_duration_ns, after.last_duration_ns);
    try std.testing.expectEqual(
        before.oldest_active_entry_timestamp_ns,
        after.oldest_active_entry_timestamp_ns,
    );
    try std.testing.expectEqual(
        before.newest_active_entry_timestamp_ns,
        after.newest_active_entry_timestamp_ns,
    );
}

fn expectOverlapCase(case: OverlapCase) !void {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();
    try module.registerProbe();
    try module.recordEntryAt(case.entries[0]);
    try module.recordEntryAt(case.entries[1]);

    const before_returns = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_returns.stage);
    try std.testing.expectEqual(@as(usize, 2), before_returns.active_instances);
    try std.testing.expectEqual(@as(?i64, case.entries[0]), before_returns.oldest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, case.entries[1]), before_returns.newest_active_entry_timestamp_ns);

    try module.recordReturnAt(case.inner_retval, case.inner_return_timestamp_ns);
    const after_inner_return = module.lifecycleSnapshot();
    try std.testing.expectEqual(@as(usize, 1), after_inner_return.active_instances);
    try std.testing.expectEqual(@as(usize, 1), after_inner_return.completed_instances);
    try std.testing.expectEqual(@as(?i32, case.inner_retval), after_inner_return.last_retval);
    try std.testing.expectEqual(
        @as(?i64, case.inner_expected_duration_ns),
        after_inner_return.last_duration_ns,
    );
    try std.testing.expectEqual(@as(?i64, case.entries[0]), after_inner_return.oldest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, case.entries[0]), after_inner_return.newest_active_entry_timestamp_ns);

    try module.recordReturnAt(case.outer_retval, case.outer_return_timestamp_ns);
    const after_outer_return = module.lifecycleSnapshot();
    try std.testing.expectEqual(@as(usize, 0), after_outer_return.active_instances);
    try std.testing.expectEqual(@as(usize, 2), after_outer_return.completed_instances);
    try std.testing.expectEqual(@as(?i32, case.outer_retval), after_outer_return.last_retval);
    try std.testing.expectEqual(
        @as(?i64, case.outer_expected_duration_ns),
        after_outer_return.last_duration_ns,
    );
    try std.testing.expectEqual(@as(?i64, null), after_outer_return.oldest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, null), after_outer_return.newest_active_entry_timestamp_ns);
}

pub fn runThresholdReplay(iterations: usize) !ThresholdReplaySummary {
    if (iterations == 0) return error.EmptyThresholdReplayBatch;

    var checksum: u64 = 0;
    var final_stage = sample.ModuleStage.cold;
    var final_completed_instances: usize = 0;
    var final_last_retval: ?i32 = null;
    var final_registration_runs: usize = 0;
    var final_unregistration_runs: usize = 0;
    var final_exit_runs: usize = 0;

    var iteration: usize = 0;
    while (iteration < iterations) : (iteration += 1) {
        const offset: i64 = @intCast(iteration * 100);
        var module = sample.RuntimeKretprobeSample{};
        try module.init();
        const selftest = try module.runSelftest();
        try module.registerProbe();
        try module.recordEntryAt(10 + offset);
        try module.recordEntryAt(45 + offset);
        try module.recordReturnAt(@intCast(7 + iteration), 90 + offset);
        try module.recordReturnAt(@intCast(19 + iteration), 170 + offset);
        try module.unregisterProbe();

        const before_exit = module.lifecycleSnapshot();
        try module.exit();
        const after_exit = module.lifecycleSnapshot();

        mixChecksumUsize(&checksum, iteration + 1);
        mixChecksumI64(&checksum, before_exit.last_entry_timestamp_ns orelse -1);
        mixChecksumI64(&checksum, before_exit.last_return_timestamp_ns orelse -1);
        mixChecksumI64(&checksum, before_exit.last_duration_ns orelse -1);
        mixChecksumI32(&checksum, before_exit.last_retval orelse -1);
        mixChecksumUsize(&checksum, before_exit.completed_instances);
        mixChecksumUsize(&checksum, before_exit.registration_runs);
        mixChecksumUsize(&checksum, before_exit.unregistration_runs);
        mixChecksumUsize(&checksum, after_exit.exit_runs);
        mixChecksumUsize(&checksum, @intFromBool(selftest.checked_registration_paths));

        final_stage = after_exit.stage;
        final_completed_instances = after_exit.completed_instances;
        final_last_retval = after_exit.last_retval;
        final_registration_runs = after_exit.registration_runs;
        final_unregistration_runs = after_exit.unregistration_runs;
        final_exit_runs = after_exit.exit_runs;
    }

    return .{
        .iterations = iterations,
        .checksum = checksum,
        .final_stage = final_stage,
        .final_completed_instances = final_completed_instances,
        .final_last_retval = final_last_retval,
        .final_registration_runs = final_registration_runs,
        .final_unregistration_runs = final_unregistration_runs,
        .final_exit_runs = final_exit_runs,
    };
}

test "runtime kretprobe diff gate replays bounded overlapping return-instance expectations" {
    const cases = [_]OverlapCase{
        .{
            .name = "sparse overlapping return timestamps keep the most recent entry visible first",
            .entries = .{ 10, 35 },
            .inner_retval = 7,
            .inner_return_timestamp_ns = 80,
            .inner_expected_duration_ns = 45,
            .outer_retval = 11,
            .outer_return_timestamp_ns = 150,
            .outer_expected_duration_ns = 140,
        },
        .{
            .name = "later entry windows stay ordered when the outer return stretches longer",
            .entries = .{ 101, 145 },
            .inner_retval = 23,
            .inner_return_timestamp_ns = 181,
            .inner_expected_duration_ns = 36,
            .outer_retval = 29,
            .outer_return_timestamp_ns = 260,
            .outer_expected_duration_ns = 159,
        },
    };

    for (cases) |case| {
        _ = case.name;
        try expectOverlapCase(case);
    }
}

test "runtime kretprobe diff gate keeps post-selftest reusable probe cycles and exit guards explicit" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();

    const selftest = try module.runSelftest();
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", selftest.anchor);
    try std.testing.expect(selftest.checked_registration_paths);
    try std.testing.expect(selftest.checked_return_paths);
    try std.testing.expect(selftest.checked_lifecycle_guards);

    try module.registerProbe();
    try module.recordEntryAt(20);
    try module.recordReturnAt(17, 71);
    try module.unregisterProbe();

    const before_exit = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_exit.stage);
    try std.testing.expectEqual(@as(usize, 2), before_exit.registration_runs);
    try std.testing.expectEqual(@as(usize, 2), before_exit.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 2), before_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 17), before_exit.last_retval);
    try std.testing.expectEqual(@as(?i64, 51), before_exit.last_duration_ns);

    try module.exit();
    const after_exit = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_exit.completed_instances, after_exit.completed_instances);
    try std.testing.expectEqual(before_exit.last_retval, after_exit.last_retval);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerProbe());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.recordEntry());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.recordReturn(5));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterProbe());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try expectSnapshotStable(after_exit, module.lifecycleSnapshot());
}

test "runtime kretprobe diff gate rejects an empty threshold replay batch" {
    try std.testing.expectError(error.EmptyThresholdReplayBatch, runThresholdReplay(0));
}

test "runtime kretprobe diff gate keeps a deterministic threshold replay batch ready for future runtime baselines" {
    const single = try runThresholdReplay(1);
    const repeated = try runThresholdReplay(4);

    try std.testing.expectEqual(@as(usize, 1), single.iterations);
    try std.testing.expectEqual(@as(usize, 4), repeated.iterations);
    try std.testing.expectEqual(sample.ModuleStage.exited, single.final_stage);
    try std.testing.expectEqual(sample.ModuleStage.exited, repeated.final_stage);
    try std.testing.expectEqual(@as(usize, 3), single.final_completed_instances);
    try std.testing.expectEqual(@as(usize, 3), repeated.final_completed_instances);
    try std.testing.expectEqual(@as(?i32, 19), single.final_last_retval);
    try std.testing.expectEqual(@as(?i32, 22), repeated.final_last_retval);
    try std.testing.expectEqual(@as(usize, 2), single.final_registration_runs);
    try std.testing.expectEqual(@as(usize, 2), repeated.final_registration_runs);
    try std.testing.expectEqual(@as(usize, 2), single.final_unregistration_runs);
    try std.testing.expectEqual(@as(usize, 2), repeated.final_unregistration_runs);
    try std.testing.expectEqual(@as(usize, 1), single.final_exit_runs);
    try std.testing.expectEqual(@as(usize, 1), repeated.final_exit_runs);
    try std.testing.expect(repeated.checksum != single.checksum);
    try std.testing.expectEqualDeep(repeated, try runThresholdReplay(4));
}
