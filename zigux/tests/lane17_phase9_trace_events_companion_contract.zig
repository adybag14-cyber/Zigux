const std = @import("std");
const options = @import("lane17_phase9_trace_events_companion_options");

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    OutOfOrderMarker,
};

const companion_markers = [_][]const u8{
    "      - name: Self-test current Phase 9 trace-events runtime packet checker\n",
    "        run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test\n",
    "      - name: Check current Phase 9 trace-events runtime packet\n",
    "        run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py\n",
    "      - name: Self-test current Phase 9 trace-events direct-summary checker\n",
    "        run: python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test\n",
    "      - name: Check current Phase 9 trace-events direct-summary packet\n",
    "        run: python3 scripts/zigux/check-phase9-trace-events-direct-summary.py\n",
    "      - name: Self-test current Phase 9 trace-events summary-preservation checker\n",
    "        run: python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py --self-test\n",
    "      - name: Check current Phase 9 trace-events summary-preservation packet\n",
    "        run: python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py\n",
    "      - name: Run current Phase 9 shared loader command-environment boundary guard tests\n",
    "        run: zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig\n",
    "      - name: Run current Phase 9 shared loader allocator-init-flow packet\n",
    "        run: zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig\n",
    "      - name: Run current Phase 9 trace-events runtime sample tests\n",
    "        run: zig test samples/zigux/runtime_trace_events.zig\n",
    "      - name: Run current Phase 9 unregistered gate companion tests\n",
    "        run: zig test samples/zigux/runtime_trace_events_unregistered_gate.zig\n",
    "      - name: Run current Phase 9 exit rollback guard companion tests\n",
    "        run: zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig\n",
    "      - name: Run current Phase 9 registration reentry companion tests\n",
    "        run: zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig\n",
    "      - name: Run current Phase 9 reinit rollback guard companion tests\n",
    "        run: zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig\n",
    "      - name: Run current Phase 9 reinit reexit guard companion tests\n",
    "        run: zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig\n",
    "      - name: Run current Phase 9 trace-events survey witness\n",
    "        run: zig test zigux/tests/runtime_trace_events_survey.zig\n",
};

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        options.workflow_path,
        allocator,
        .limited(256 * 1024),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative| {
        count += 1;
        cursor += relative + needle.len;
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return WorkflowError.MissingMarker;
    if (countOccurrences(haystack, needle) != 1) return WorkflowError.DuplicateMarker;
    return first;
}

fn requireOrderedUnique(haystack: []const u8, markers: []const []const u8) !void {
    var previous: usize = 0;
    for (markers, 0..) |marker, index| {
        const current = try requireOnce(haystack, marker);
        if (index > 0 and current <= previous) return WorkflowError.OutOfOrderMarker;
        previous = current;
    }
}

fn validatePhase9TraceEventsCompanion(workflow: []const u8) !void {
    try requireOrderedUnique(workflow, &companion_markers);

    const build_only = try requireOnce(
        workflow,
        "      - name: Check current Phase 9 build-only surface\n",
    );
    const first_trace_events = try requireOnce(workflow, companion_markers[0]);
    if (first_trace_events <= build_only) return WorkflowError.OutOfOrderMarker;

    const survey = try requireOnce(
        workflow,
        "      - name: Run current Phase 9 trace-events survey witness\n",
    );
    const phase7_handoff = try requireOnce(
        workflow,
        "      - name: Self-test current Phase 7 shared-control gap checker\n",
    );
    if (phase7_handoff <= survey) return WorkflowError.OutOfOrderMarker;
}

test "live workflow keeps the Phase 9 trace-events companion ladder intact" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try validatePhase9TraceEventsCompanion(workflow);
}

test "contract fails closed when a companion sample command is missing" {
    const fixture =
        "      - name: Check current Phase 9 build-only surface\n" ++
        companion_markers[0] ++ companion_markers[1] ++
        companion_markers[2] ++ companion_markers[3] ++
        companion_markers[4] ++ companion_markers[5] ++
        companion_markers[6] ++ companion_markers[7] ++
        companion_markers[8] ++ companion_markers[9] ++
        companion_markers[10] ++ companion_markers[11] ++
        companion_markers[12] ++ companion_markers[13] ++
        companion_markers[14] ++ companion_markers[15] ++
        companion_markers[16] ++ companion_markers[17] ++
        companion_markers[18] ++ companion_markers[19] ++
        companion_markers[20] ++ companion_markers[21] ++
        companion_markers[22] ++ companion_markers[23] ++
        companion_markers[24] ++
        "      - name: Self-test current Phase 7 shared-control gap checker\n";

    try std.testing.expectError(WorkflowError.MissingMarker, validatePhase9TraceEventsCompanion(fixture));
}

test "contract fails closed when the companion survey is before a runtime sample" {
    const fixture =
        "      - name: Check current Phase 9 build-only surface\n" ++
        companion_markers[0] ++ companion_markers[1] ++
        companion_markers[2] ++ companion_markers[3] ++
        companion_markers[4] ++ companion_markers[5] ++
        companion_markers[6] ++ companion_markers[7] ++
        companion_markers[8] ++ companion_markers[9] ++
        companion_markers[10] ++ companion_markers[11] ++
        companion_markers[24] ++ companion_markers[25] ++
        companion_markers[12] ++ companion_markers[13] ++
        companion_markers[14] ++ companion_markers[15] ++
        companion_markers[16] ++ companion_markers[17] ++
        companion_markers[18] ++ companion_markers[19] ++
        companion_markers[20] ++ companion_markers[21] ++
        companion_markers[22] ++ companion_markers[23] ++
        "      - name: Self-test current Phase 7 shared-control gap checker\n";

    try std.testing.expectError(WorkflowError.OutOfOrderMarker, validatePhase9TraceEventsCompanion(fixture));
}

test "contract fails closed when a companion command is duplicated" {
    const fixture =
        "      - name: Check current Phase 9 build-only surface\n" ++
        companion_markers[0] ++ companion_markers[1] ++
        companion_markers[2] ++ companion_markers[3] ++
        companion_markers[4] ++ companion_markers[5] ++
        companion_markers[6] ++ companion_markers[7] ++
        companion_markers[8] ++ companion_markers[9] ++
        companion_markers[10] ++ companion_markers[11] ++
        companion_markers[12] ++ companion_markers[13] ++ companion_markers[13] ++
        companion_markers[14] ++ companion_markers[15] ++
        companion_markers[16] ++ companion_markers[17] ++
        companion_markers[18] ++ companion_markers[19] ++
        companion_markers[20] ++ companion_markers[21] ++
        companion_markers[22] ++ companion_markers[23] ++
        companion_markers[24] ++ companion_markers[25] ++
        "      - name: Self-test current Phase 7 shared-control gap checker\n";

    try std.testing.expectError(WorkflowError.DuplicateMarker, validatePhase9TraceEventsCompanion(fixture));
}
