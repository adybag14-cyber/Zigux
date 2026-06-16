const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_RUNTIME_TRACE_EVENTS_MODULE_SLICE_SELF_TEST=pass";

const MODULE_SLICE_SAMPLE_LOCAL_ONLY_MARKER = [_][]const u8{
    "do not by themselves prove live `module_init()`, `module_exit()`, depmod-visible module registration, or the removed shared runtime-loader substrate on current `master`",
};

const MODULE_SLICE_INIT_MARKER = [_][]const u8{
    "`init()` only accepts the `.cold` stage, resets registration depth, counters, labels, and cached payloads, increments `init_runs`, and moves `stage_state` to `.initialized`.",
};

const MODULE_SLICE_REGISTER_MARKER = [_][]const u8{
    "`registerFunctionThread()` only runs through `ensureMutable()` while the sample is still `.initialized` or `.selftest_complete`; if `registration_depth != 0` it returns `error.FunctionThreadAlreadyRegistered`, otherwise it sets `registration_depth = 1` and `last_register_label = \"foo_bar_reg\"`.",
};

const MODULE_SLICE_SELFTEST_MARKER = [_][]const u8{
    "`runSelftest()` is only accepted from `.initialized`; it replays `emitMainIteration(0)`, `registerFunctionThread()`, `emitFunctionIteration(1)`, and `unregisterFunctionThread()` before incrementing `selftest_runs` and moving the sample to `.selftest_complete`.",
};

const MODULE_SLICE_EXIT_MARKER = [_][]const u8{
    "`unregisterFunctionThread()` fails closed with `error.RegistrationUnderflow` when the depth is already zero, and `exit()` rejects nonzero registration depth with `error.OutstandingRegistration` before allowing the `.exited` stage.",
};

const MODULE_SLICE_DUPLICATE_REGISTRATION_MARKER = [_][]const u8{
    "The shipped duplicate-registration test in `samples/zigux/runtime_trace_events.zig` confirms that a second `registerFunctionThread()` call preserves the prior summary and fails with `error.FunctionThreadAlreadyRegistered`.",
};

const MODULE_SLICE_BACKLOG_MARKER = [_][]const u8{
    "No current family-local trace-events packet should therefore describe `samples/zigux/runtime_trace_events_loader.zig`, `zigux/tests/runtime_trace_events_module.zig`, `zigux/tests/runtime_trace_events_diff.zig`, `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`, `zigux/tests/runtime_trace_events_survey.zig`, or `zigux/tests/runtime_trace_events_manifest.json` as shipped current-`master` evidence unless a fresh repo reread proves they have returned.",
};

const SAMPLE_DUPLICATE_REGISTRATION_TEST_MARKER = [_][]const u8{
    "test \"trace-events sample rejects duplicate function-thread registration\" {",
};

const UNREGISTERED_GATE_TEST_MARKER = [_][]const u8{
    "test \"phase9 trace-events sample keeps unregistered function-thread failures fail-closed\" {",
};

const MODULE_SLICE_REQUIRED_MARKERS = [_][]const u8{
    "MODULE_SLICE_HEADER_MARKER",
    "MODULE_SLICE_PACKET_MARKER",
    "MODULE_SLICE_GATE_MARKER",
    "MODULE_SLICE_LANE_NOTE_MARKER",
    "MODULE_SLICE_CHECKER_MARKER",
    "MODULE_SLICE_SELFTEST_HOOK_MARKER",
    "MODULE_SLICE_LIFECYCLE_MARKER",
    "MODULE_SLICE_SAMPLE_LOCAL_ONLY_MARKER",
    "MODULE_SLICE_INIT_MARKER",
    "MODULE_SLICE_REGISTER_MARKER",
    "MODULE_SLICE_EMIT_FN_MARKER",
    "MODULE_SLICE_SELFTEST_MARKER",
    "MODULE_SLICE_EXIT_MARKER",
    "MODULE_SLICE_DUPLICATE_REGISTRATION_MARKER",
    "MODULE_SLICE_ABSENT_LOADER_MARKER",
    "MODULE_SLICE_BACKLOG_MARKER",
};

const SAMPLE_REQUIRED_MARKERS = [_][]const u8{
    "SAMPLE_DESCRIPTOR_MARKER",
    "SAMPLE_RUN_SELFTEST_MARKER",
    "SAMPLE_REGISTER_MARKER",
    "SAMPLE_UNREGISTER_MARKER",
    "SAMPLE_EXIT_MARKER",
    "SAMPLE_DUPLICATE_REGISTRATION_TEST_MARKER",
    "SAMPLE_DUPLICATE_REGISTRATION_ERROR_MARKER",
    "SAMPLE_OUTSTANDING_REGISTRATION_MARKER",
};

const UNREGISTERED_GATE_REQUIRED_MARKERS = [_][]const u8{
    "UNREGISTERED_GATE_TEST_MARKER",
    "UNREGISTERED_GATE_FN_REJECTION_MARKER",
    "UNREGISTERED_GATE_UNREGISTER_REJECTION_MARKER",
    "UNREGISTERED_GATE_SELFTEST_STAGE_MARKER",
};

const MODULE_SLICE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
};

const SAMPLE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events.zig",
};

const UNREGISTERED_GATE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
};

const MODULE_SLICE_HEADER_MARKER = [_][]const u8{
    "# Phase 9 Runtime Trace-Events Module Slice",
};

const MODULE_SLICE_PACKET_MARKER = [_][]const u8{
    "Current `master` keeps only a narrow direct trace-events runtime packet in this family-local slice:",
};

const MODULE_SLICE_SAMPLE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events.zig`",
};

const MODULE_SLICE_GATE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
};

const MODULE_SLICE_LANE_NOTE_MARKER = [_][]const u8{
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
};

const MODULE_SLICE_CHECKER_MARKER = [_][]const u8{
    "`scripts/zigux/check_phase9_trace_events_runtime_packet.zig`",
};

const MODULE_SLICE_SELFTEST_HOOK_MARKER = [_][]const u8{
    "`.provides_selftest_hook = true`",
};

const MODULE_SLICE_LIFECYCLE_MARKER = [_][]const u8{
    "initialized, selftest_complete, and exited sample-local lifecycle tracking",
};

const MODULE_SLICE_EMIT_FN_MARKER = [_][]const u8{
    "`emitFunctionIteration()` rejects use without prior registration with `error.FunctionThreadNotRegistered`.",
};

const MODULE_SLICE_ABSENT_LOADER_MARKER = [_][]const u8{
    "does not currently expose the broader shared runtime-loader packet",
};

const SAMPLE_DESCRIPTOR_MARKER = [_][]const u8{
    ".provides_selftest_hook = true",
};

const SAMPLE_RUN_SELFTEST_MARKER = [_][]const u8{
    "pub fn runSelftest(self: *Self) !EmissionSummary {",
};

const SAMPLE_REGISTER_MARKER = [_][]const u8{
    "pub fn registerFunctionThread(self: *Self) !void {",
};

const SAMPLE_UNREGISTER_MARKER = [_][]const u8{
    "pub fn unregisterFunctionThread(self: *Self) !void {",
};

const SAMPLE_EXIT_MARKER = [_][]const u8{
    "pub fn exit(self: *Self) !void {",
};

const SAMPLE_DUPLICATE_REGISTRATION_ERROR_MARKER = [_][]const u8{
    "error.FunctionThreadAlreadyRegistered",
};

const SAMPLE_OUTSTANDING_REGISTRATION_MARKER = [_][]const u8{
    "error.OutstandingRegistration",
};

const UNREGISTERED_GATE_FN_REJECTION_MARKER = [_][]const u8{
    "error.FunctionThreadNotRegistered",
};

const UNREGISTERED_GATE_UNREGISTER_REJECTION_MARKER = [_][]const u8{
    "error.RegistrationUnderflow",
};

const UNREGISTERED_GATE_SELFTEST_STAGE_MARKER = [_][]const u8{
    "ModuleStage.selftest_complete",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (MODULE_SLICE_SAMPLE_LOCAL_ONLY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_INIT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_REGISTER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_SELFTEST_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_EXIT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_DUPLICATE_REGISTRATION_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_BACKLOG_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_DUPLICATE_REGISTRATION_TEST_MARKER) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_GATE_TEST_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_GATE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_GATE_PATH) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_HEADER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_PACKET_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_SAMPLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_GATE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_LANE_NOTE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_CHECKER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_SELFTEST_HOOK_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_LIFECYCLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_EMIT_FN_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_ABSENT_LOADER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_DESCRIPTOR_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_RUN_SELFTEST_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_REGISTER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_UNREGISTER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_EXIT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_DUPLICATE_REGISTRATION_ERROR_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_OUTSTANDING_REGISTRATION_MARKER) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_GATE_FN_REJECTION_MARKER) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_GATE_UNREGISTER_REJECTION_MARKER) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_GATE_SELFTEST_STAGE_MARKER) |marker| try guard.requireMarker(text, marker);
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
