const std = @import("std");
const sample = @import("runtime_trace_events_sample");

fn expectSummaryStable(
    before: sample.RuntimeTraceEventsSummary,
    after: sample.RuntimeTraceEventsSummary,
) !void {
    try std.testing.expectEqual(before.stage, after.stage);
    try std.testing.expectEqual(before.registration_depth, after.registration_depth);
    try std.testing.expectEqual(before.main_iterations, after.main_iterations);
    try std.testing.expectEqual(before.fn_iterations, after.fn_iterations);
    try std.testing.expectEqual(before.main_thread_events, after.main_thread_events);
    try std.testing.expectEqual(before.fn_thread_events, after.fn_thread_events);
    try std.testing.expectEqual(before.total_events, after.total_events);
    try std.testing.expectEqual(before.last_main_emitted_events, after.last_main_emitted_events);
    try std.testing.expectEqual(before.last_fn_emitted_events, after.last_fn_emitted_events);
    try std.testing.expectEqual(before.last_main_conditional_event_count, after.last_main_conditional_event_count);
    try std.testing.expectEqual(before.register_transitions, after.register_transitions);
    try std.testing.expectEqual(before.unregister_transitions, after.unregister_transitions);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
    try std.testing.expectEqual(before.selftest_runs, after.selftest_runs);
    try std.testing.expectEqual(before.exit_runs, after.exit_runs);
    try std.testing.expectEqual(before.last_main_count, after.last_main_count);
    try std.testing.expectEqual(before.last_fn_count, after.last_fn_count);
    try std.testing.expectEqual(before.saw_vararg_payload, after.saw_vararg_payload);
    try std.testing.expectEqual(before.saw_rel_loc_payload, after.saw_rel_loc_payload);
    try std.testing.expectEqual(before.saw_conditional_path, after.saw_conditional_path);
    try std.testing.expectEqual(before.last_main_vararg_array_length, after.last_main_vararg_array_length);
    try std.testing.expectEqual(before.last_main_vararg_array_terminator_zero, after.last_main_vararg_array_terminator_zero);
    try std.testing.expect(std.meta.eql(before.main_thread_label, after.main_thread_label));
    try std.testing.expect(std.meta.eql(before.function_thread_label, after.function_thread_label));
    try std.testing.expect(std.meta.eql(before.last_register_label, after.last_register_label));
    try std.testing.expect(std.meta.eql(before.last_unregister_label, after.last_unregister_label));
    try std.testing.expect(std.meta.eql(before.last_main_foo_bar_message, after.last_main_foo_bar_message));
    try std.testing.expect(std.meta.eql(before.last_main_random_choice_message, after.last_main_random_choice_message));
    try std.testing.expect(std.meta.eql(before.last_main_template_message, after.last_main_template_message));
    try std.testing.expect(std.meta.eql(before.last_main_conditional_message, after.last_main_conditional_message));
    try std.testing.expect(std.meta.eql(before.last_main_template_cond_message, after.last_main_template_cond_message));
    try std.testing.expect(std.meta.eql(before.last_main_template_print_message, after.last_main_template_print_message));
    try std.testing.expect(std.meta.eql(before.last_main_relative_location_message, after.last_main_relative_location_message));
    try std.testing.expect(std.meta.eql(before.last_function_template_message, after.last_function_template_message));
    try std.testing.expect(std.meta.eql(before.last_function_foo_bar_message, after.last_function_foo_bar_message));
    try std.testing.expect(std.meta.eql(before.last_format_template, after.last_format_template));
}

test "runtime trace-events sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeTraceEventsSample.descriptor();
    try std.testing.expectEqualStrings("runtime_trace_events", descriptor.name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime trace-events sample keeps selftest summary replay explicit at the module boundary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    const selftest_summary = try module.runSelftest();
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", selftest_summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), selftest_summary.event_families.len);
    try std.testing.expectEqual(sample.EventFamily.foo_bar, selftest_summary.event_families[0]);
    try std.testing.expectEqual(sample.EventFamily.template, selftest_summary.event_families[1]);
    try std.testing.expectEqual(sample.EventFamily.conditional, selftest_summary.event_families[2]);
    try std.testing.expectEqual(sample.EventFamily.relative_location, selftest_summary.event_families[3]);
    try std.testing.expectEqual(sample.EventFamily.function_callback, selftest_summary.event_families[4]);
    try std.testing.expectEqual(@as(usize, 6), selftest_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), selftest_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), selftest_summary.total_events);
    try std.testing.expect(selftest_summary.conditional_paths_checked);
    try std.testing.expect(selftest_summary.registration_paths_checked);

    const selftest_snapshot = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, selftest_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), selftest_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_snapshot.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), selftest_snapshot.register_transitions);
    try std.testing.expectEqual(@as(i32, 0), selftest_snapshot.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), selftest_snapshot.last_fn_count);
    try std.testing.expect(selftest_snapshot.saw_vararg_payload);
    try std.testing.expect(selftest_snapshot.saw_rel_loc_payload);
    try std.testing.expect(selftest_snapshot.saw_conditional_path);
}

test "runtime trace-events sample keeps lifecycle summary replay explicit at the module boundary" {
    var module = sample.RuntimeTraceEventsSample{};

    const cold_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.cold, cold_summary.stage);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.registration_depth);
    try std.testing.expectEqual(@as(i32, -1), cold_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), cold_summary.last_fn_count);
    try std.testing.expectEqual(@as(?usize, null), cold_summary.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), cold_summary.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), cold_summary.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_register_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_unregister_label);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());

    try module.init();
    const initialized_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, initialized_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.registration_depth);
    try std.testing.expectEqualStrings("event-sample", initialized_summary.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("event-sample-fn", initialized_summary.function_thread_label orelse return error.ExpectedFunctionPayload);

    _ = try module.runSelftest();
    const selftest_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, selftest_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_summary.registration_depth);

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), exited_summary.registration_depth);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(3));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());
}

test "runtime trace-events sample keeps initialized-stage exit replay explicit at the module boundary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    const before_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 0), before_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 0), before_exit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), before_exit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 0), before_exit.total_events);

    try module.exit();

    const after_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(before_exit.registration_depth, after_exit.registration_depth);
    try std.testing.expectEqual(before_exit.main_iterations, after_exit.main_iterations);
    try std.testing.expectEqual(before_exit.fn_iterations, after_exit.fn_iterations);
    try std.testing.expectEqual(before_exit.main_thread_events, after_exit.main_thread_events);
    try std.testing.expectEqual(before_exit.fn_thread_events, after_exit.fn_thread_events);
    try std.testing.expectEqual(before_exit.total_events, after_exit.total_events);
    try std.testing.expectEqual(before_exit.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_exit.last_register_label, after_exit.last_register_label);
    try std.testing.expectEqual(before_exit.last_unregisterLabel, after_exit.last_unregisterLabel);
}
