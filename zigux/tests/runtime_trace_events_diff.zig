const std = @import("std");
const sample = @import("runtime_trace_events_sample");

test "runtime trace-events diff gate replays the Linux sample's concrete main-thread payload literals" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    const emitted = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 6), emitted);
    try std.testing.expectEqual(@as(usize, 1), module.main_iterations);
    try std.testing.expectEqual(@as(usize, 6), module.total_events);
    try std.testing.expectEqual(@as(i32, 7), module.last_main_count);
    try std.testing.expect(module.saw_vararg_payload);
    try std.testing.expect(module.saw_rel_loc_payload);
    try std.testing.expect(module.saw_conditional_path);

    const payload = module.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", payload.foo_bar_message);
    try std.testing.expectEqualStrings("HELLO", payload.template_message);
    try std.testing.expectEqualStrings("Some times print", payload.conditional_message);
    try std.testing.expectEqualStrings("prints other times", payload.template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", payload.template_print_message);
    try std.testing.expectEqualStrings("Hello __rel_loc", payload.relative_location_message);
    try std.testing.expectEqualStrings("iter=%d", payload.format_template);
}

test "runtime trace-events diff gate keeps function-callback registration balance and payload labels explicit" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(0));

    try module.registerFunctionThread();
    try module.registerFunctionThread();
    try std.testing.expectEqual(@as(usize, 2), module.registration_depth);

    const emitted = try module.emitFunctionIteration(9);
    try std.testing.expectEqual(@as(usize, 2), emitted);
    try std.testing.expectEqual(@as(usize, 1), module.fn_iterations);
    try std.testing.expectEqual(@as(usize, 2), module.total_events);
    try std.testing.expectEqual(@as(i32, 9), module.last_fn_count);

    const payload = module.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", payload.template_message);

    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 1), module.registration_depth);
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 0), module.registration_depth);
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());
}