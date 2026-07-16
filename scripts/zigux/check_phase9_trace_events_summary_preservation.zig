const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION=pass";
pub const self_test_pass_marker = "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "test \"phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay\" {",
    "try std.testing.expectEqual(@as(?usize, 4), before_failed_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), before_failed_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), before_failed_exit.last_main_conditional_event_count);",
    "try std.testing.expectEqualStrings(\"foo_bar_reg\", before_failed_exit.last_register_label orelse return error.ExpectedRegisterLabel);",
    "try std.testing.expectEqualStrings(\"foo_bar_unreg\", before_failed_exit.last_unregister_label orelse return error.ExpectedUnregisterLabel);",
    "try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit_main_replay.last_main_conditional_message);",
    "try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit_main_replay.last_main_template_cond_message);",
    "try std.testing.expectEqualStrings(\"Hello __rel_loc\", after_failed_exit_main_replay.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqual(@as(usize, 14), before_unregister.main_thread_events);",
    "try std.testing.expectEqual(@as(usize, 6), before_unregister.fn_thread_events);",
    "try std.testing.expectEqual(@as(usize, 20), before_unregister.total_events);",
    "try std.testing.expectEqualStrings(\"Look at me too\", before_unregister.last_function_template_message orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 20), before_exit.total_events);",
    "try std.testing.expectEqual(@as(?usize, 4), before_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(before_exit.unregister_transitions, after_exit.unregister_transitions);",
    "try std.testing.expectEqualStrings(before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload, after_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(before_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);",
    "test \"phase9 trace-events sample keeps initialized direct-activity exit rollback explicit before selftest replay\" {",
    "try expectSummaryStable(exited_before_rejected_ops, exited_after_rejected_ops);",
};

const markers_1 = [_][]const u8{
    "test \"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\" {",
    "try std.testing.expectEqual(@as(?usize, 4), before_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), before_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), before_exit.last_main_conditional_event_count);",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);",
    "try std.testing.expectEqual(@as(?[]const u8, null), before_exit.last_main_conditional_message);",
    "try std.testing.expectEqual(@as(?[]const u8, null), before_exit.last_main_template_cond_message);",
    "try std.testing.expectEqualStrings(\"Hello __rel_loc\", before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"iter=%d\", before_exit.last_format_template orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload, after_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(before_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqual(before_exit.last_main_conditional_message, after_exit.last_main_conditional_message);",
    "try std.testing.expectEqual(before_exit.last_main_template_cond_message, after_exit.last_main_template_cond_message);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(11));",
    "try std.testing.expect(std.meta.eql(after_exit, after_rejected_lifecycle));",
};

const markers_2 = [_][]const u8{
    "test \"phase9 trace-events sample keeps re-init rollback explicit across initialized, selftest-complete, and exited states\" {",
    "try std.testing.expectEqual(ModuleStage.initialized, before_initialized_reinit.stage);",
    "try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.init_runs);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init());",
    "try expectSummaryStable(before_initialized_reinit, after_initialized_reinit);",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, before_selftested_reinit.stage);",
    "try std.testing.expectEqual(@as(usize, 14), before_selftested_reinit.total_events);",
    "try std.testing.expectEqualStrings(\"Some times print\", before_selftested_reinit.last_main_conditional_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"prints other times\", before_selftested_reinit.last_main_template_cond_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init());",
    "try expectSummaryStable(before_selftested_reinit, after_selftested_reinit);",
    "try std.testing.expectEqual(ModuleStage.exited, before_exited_reinit.stage);",
    "try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.exit_runs);",
    "try std.testing.expectEqual(@as(?[]const u8, null), before_exited_reinit.last_main_conditional_message);",
    "try std.testing.expectEqual(@as(?[]const u8, null), before_exited_reinit.last_main_template_cond_message);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init());",
    "try expectSummaryStable(before_exited_reinit, after_exited_reinit);",
};

const markers_3 = [_][]const u8{
    "test \"phase9 trace-events sample keeps initialized direct-activity summary explicit across clean exit\" {",
    "try std.testing.expectEqual(@as(?usize, 4), before_exit.last_main_emitted_events);",
    "try std.testing.expectEqualStrings(\"Mother Goose\", before_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);",
    "try module.exit();",
    "try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);",
    "test \"phase9 trace-events sample keeps re-init rollback explicit after initialized, selftest-complete, and exited replay\" {",
    "try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init());",
    "try expectSummaryStable(before_initialized_reinit, initialized_module.summary());",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, before_selftested_reinit.stage);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init());",
    "try expectSummaryStable(before_selftested_reinit, selftested_module.summary());",
    "try std.testing.expectEqual(ModuleStage.exited, before_exited_reinit.stage);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init());",
    "try expectSummaryStable(before_exited_reinit, exited_module.summary());",
    "test \"phase9 trace-events sample keeps re-exit rollback explicit after initialized and selftest-complete replay\" {",
    "try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.exit());",
    "try expectSummaryStable(before_initialized_reexit, initialized_module.summary());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.exit());",
    "try expectSummaryStable(before_selftested_reexit, selftested_module.summary());",
};

const contracts = [_]FileContract{
    .{ .rel = "samples/zigux/runtime_trace_events_exit_rollback_guard.zig", .markers = &markers_0 },
    .{ .rel = "samples/zigux/runtime_trace_events_registration_reentry_gate.zig", .markers = &markers_1 },
    .{ .rel = "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig", .markers = &markers_2 },
    .{ .rel = "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig", .markers = &markers_3 },
};

const exact_markers_0 = [_][]const u8{
    "test \"phase9 trace-events sample keeps initialized direct-activity exit rollback explicit before selftest replay\" {",
};

const exact_markers_1 = [_][]const u8{
    "test \"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\" {",
};

const exact_markers_2 = [_][]const u8{
    "test \"phase9 trace-events sample keeps re-init rollback explicit across initialized, selftest-complete, and exited states\" {",
};

const exact_markers_3 = [_][]const u8{
    "test \"phase9 trace-events sample keeps re-exit rollback explicit after initialized and selftest-complete replay\" {",
};

const exact_contracts = [_]FileContract{
    .{ .rel = "samples/zigux/runtime_trace_events_exit_rollback_guard.zig", .markers = &exact_markers_0 },
    .{ .rel = "samples/zigux/runtime_trace_events_registration_reentry_gate.zig", .markers = &exact_markers_1 },
    .{ .rel = "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig", .markers = &exact_markers_2 },
    .{ .rel = "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig", .markers = &exact_markers_3 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
    for (exact_contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireExactLineCount(text, marker, 1);
    }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_MARKER_COUNT=75", .{});
    try guard.printLine(io, "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_EXACT_ONCE_COUNT=4", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try std.testing.expectEqual(@as(usize, 75), comptime blk: {
        var total: usize = 0;
        for (contracts) |contract| total += contract.markers.len;
        break :blk total;
    });
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_SELF_TEST=pass";
//
// const EXIT_ROLLBACK_REQUIRED_MARKERS = [_][]const u8{
//     "test \"phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay\" {",
//     "try std.testing.expectEqual(@as(?usize, 4), before_failed_exit.last_main_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, 2), before_failed_exit.last_fn_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, 0), before_failed_exit.last_main_conditional_event_count);",
//     "try std.testing.expectEqualStrings(\"foo_bar_reg\", before_failed_exit.last_register_label orelse return error.ExpectedRegisterLabel);",
//     "try std.testing.expectEqualStrings(\"foo_bar_unreg\", before_failed_exit.last_unregister_label orelse return error.ExpectedUnregisterLabel);",
//     "try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit_main_replay.last_main_conditional_message);",
//     "try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit_main_replay.last_main_template_cond_message);",
//     "try std.testing.expectEqualStrings(\"Hello __rel_loc\", after_failed_exit_main_replay.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqual(@as(usize, 14), before_unregister.main_thread_events);",
//     "try std.testing.expectEqual(@as(usize, 6), before_unregister.fn_thread_events);",
//     "try std.testing.expectEqual(@as(usize, 20), before_unregister.total_events);",
//     "try std.testing.expectEqualStrings(\"Look at me too\", before_unregister.last_function_template_message orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqual(@as(usize, 0), before_exit.registration_depth);",
//     "try std.testing.expectEqual(@as(usize, 20), before_exit.total_events);",
//     "try std.testing.expectEqual(@as(?usize, 4), before_exit.last_main_emitted_events);",
//     "try std.testing.expectEqual(before_exit.unregister_transitions, after_exit.unregister_transitions);",
//     "try std.testing.expectEqualStrings(before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload, after_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(before_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);",
//     "test \"phase9 trace-events sample keeps initialized direct-activity exit rollback explicit before selftest replay\" {",
//     "try expectSummaryStable(exited_before_rejected_ops, exited_after_rejected_ops);",
// };
//
// const REENTRY_REQUIRED_MARKERS = [_][]const u8{
//     "test \"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\" {",
//     "try std.testing.expectEqual(@as(?usize, 4), before_exit.last_main_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, 2), before_exit.last_fn_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, 0), before_exit.last_main_conditional_event_count);",
//     "try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);",
//     "try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);",
//     "try std.testing.expectEqual(@as(?[]const u8, null), before_exit.last_main_conditional_message);",
//     "try std.testing.expectEqual(@as(?[]const u8, null), before_exit.last_main_template_cond_message);",
//     "try std.testing.expectEqualStrings(\"Hello __rel_loc\", before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"iter=%d\", before_exit.last_format_template orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload, after_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(before_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqual(before_exit.last_main_conditional_message, after_exit.last_main_conditional_message);",
//     "try std.testing.expectEqual(before_exit.last_main_template_cond_message, after_exit.last_main_template_cond_message);",
//     "try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());",
//     "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(11));",
//     "try std.testing.expect(std.meta.eql(after_exit, after_rejected_lifecycle));",
// };
//
// const REINIT_ROLLBACK_REQUIRED_MARKERS = [_][]const u8{
//     "test \"phase9 trace-events sample keeps re-init rollback explicit across initialized, selftest-complete, and exited states\" {",
//     "try std.testing.expectEqual(ModuleStage.initialized, before_initialized_reinit.stage);",
//     "try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.registration_depth);",
//     "try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.init_runs);",
//     "try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init());",
//     "try expectSummaryStable(before_initialized_reinit, after_initialized_reinit);",
//     "try std.testing.expectEqual(ModuleStage.selftest_complete, before_selftested_reinit.stage);",
//     "try std.testing.expectEqual(@as(usize, 14), before_selftested_reinit.total_events);",
//     "try std.testing.expectEqualStrings(\"Some times print\", before_selftested_reinit.last_main_conditional_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"prints other times\", before_selftested_reinit.last_main_template_cond_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init());",
//     "try expectSummaryStable(before_selftested_reinit, after_selftested_reinit);",
//     "try std.testing.expectEqual(ModuleStage.exited, before_exited_reinit.stage);",
//     "try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.exit_runs);",
//     "try std.testing.expectEqual(@as(?[]const u8, null), before_exited_reinit.last_main_conditional_message);",
//     "try std.testing.expectEqual(@as(?[]const u8, null), before_exited_reinit.last_main_template_cond_message);",
//     "try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init());",
//     "try expectSummaryStable(before_exited_reinit, after_exited_reinit);",
// };
//
// const REINIT_REEXIT_REQUIRED_MARKERS = [_][]const u8{
//     "test \"phase9 trace-events sample keeps initialized direct-activity summary explicit across clean exit\" {",
//     "try std.testing.expectEqual(@as(?usize, 4), before_exit.last_main_emitted_events);",
//     "try std.testing.expectEqualStrings(\"Mother Goose\", before_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);",
//     "try module.exit();",
//     "try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);",
//     "test \"phase9 trace-events sample keeps re-init rollback explicit after initialized, selftest-complete, and exited replay\" {",
//     "try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init());",
//     "try expectSummaryStable(before_initialized_reinit, initialized_module.summary());",
//     "try std.testing.expectEqual(ModuleStage.selftest_complete, before_selftested_reinit.stage);",
//     "try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init());",
//     "try expectSummaryStable(before_selftested_reinit, selftested_module.summary());",
//     "try std.testing.expectEqual(ModuleStage.exited, before_exited_reinit.stage);",
//     "try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init());",
//     "try expectSummaryStable(before_exited_reinit, exited_module.summary());",
//     "test \"phase9 trace-events sample keeps re-exit rollback explicit after initialized and selftest-complete replay\" {",
//     "try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.exit());",
//     "try expectSummaryStable(before_initialized_reexit, initialized_module.summary());",
//     "try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.exit());",
//     "try expectSummaryStable(before_selftested_reexit, selftested_module.summary());",
// };
//
// const FILE_EXACT_ONCE_MARKERS = [_][]const u8{
//     "test \"phase9 trace-events sample keeps initialized direct-activity exit rollback explicit before selftest replay\" {",
//     "test \"phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest\" {",
//     "test \"phase9 trace-events sample keeps re-init rollback explicit across initialized, selftest-complete, and exited states\" {",
//     "test \"phase9 trace-events sample keeps re-exit rollback explicit after initialized and selftest-complete replay\" {",
// };
//
// const EXIT_ROLLBACK_GUARD_SAMPLE_PATH = [_][]const u8{
//     "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
// };
//
// const REENTRY_GATE_SAMPLE_PATH = [_][]const u8{
//     "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
// };
//
// const REINIT_ROLLBACK_GUARD_SAMPLE_PATH = [_][]const u8{
//     "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
// };
//
// const REINIT_REEXIT_GUARD_SAMPLE_PATH = [_][]const u8{
//     "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (EXIT_ROLLBACK_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REENTRY_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REINIT_ROLLBACK_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REINIT_REEXIT_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (FILE_EXACT_ONCE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (EXIT_ROLLBACK_GUARD_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REENTRY_GATE_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REINIT_ROLLBACK_GUARD_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REINIT_REEXIT_GUARD_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
