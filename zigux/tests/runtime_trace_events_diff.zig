const std = @import("std");
const sample = @import("runtime_trace_events_sample");

test "runtime trace-events diff gate replays the Linux sample's main-thread payload families" {
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
}

test "runtime trace-events diff gate keeps function-callback registration balance explicit" {
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

    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 1), module.registration_depth);
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 0), module.registration_depth);
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());
}
