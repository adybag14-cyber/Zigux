const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_TRACE_EVENTS_REINIT_REEXIT_GUARD_ROUTE_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
    "The reinit/reexit companion still keeps rejected re-init and rejected re-exit rollback explicit after both initialized direct activity and selftest-ready replay, so the same narrow packet now spells out that lifecycle retries fail closed without mutating the captured summaries.",
    ".name = \"phase9-runtime-trace-events-reinit-reexit-guard-tests\"",
    "../../samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    "phase9_runtime_trace_events.dependOn(n        &run_runtime_trace_events_reinit_reexit_guard_tests.step,n    );",
    "zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    "test \"phase9 trace-events sample keeps re-init rollback explicit after initialized, selftest-complete, and exited replay\" {",
    "test \"phase9 trace-events sample keeps re-exit rollback explicit after initialized and selftest-complete replay\" {",
    "try expectSummaryStable(before_initialized_reinit, initialized_module.summary());",
    "try expectSummaryStable(before_selftested_reinit, selftested_module.summary());",
    "try expectSummaryStable(before_exited_reinit, exited_module.summary());",
    "try expectSummaryStable(before_initialized_reexit, initialized_module.summary());",
    "try expectSummaryStable(before_selftested_reexit, selftested_module.summary());",
};

const EXACT_ONCE_MARKERS = [_][]const u8{
    "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
    ".name = \"phase9-runtime-trace-events-reinit-reexit-guard-tests\"",
    "zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    "test \"phase9 trace-events sample keeps re-init rollback explicit after initialized, selftest-complete, and exited replay\" {",
    "test \"phase9 trace-events sample keeps re-exit rollback explicit after initialized and selftest-complete replay\" {",
};

const SURVEY_NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
};

const PHASE9_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase9_build.zig",
};

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const SAMPLE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXACT_ONCE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
    for (PHASE9_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
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
