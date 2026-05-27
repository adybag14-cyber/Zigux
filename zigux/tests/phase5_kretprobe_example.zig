const std = @import("std");
const sample = @import("kretprobe_example_sample");

test "phase 5 kretprobe sample stays in the reference-sample lane" {
    const descriptor = sample.KretprobeExampleSample.descriptor();
    const contract = sample.KretprobeExampleSample.reviewContract();
    const expected_focus = [_]sample.SampleFocus{
        .symbol_selection,
        .entry_timestamp,
        .private_data_shape,
        .return_duration,
        .missed_summary,
        .ownership_and_lifetime,
    };
    const expected_non_goals = [_][]const u8{
        "register_kretprobe parity",
        "unregister_kretprobe parity",
        "pt_regs or regs_return_value parity",
        "loadable module wiring",
    };

    try std.testing.expectEqualStrings("kretprobe_example", descriptor.name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
    try std.testing.expectEqual(@as(usize, expected_focus.len), contract.focus.len);
    for (expected_focus, contract.focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
    try std.testing.expectEqual(@as(usize, expected_non_goals.len), contract.non_goals.len);
    for (expected_non_goals, contract.non_goals) |expected, actual| {
        try std.testing.expectEqualStrings(expected, actual);
    }
}

test "phase 5 kretprobe sample replays the bounded skip, return, and summary paths" {
    const contract = sample.KretprobeExampleSample.reviewContract();
    var module = sample.KretprobeExampleSample{};
    try module.init();
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqualStrings("kernel_clone", replay.symbol_name);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(module.privateDataSizeBytes(), replay.private_data_size_bytes);
    try std.testing.expectEqual(@as(usize, 42), replay.return_value);
    try std.testing.expectEqual(@as(i64, 75), replay.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), replay.nmissed);
    try std.testing.expectEqual(@as(usize, sample.KretprobeExampleSample.default_maxactive), replay.maxactive);
    try std.testing.expectEqual(@as(usize, contract.focus.len), replay.checked_focus.len);
    for (contract.focus, replay.checked_focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.replay_runs);
}

test "phase 5 kretprobe sample exports the live instance-budget contract" {
    const contract = sample.KretprobeExampleSample.instanceBudgetContract();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", contract.anchor);
    try std.testing.expectEqualStrings("func", contract.symbol_param_name);
    try std.testing.expectEqual(@as(u16, 0o644), contract.symbol_param_mode);
    try std.testing.expectEqualStrings("kernel_clone", contract.default_symbol_name);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), contract.private_data_word_bytes);
    try std.testing.expectEqual(sample.KretprobeExampleSample.default_maxactive, contract.default_maxactive);
    try std.testing.expect(contract.reports_return_value_and_duration);
    try std.testing.expect(contract.skips_kernel_threads_without_mm);
    try std.testing.expect(contract.nmissed_suggests_increasing_maxactive);
}

test "phase 5 kretprobe sample keeps contributor route packet explicit" {
    const routes = sample.KretprobeExampleSample.contributorRoutePacket();

    try std.testing.expectEqualStrings(sample.sample_selfcheck_route, routes.sample_selfcheck_route);
    try std.testing.expectEqualStrings(sample.focused_replay_route, routes.focused_replay_route);
    try std.testing.expectEqualStrings(sample.survey_guard_route, routes.survey_guard_route);
    try std.testing.expectEqualStrings(sample.instance_budget_companion_route, routes.instance_budget_companion_route);
    try std.testing.expectEqualStrings(sample.instance_budget_focused_route, routes.instance_budget_focused_route);
    try std.testing.expectEqualStrings(sample.probe_spec_companion_route, routes.probe_spec_companion_route);
    try std.testing.expectEqualStrings(sample.probe_spec_focused_route, routes.probe_spec_focused_route);
    try std.testing.expectEqualStrings(sample.shared_build_route, routes.shared_build_route);
}

test "phase 5 kretprobe sample keeps maxactive retargeting pre-init and explicit" {
    var module = sample.KretprobeExampleSample{};

    try std.testing.expectError(error.InvalidMaxactive, module.retargetMaxactive(0));
    try module.retargetMaxactive(3);
    try module.init();

    const replay = try module.runAnchorReplay();
    try std.testing.expectEqual(@as(usize, 3), module.maxactive);
    try std.testing.expectEqual(@as(usize, 3), replay.maxactive);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.retargetMaxactive(4));
}

test "phase 5 kretprobe sample keeps symbol retargeting and handler boundaries explicit" {
    var module = sample.KretprobeExampleSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, module.entryHandler(true, 100));
    try std.testing.expectError(error.InvalidSymbolName, module.retargetSymbol(""));

    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    try std.testing.expectEqualStrings("do_sys_openat2", module.symbol_name);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), module.privateDataSizeBytes());
    try std.testing.expect(!(try module.entryHandler(false, 11)));
    try std.testing.expectEqual(@as(usize, 1), module.skipped_kernel_threads);
    try std.testing.expect(try module.entryHandler(true, 100));
    try std.testing.expectEqual(sample.SampleStage.armed, module.stage());
    try std.testing.expectError(error.OutstandingProbeInstance, module.entryHandler(true, 120));

    const result = try module.retHandler(37, 145);
    try std.testing.expectEqual(@as(usize, 37), result.retval);
    try std.testing.expectEqual(@as(i64, 45), result.duration_ns);
    try std.testing.expectEqual(@as(usize, 37), module.last_retval);
    try std.testing.expectEqual(@as(i64, 45), module.last_duration_ns);

    try module.recordMissedInstance();
    try std.testing.expectEqual(@as(usize, 1), module.nmissed);
}

test "phase 5 kretprobe sample ownership replay keeps lifecycle snapshots explicit" {
    var module = sample.KretprobeExampleSample{};
    const replay = try module.runOwnershipReplay();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings(sample.KretprobeExampleSample.default_symbol_name, replay.symbol_name);
    try std.testing.expectEqual(sample.SampleStage.cold, replay.stage_snapshots[0].stage);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_snapshots[1].stage);
    try std.testing.expectEqual(sample.SampleStage.armed, replay.stage_snapshots[2].stage);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_snapshots[3].stage);
    try std.testing.expectEqual(sample.SampleStage.exited, replay.stage_snapshots[4].stage);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[0].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[1].active_instances);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[2].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[3].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[4].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[0].skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[1].skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].skipped_kernel_threads);
    try std.testing.expect(replay.stage_snapshots[2].entry_timestamp_armed);
    try std.testing.expect(!replay.stage_snapshots[3].entry_timestamp_armed);
    try std.testing.expect(!replay.stage_snapshots[4].entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[1].init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].replay_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[4].exit_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].nmissed);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(@as(usize, 42), replay.replay_return_value);
    try std.testing.expectEqual(@as(i64, 75), replay.replay_duration_ns);
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
}

test "phase 5 kretprobe sample makes ownership and teardown boundaries explicit" {
    var module = sample.KretprobeExampleSample{};

    try std.testing.expectEqual(sample.SampleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());

    try module.init();
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try std.testing.expect(try module.entryHandler(true, 200));
    try std.testing.expectError(error.OutstandingProbeInstance, module.exit());
    try std.testing.expectError(error.InvalidTimestampOrder, module.retHandler(9, 199));

    const recovered = try module.retHandler(9, 260);
    try std.testing.expectEqual(@as(i64, 60), recovered.duration_ns);
    try std.testing.expectEqual(@as(i64, -1), module.instance_data.entry_stamp_ns);
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), module.active_instances);
    try std.testing.expectEqual(@as(i64, -1), module.instance_data.entry_stamp_ns);

    const exited_summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 0), exited_summary.active_instances);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expect(!exited_summary.entry_timestamp_armed);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.entryHandler(true, 300));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.retHandler(11, 320));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.recordMissedInstance());
}
