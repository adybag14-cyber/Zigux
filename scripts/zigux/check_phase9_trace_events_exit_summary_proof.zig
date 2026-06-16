const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_TRACE_EVENTS_EXIT_SUMMARY_PROOF_SELF_TEST=pass";

const MODULE_SLICE_EXIT_SUMMARY_MARKER = [_][]const u8{
    "The exit-rollback companion keeps failed-exit rollback explicit after reusable selftest replay by proving `error.OutstandingRegistration` leaves the selftest_complete summary unchanged until the function thread unregisters and clean exit succeeds.",
};

const SURVEY_NOTE_EXIT_SUMMARY_MARKER = [_][]const u8{
    "`error.OutstandingRegistration` guard plus the later post-exit invalid-lifecycle rejections that leave the summary unchanged.",
};

const SAMPLES_README_EXIT_SUMMARY_MARKER = [_][]const u8{
    "`error.OutstandingRegistration` leaves the selftest_complete summary unchanged until the function thread unregisters",
};

const EXIT_ROLLBACK_GUARD_MARKERS = [_][]const u8{
    "test \"phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay\" {",
    "try std.testing.expectError(error.OutstandingRegistration, module.exit());",
    "try expectSummaryStable(before_failed_exit, after_failed_exit);",
    "try std.testing.expectEqual(@as(usize, 20), before_unregister.total_events);",
    "try std.testing.expectEqual(@as(usize, 2), before_exit.unregister_transitions);",
    "try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);",
    "try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);",
    "try expectSummaryStable(exited_before_rejected_ops, exited_after_rejected_ops);",
};

const MODULE_SLICE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
};

const SURVEY_NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
};

const SAMPLES_README_PATH = [_][]const u8{
    "samples/zigux/README.md",
};

const EXIT_ROLLBACK_GUARD_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (MODULE_SLICE_EXIT_SUMMARY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_EXIT_SUMMARY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_EXIT_SUMMARY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (EXIT_ROLLBACK_GUARD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (EXIT_ROLLBACK_GUARD_PATH) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
