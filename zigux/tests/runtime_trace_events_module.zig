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
    const before_exit_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_exit_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), before_exit_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exit_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit_summary.registration_depth);
    try std.testing.expectEqualStrings("Some times print", before_exit_summary.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", before_exit_summary.last_main_template_cond_message orelse return error.ExpectedMainPayload);

    try module.exit();
    const exited_summary = module.summary();
    var expected_after_exit = before_exit_summary;
    expected_after_exit.stage = sample.ModuleStage.exited;
    expected_after_exit.exit_runs += 1;
    try expectSummaryStable(expected_after_exit, exited_summary);
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
    try std.testing.expectEqual(before_exit.last_unregister_label, after_exit.last_unregister_label);
}

test "runtime trace-events sample keeps rejected re-init rollback explicit at the module boundary" {
    var initialized_module = sample.RuntimeTraceEventsSample{};
    try initialized_module.init();

    const before_initialized_reinit = initialized_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_initialized_reinit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.registration_depth);
    try std.testing.expectEqualStrings("event-sample", before_initialized_reinit.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("event-sample-fn", before_initialized_reinit.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init());

    const after_initialized_reinit = initialized_module.summary();
    try expectSummaryStable(before_initialized_reinit, after_initialized_reinit);

    var selftested_module = sample.RuntimeTraceEventsSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();

    const before_selftested_reinit = selftested_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_selftested_reinit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_reinit.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_reinit.registration_depth);
    try std.testing.expectEqualStrings("Some times print", before_selftested_reinit.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", before_selftested_reinit.last_main_template_cond_message orelse return error.ExpectedMainPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init());

    const after_selftested_reinit = selftested_module.summary();
    try expectSummaryStable(before_selftested_reinit, after_selftested_reinit);

    var exited_module = sample.RuntimeTraceEventsSample{};
    try exited_module.init();
    _ = try exited_module.runSelftest();
    try exited_module.exit();

    const before_exited_reinit = exited_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, before_exited_reinit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exited_reinit.registration_depth);

    try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init());

    const after_exited_reinit = exited_module.summary();
    try expectSummaryStable(before_exited_reinit, after_exited_reinit);
}

test "runtime trace-events sample keeps rejected re-selftest rollback explicit at the module boundary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    const before_rejected_selftest = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_rejected_selftest.stage);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_rejected_selftest.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_rejected_selftest.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.register_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.unregister_transitions);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const after_rejected_selftest = module.summary();
    try expectSummaryStable(before_rejected_selftest, after_rejected_selftest);

    try module.exit();

    const before_rejected_exit_selftest = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, before_rejected_exit_selftest.stage);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_rejected_exit_selftest.registration_depth);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const after_rejected_exit_selftest = module.summary();
    try expectSummaryStable(before_rejected_exit_selftest, after_rejected_exit_selftest);
}

test "runtime trace-events sample keeps rejected re-exit rollback explicit at the module boundary" {
    var initialized_module = sample.RuntimeTraceEventsSample{};
    try initialized_module.init();
    try initialized_module.exit();

    const before_initialized_reexit = initialized_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, before_initialized_reexit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reexit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reexit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reexit.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reexit.registration_depth);

    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.exit());

    const after_initialized_reexit = initialized_module.summary();
    try expectSummaryStable(before_initialized_reexit, after_initialized_reexit);

    var selftested_module = sample.RuntimeTraceEventsSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();
    try selftested_module.exit();

    const before_selftested_reexit = selftested_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, before_selftested_reexit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_reexit.registration_depth);
    try std.testing.expectEqualStrings("Some times print", before_selftested_reexit.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", before_selftested_reexit.last_main_template_cond_message orelse return error.ExpectedMainPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.exit());

    const after_selftested_reexit = selftested_module.summary();
    try expectSummaryStable(before_selftested_reexit, after_selftested_reexit);
}

test "runtime trace-events sample keeps direct-activity re-init and re-exit rollback explicit at the module boundary" {
    var initialized_module = sample.RuntimeTraceEventsSample{};
    try initialized_module.init();
    _ = try initialized_module.emitMainIteration(5);
    try initialized_module.registerFunctionThread();
    _ = try initialized_module.emitFunctionIteration(7);
    try initialized_module.unregisterFunctionThread();

    const before_initialized_reinit = initialized_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_initialized_reinit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 4), before_initialized_reinit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), before_initialized_reinit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 6), before_initialized_reinit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_initialized_reinit.last_main_count);
    try std.testing.expectEqual(@as(i32, 7), before_initialized_reinit.last_fn_count);
    try std.testing.expectEqualStrings("Mother Goose", before_initialized_reinit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_initialized_reinit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init());
    try expectSummaryStable(before_initialized_reinit, initialized_module.summary());

    try initialized_module.exit();
    const before_initialized_reexit = initialized_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, before_initialized_reexit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reexit.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.exit());
    try expectSummaryStable(before_initialized_reexit, initialized_module.summary());

    var selftested_module = sample.RuntimeTraceEventsSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();
    _ = try selftested_module.emitMainIteration(5);
    try selftested_module.registerFunctionThread();
    _ = try selftested_module.emitFunctionIteration(11);
    try selftested_module.unregisterFunctionThread();

    const before_selftested_reinit = selftested_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_selftested_reinit.stage);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_reinit.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_reinit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), before_selftested_reinit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), before_selftested_reinit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), before_selftested_reinit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_reinit.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_selftested_reinit.last_main_count);
    try std.testing.expectEqual(@as(i32, 11), before_selftested_reinit.last_fn_count);
    try std.testing.expectEqualStrings("Mother Goose", before_selftested_reinit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_selftested_reinit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init());
    try expectSummaryStable(before_selftested_reinit, selftested_module.summary());

    try selftested_module.exit();
    const before_selftested_reexit = selftested_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, before_selftested_reexit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.exit());
    try expectSummaryStable(before_selftested_reexit, selftested_module.summary());
}

test "runtime trace-events sample keeps duplicate registration and failed-exit rollback explicit at the module boundary" {
    var initialized_module = sample.RuntimeTraceEventsSample{};
    try initialized_module.init();
    try initialized_module.registerFunctionThread();

    const before_initialized_duplicate_registration = initialized_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_initialized_duplicate_registration.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_duplicate_registration.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_duplicate_registration.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_duplicate_registration.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_duplicate_registration.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_duplicate_registration.register_transitions);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_duplicate_registration.unregister_transitions);
    try std.testing.expectEqualStrings("event-sample", before_initialized_duplicate_registration.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("event-sample-fn", before_initialized_duplicate_registration.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", before_initialized_duplicate_registration.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), before_initialized_duplicate_registration.last_unregister_label);

    try std.testing.expectError(
        error.FunctionThreadAlreadyRegistered,
        initialized_module.registerFunctionThread(),
    );
    try expectSummaryStable(
        before_initialized_duplicate_registration,
        initialized_module.summary(),
    );

    const before_initialized_failed_exit = initialized_module.summary();
    try std.testing.expectError(error.OutstandingRegistration, initialized_module.exit());
    try expectSummaryStable(before_initialized_failed_exit, initialized_module.summary());

    try initialized_module.unregisterFunctionThread();
    try initialized_module.exit();
    const initialized_after_exit = initialized_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, initialized_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_after_exit.exit_runs);

    var selftested_module = sample.RuntimeTraceEventsSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();
    try selftested_module.registerFunctionThread();

    const before_selftested_duplicate_registration = selftested_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_selftested_duplicate_registration.stage);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_duplicate_registration.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_duplicate_registration.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_duplicate_registration.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_duplicate_registration.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_duplicate_registration.register_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_duplicate_registration.unregister_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_duplicate_registration.fn_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_duplicate_registration.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), before_selftested_duplicate_registration.total_events);
    try std.testing.expectEqual(@as(?usize, 2), before_selftested_duplicate_registration.last_fn_emitted_events);
    try std.testing.expectEqual(@as(i32, 1), before_selftested_duplicate_registration.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", before_selftested_duplicate_registration.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_selftested_duplicate_registration.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me", before_selftested_duplicate_registration.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", before_selftested_duplicate_registration.last_function_template_message orelse return error.ExpectedFunctionPayload);

    try std.testing.expectError(
        error.FunctionThreadAlreadyRegistered,
        selftested_module.registerFunctionThread(),
    );
    try expectSummaryStable(
        before_selftested_duplicate_registration,
        selftested_module.summary(),
    );

    const before_selftested_failed_exit = selftested_module.summary();
    try std.testing.expectError(error.OutstandingRegistration, selftested_module.exit());
    try expectSummaryStable(before_selftested_failed_exit, selftested_module.summary());

    const replayed_fn = try selftested_module.emitFunctionIteration(11);
    try std.testing.expectEqual(@as(usize, 2), replayed_fn);
    try selftested_module.unregisterFunctionThread();
    try selftested_module.exit();
    const selftested_after_exit = selftested_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, selftested_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_after_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), selftested_after_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 4), selftested_after_exit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 10), selftested_after_exit.total_events);
    try std.testing.expectEqual(@as(?usize, 2), selftested_after_exit.last_fn_emitted_events);
    try std.testing.expectEqual(@as(i32, 11), selftested_after_exit.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", selftested_after_exit.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", selftested_after_exit.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me", selftested_after_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", selftested_after_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);
}
