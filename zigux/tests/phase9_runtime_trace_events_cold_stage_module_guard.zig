const std = @import("std");
const sample = @import("../../samples/zigux/runtime_trace_events.zig");

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

test "phase9 trace-events module boundary keeps cold-stage registration failures fail-closed" {
    var module = sample.RuntimeTraceEventsSample{};

    const cold_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.cold, cold_summary.stage);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.total_events);
    try std.testing.expectEqual(@as(?usize, null), cold_summary.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), cold_summary.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), cold_summary.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.register_transitions);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.unregister_transitions);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.exit_runs);
    try std.testing.expectEqual(@as(i32, -1), cold_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), cold_summary.last_fn_count);
    try std.testing.expect(!cold_summary.saw_vararg_payload);
    try std.testing.expect(!cold_summary.saw_rel_loc_payload);
    try std.testing.expect(!cold_summary.saw_conditional_path);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.main_thread_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.function_thread_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_register_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_unregister_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_foo_bar_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_random_choice_message);
    try std.testing.expectEqual(@as(?usize, null), cold_summary.last_main_vararg_array_length);
    try std.testing.expectEqual(@as(?bool, null), cold_summary.last_main_vararg_array_terminator_zero);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_template_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_template_cond_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_template_print_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_relative_location_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_function_foo_bar_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_function_template_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_format_template);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());

    const cold_after = module.summary();
    try expectSummaryStable(cold_summary, cold_after);
}
