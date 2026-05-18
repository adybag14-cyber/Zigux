const std = @import("std");
const trace_events = @import("runtime_trace_events.zig");

const ModuleStage = trace_events.ModuleStage;
const RuntimeTraceEventsSummary = trace_events.RuntimeTraceEventsSummary;
const RuntimeTraceEventsSample = trace_events.RuntimeTraceEventsSample;

fn expectSummaryStable(before: RuntimeTraceEventsSummary, after: RuntimeTraceEventsSummary) !void {
    try std.testing.expect(std.meta.eql(before, after));
}

test "phase9 trace-events sample keeps unregistered function-thread failures fail-closed" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    const initialized_before = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_before.stage);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.main_iterations);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.fn_iterations);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.total_events);
    try std.testing.expectEqual(@as(?usize, null), initialized_before.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), initialized_before.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), initialized_before.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(usize, 1), initialized_before.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.exit_runs);
    try std.testing.expectEqual(@as(i32, -1), initialized_before.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), initialized_before.last_fn_count);
    try std.testing.expect(!initialized_before.saw_vararg_payload);
    try std.testing.expect(!initialized_before.saw_rel_loc_payload);
    try std.testing.expect(!initialized_before.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", initialized_before.main_thread_label orelse return error.ExpectedMainThreadLabel);
    try std.testing.expectEqualStrings("event-sample-fn", initialized_before.function_thread_label orelse return error.ExpectedFunctionThreadLabel);
    try std.testing.expectEqual(@as(?[]const u8, null), initialized_before.last_register_label);
    try std.testing.expectEqual(@as(?[]const u8, null), initialized_before.last_unregister_label);

    try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(3));
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());

    const initialized_after = module.summary();
    try expectSummaryStable(initialized_before, initialized_after);

    _ = try module.runSelftest();
    _ = try module.emitMainIteration(5);

    const selftest_complete_before = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_complete_before.stage);
    try std.testing.expectEqual(@as(usize, 0), selftest_complete_before.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), selftest_complete_before.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), selftest_complete_before.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), selftest_complete_before.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), selftest_complete_before.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 12), selftest_complete_before.total_events);
    try std.testing.expectEqual(@as(?usize, 4), selftest_complete_before.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), selftest_complete_before.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 0), selftest_complete_before.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(usize, 1), selftest_complete_before.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_complete_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_complete_before.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), selftest_complete_before.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), selftest_complete_before.last_fn_count);
    try std.testing.expect(selftest_complete_before.saw_vararg_payload);
    try std.testing.expect(selftest_complete_before.saw_rel_loc_payload);
    try std.testing.expect(selftest_complete_before.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", selftest_complete_before.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", selftest_complete_before.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("hello", selftest_complete_before.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Mother Goose", selftest_complete_before.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 0), selftest_complete_before.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(selftest_complete_before.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", selftest_complete_before.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), selftest_complete_before.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), selftest_complete_before.last_main_template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", selftest_complete_before.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", selftest_complete_before.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", selftest_complete_before.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", selftest_complete_before.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("iter=%d", selftest_complete_before.last_format_template orelse return error.ExpectedMainPayload);

    try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(7));
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());

    const selftest_complete_after = module.summary();
    try expectSummaryStable(selftest_complete_before, selftest_complete_after);

    try module.exit();

    const exited_before = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, exited_before.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_before.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), exited_before.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), exited_before.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), exited_before.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), exited_before.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), exited_before.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 12), exited_before.total_events);
    try std.testing.expectEqual(@as(?usize, 4), exited_before.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), exited_before.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 0), exited_before.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(usize, 1), exited_before.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_before.selftest_runs);
    try std.testing.expectEqual(@as(i32, 5), exited_before.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), exited_before.last_fn_count);
    try std.testing.expect(selftest_complete_before.saw_vararg_payload == exited_before.saw_vararg_payload);
    try std.testing.expect(selftest_complete_before.saw_rel_loc_payload == exited_before.saw_rel_loc_payload);
    try std.testing.expect(selftest_complete_before.saw_conditional_path == exited_before.saw_conditional_path);
    try std.testing.expectEqualStrings(selftest_complete_before.last_register_label orelse return error.ExpectedRegisterLabel, exited_before.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings(selftest_complete_before.last_unregister_label orelse return error.ExpectedUnregisterLabel, exited_before.last_unregister_label orelse return error.ExpectedUnregisterLabel);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(9));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(11));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());

    const exited_after = module.summary();
    try expectSummaryStable(exited_before, exited_after);
}
