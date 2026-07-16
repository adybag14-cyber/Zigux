const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE9_TRACE_EVENTS_DIRECT_SUMMARY=pass";
pub const self_test_pass_marker = "PHASE9_TRACE_EVENTS_DIRECT_SUMMARY_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "last_main_emitted_events: ?usize,",
    "last_fn_emitted_events: ?usize,",
    "last_main_conditional_event_count: ?usize,",
    "test \"count-gated main-thread replay matches the Linux sample conditions\" {",
    "try std.testing.expectEqual(@as(?usize, 4), replay.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, null), replay.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), replay.last_main_conditional_event_count);",
    "try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_conditional_message);",
    "try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_template_cond_message);",
    "test \"selftest path still records both conditional families at count zero\" {",
    "try std.testing.expectEqual(@as(?usize, 6), replay.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), replay.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), replay.last_main_conditional_event_count);",
    "try std.testing.expectEqualStrings(\"Some times print\", replay.last_main_conditional_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"prints other times\", replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);",
    "test \"trace-events sample keeps conditional replay explicit after selftest\" {",
    "try std.testing.expectEqualStrings(\"Some times print\", before_conditional_replay.last_main_conditional_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"prints other times\", before_conditional_replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"event-sample\", after_conditional_replay.main_thread_label orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(\"event-sample-fn\", after_conditional_replay.function_thread_label orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(\"foo_bar_reg\", after_conditional_replay.last_register_label orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(\"foo_bar_unreg\", after_conditional_replay.last_unregister_label orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(\"hello\", after_conditional_replay.last_main_foo_bar_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"Mother Goose\", after_conditional_replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqual(@as(usize, 0), after_conditional_replay.last_main_vararg_array_length orelse return error.ExpectedMainPayload);",
    "try std.testing.expect(after_conditional_replay.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"HELLO\", after_conditional_replay.last_main_template_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"Some times print\", after_conditional_replay.last_main_conditional_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"prints other times\", after_conditional_replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"I have to be different\", after_conditional_replay.last_main_template_print_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"Hello __rel_loc\", after_conditional_replay.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"iter=%d\", after_conditional_replay.last_format_template orelse return error.ExpectedMainPayload);",
    "test \"trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity\" {",
    "try std.testing.expectEqual(ModuleStage.initialized, initialized_summary.stage);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_summary.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_summary.register_transitions);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_summary.unregister_transitions);",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_complete_summary.stage);",
    "try std.testing.expectEqual(@as(usize, 3), selftest_complete_summary.register_transitions);",
    "try std.testing.expectEqual(@as(usize, 3), selftest_complete_summary.unregister_transitions);",
    "try std.testing.expectEqual(@as(?usize, 4), selftest_complete_summary.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), selftest_complete_summary.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), selftest_complete_summary.last_main_conditional_event_count);",
    "try std.testing.expectEqualStrings(\"Frodo\", selftest_complete_summary.last_main_random_choice_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(\"Look at me\", selftest_complete_summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(\"Look at me too\", selftest_complete_summary.last_function_template_message orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqual(ModuleStage.exited, exited_summary.stage);",
    "try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);",
    "try std.testing.expectEqualStrings(selftest_complete_summary.last_register_label orelse return error.ExpectedFunctionPayload, exited_summary.last_register_label orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(selftest_complete_summary.last_unregister_label orelse return error.ExpectedFunctionPayload, exited_summary.last_unregister_label orelse return error.ExpectedFunctionPayload);",
    "test \"trace-events sample preserves initialized summary across direct exit without selftest\" {",
    "try std.testing.expectEqual(@as(?usize, null), before_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, null), before_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, null), before_exit.last_main_conditional_event_count);",
    "test \"trace-events sample keeps failed-exit rollback explicit after selftest-ready replay\" {",
    "try std.testing.expectEqual(@as(?usize, 4), before_failed_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), before_failed_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), before_failed_exit.last_main_conditional_event_count);",
    "test \"trace-events sample keeps rejected re-selftest rollback explicit\" {",
    "try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.selftest_runs);",
    "try std.testing.expectEqualStrings(\"foo_bar_reg\", before_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(\"foo_bar_unreg\", before_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(before_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload, after_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(before_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload, after_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.exit_runs);",
    "try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.register_transitions);",
    "try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.unregister_transitions);",
    "try std.testing.expectEqualStrings(before_rejected_exit_selftest.last_register_label orelse return error.ExpectedFunctionPayload, after_rejected_exit_selftest.last_register_label orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(before_rejected_exit_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload, after_rejected_exit_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqual(before_rejected_exit_selftest.last_main_conditional_event_count, after_rejected_exit_selftest.last_main_conditional_event_count);",
};

const contracts = [_]FileContract{
    .{ .rel = "samples/zigux/runtime_trace_events.zig", .markers = &markers_0 },
};

const exact_contracts = [_]FileContract{
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
    try guard.printLine(io, "PHASE9_TRACE_EVENTS_DIRECT_SUMMARY_MARKER_COUNT=70", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try std.testing.expectEqual(@as(usize, 70), comptime blk: {
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
// pub const pass_marker = "PHASE9_TRACE_EVENTS_DIRECT_SUMMARY_SELF_TEST=pass";
//
// const DIRECT_SAMPLE_REQUIRED_MARKERS = [_][]const u8{
//     "last_main_emitted_events: ?usize,",
//     "last_fn_emitted_events: ?usize,",
//     "last_main_conditional_event_count: ?usize,",
//     "test \"count-gated main-thread replay matches the Linux sample conditions\" {",
//     "try std.testing.expectEqual(@as(?usize, 4), replay.last_main_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, null), replay.last_fn_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, 0), replay.last_main_conditional_event_count);",
//     "try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_conditional_message);",
//     "try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_template_cond_message);",
//     "test \"selftest path still records both conditional families at count zero\" {",
//     "try std.testing.expectEqual(@as(?usize, 6), replay.last_main_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, 2), replay.last_fn_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, 2), replay.last_main_conditional_event_count);",
//     "try std.testing.expectEqualStrings(\"Some times print\", replay.last_main_conditional_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"prints other times\", replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);",
//     "test \"trace-events sample keeps conditional replay explicit after selftest\" {",
//     "try std.testing.expectEqualStrings(\"Some times print\", before_conditional_replay.last_main_conditional_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"prints other times\", before_conditional_replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"event-sample\", after_conditional_replay.main_thread_label orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqualStrings(\"event-sample-fn\", after_conditional_replay.function_thread_label orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqualStrings(\"foo_bar_reg\", after_conditional_replay.last_register_label orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqualStrings(\"foo_bar_unreg\", after_conditional_replay.last_unregister_label orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqualStrings(\"hello\", after_conditional_replay.last_main_foo_bar_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"Mother Goose\", after_conditional_replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqual(@as(usize, 0), after_conditional_replay.last_main_vararg_array_length orelse return error.ExpectedMainPayload);",
//     "try std.testing.expect(after_conditional_replay.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"HELLO\", after_conditional_replay.last_main_template_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"Some times print\", after_conditional_replay.last_main_conditional_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"prints other times\", after_conditional_replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"I have to be different\", after_conditional_replay.last_main_template_print_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"Hello __rel_loc\", after_conditional_replay.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"iter=%d\", after_conditional_replay.last_format_template orelse return error.ExpectedMainPayload);",
//     "test \"trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity\" {",
//     "try std.testing.expectEqual(ModuleStage.initialized, initialized_summary.stage);",
//     "try std.testing.expectEqual(@as(usize, 0), initialized_summary.registration_depth);",
//     "try std.testing.expectEqual(@as(usize, 0), initialized_summary.register_transitions);",
//     "try std.testing.expectEqual(@as(usize, 0), initialized_summary.unregister_transitions);",
//     "try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_complete_summary.stage);",
//     "try std.testing.expectEqual(@as(usize, 3), selftest_complete_summary.register_transitions);",
//     "try std.testing.expectEqual(@as(usize, 3), selftest_complete_summary.unregister_transitions);",
//     "try std.testing.expectEqual(@as(?usize, 4), selftest_complete_summary.last_main_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, 2), selftest_complete_summary.last_fn_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, 0), selftest_complete_summary.last_main_conditional_event_count);",
//     "try std.testing.expectEqualStrings(\"Frodo\", selftest_complete_summary.last_main_random_choice_message orelse return error.ExpectedMainPayload);",
//     "try std.testing.expectEqualStrings(\"Look at me\", selftest_complete_summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqualStrings(\"Look at me too\", selftest_complete_summary.last_function_template_message orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqual(ModuleStage.exited, exited_summary.stage);",
//     "try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);",
//     "try std.testing.expectEqualStrings(selftest_complete_summary.last_register_label orelse return error.ExpectedFunctionPayload, exited_summary.last_register_label orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqualStrings(selftest_complete_summary.last_unregister_label orelse return error.ExpectedFunctionPayload, exited_summary.last_unregister_label orelse return error.ExpectedFunctionPayload);",
//     "test \"trace-events sample preserves initialized summary across direct exit without selftest\" {",
//     "try std.testing.expectEqual(@as(?usize, null), before_exit.last_main_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, null), before_exit.last_fn_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, null), before_exit.last_main_conditional_event_count);",
//     "test \"trace-events sample keeps failed-exit rollback explicit after selftest-ready replay\" {",
//     "try std.testing.expectEqual(@as(?usize, 4), before_failed_exit.last_main_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, 2), before_failed_exit.last_fn_emitted_events);",
//     "try std.testing.expectEqual(@as(?usize, 0), before_failed_exit.last_main_conditional_event_count);",
//     "test \"trace-events sample keeps rejected re-selftest rollback explicit\" {",
//     "try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.selftest_runs);",
//     "try std.testing.expectEqualStrings(\"foo_bar_reg\", before_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqualStrings(\"foo_bar_unreg\", before_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqualStrings(before_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload, after_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqualStrings(before_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload, after_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.exit_runs);",
//     "try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.register_transitions);",
//     "try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.unregister_transitions);",
//     "try std.testing.expectEqualStrings(before_rejected_exit_selftest.last_register_label orelse return error.ExpectedFunctionPayload, after_rejected_exit_selftest.last_register_label orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqualStrings(before_rejected_exit_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload, after_rejected_exit_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);",
//     "try std.testing.expectEqual(before_rejected_exit_selftest.last_main_conditional_event_count, after_rejected_exit_selftest.last_main_conditional_event_count);",
// };
//
// const DIRECT_SAMPLE_PATH = [_][]const u8{
//     "samples/zigux/runtime_trace_events.zig",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (DIRECT_SAMPLE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (DIRECT_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
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
