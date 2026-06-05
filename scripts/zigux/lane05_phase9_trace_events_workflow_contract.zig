const std = @import("std");
const Io = std.Io;

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingMarker,
    OutOfOrderMarker,
};

const Marker = struct {
    label: []const u8,
    text: []const u8,
};

const phase9_markers = [_]Marker{
    .{
        .label = "phase9 review checklist self-test",
        .text = "Self-test current Phase 9 review-checklist boundaries checker",
    },
    .{
        .label = "phase9 review checklist packet",
        .text = "Check current Phase 9 review-checklist boundaries packet",
    },
    .{
        .label = "phase9 freeze-map self-test",
        .text = "Self-test current Phase 9 freeze-map study-boundaries checker",
    },
    .{
        .label = "phase9 build-only packet",
        .text = "Check current Phase 9 build-only surface packet",
    },
    .{
        .label = "phase9 trace-events runtime self-test",
        .text = "Self-test current Phase 9 trace-events runtime packet checker",
    },
    .{
        .label = "phase9 trace-events runtime packet",
        .text = "Check current Phase 9 trace-events runtime packet",
    },
    .{
        .label = "phase9 trace-events direct summary packet",
        .text = "Check current Phase 9 trace-events direct-summary packet",
    },
    .{
        .label = "phase9 trace-events summary preservation packet",
        .text = "Check current Phase 9 trace-events summary-preservation packet",
    },
    .{
        .label = "phase9 loader command environment guard",
        .text = "Run current Phase 9 shared loader command-environment boundary guard tests",
    },
    .{
        .label = "phase9 loader allocator flow",
        .text = "Run current Phase 9 shared loader allocator-init-flow packet",
    },
    .{
        .label = "phase9 trace-events runtime sample",
        .text = "Run current Phase 9 trace-events runtime sample tests",
    },
    .{
        .label = "phase9 unregistered gate companion",
        .text = "Run current Phase 9 unregistered gate companion tests",
    },
    .{
        .label = "phase9 exit rollback guard companion",
        .text = "Run current Phase 9 exit rollback guard companion tests",
    },
    .{
        .label = "phase9 registration reentry companion",
        .text = "Run current Phase 9 registration reentry companion tests",
    },
    .{
        .label = "phase9 reinit rollback guard companion",
        .text = "Run current Phase 9 reinit rollback guard companion tests",
    },
    .{
        .label = "phase9 reinit reexit guard companion",
        .text = "Run current Phase 9 reinit reexit guard companion tests",
    },
    .{
        .label = "phase9 trace-events survey witness",
        .text = "Run current Phase 9 trace-events survey witness",
    },
    .{
        .label = "phase7 handoff self-test",
        .text = "Self-test current Phase 7 shared-control gap checker",
    },
};

fn markerIndex(workflow: []const u8, marker: Marker) ContractError!usize {
    return std.mem.indexOf(u8, workflow, marker.text) orelse {
        return ContractError.MissingMarker;
    };
}

fn requireOrderedMarkers(workflow: []const u8, markers: []const Marker) ContractError!void {
    var previous_index: ?usize = null;

    for (markers) |marker| {
        const index = try markerIndex(workflow, marker);
        if (previous_index) |prev| {
            if (index <= prev) {
                return ContractError.OutOfOrderMarker;
            }
        }
        previous_index = index;
    }
}

fn requireAdjacentCommand(workflow: []const u8, name_marker: []const u8, command_marker: []const u8) ContractError!void {
    const name_index = std.mem.indexOf(u8, workflow, name_marker) orelse return ContractError.MissingMarker;
    const command_index = std.mem.indexOfPos(u8, workflow, name_index, command_marker) orelse return ContractError.MissingMarker;
    const next_name = std.mem.indexOfPos(u8, workflow, name_index + name_marker.len, "\n      - name:");
    if (next_name) |next_name_index| {
        if (command_index > next_name_index) return ContractError.OutOfOrderMarker;
    }
}

pub fn validateWorkflow(workflow: []const u8) ContractError!void {
    try requireOrderedMarkers(workflow, phase9_markers[0..]);
    try requireAdjacentCommand(
        workflow,
        "Run current Phase 9 trace-events runtime sample tests",
        "zig test samples/zigux/runtime_trace_events.zig",
    );
    try requireAdjacentCommand(
        workflow,
        "Run current Phase 9 trace-events survey witness",
        "zig test zigux/tests/runtime_trace_events_survey.zig",
    );
}

pub fn main() !void {
    const allocator = std.heap.page_allocator;
    var io_instance: Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    const workflow = try Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
    defer allocator.free(workflow);

    try validateWorkflow(workflow);

    std.debug.print("LANE05_PHASE9_TRACE_EVENTS_WORKFLOW_CONTRACT=pass\n", .{});
    std.debug.print("LANE05_PHASE9_TRACE_EVENTS_WORKFLOW_CONTRACT_MARKER_COUNT={d}\n", .{phase9_markers.len});
}

test "current Phase 9 trace-events workflow block stays ordered" {
    const workflow =
        \\      - name: Self-test current Phase 9 review-checklist boundaries checker
        \\        run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test
        \\      - name: Check current Phase 9 review-checklist boundaries packet
        \\        run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py
        \\      - name: Self-test current Phase 9 freeze-map study-boundaries checker
        \\        run: python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test
        \\      - name: Check current Phase 9 build-only surface packet
        \\        run: python3 scripts/zigux/check-phase9-build-only-surface.py
        \\      - name: Self-test current Phase 9 trace-events runtime packet checker
        \\        run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test
        \\      - name: Check current Phase 9 trace-events runtime packet
        \\        run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py
        \\      - name: Check current Phase 9 trace-events direct-summary packet
        \\        run: python3 scripts/zigux/check-phase9-trace-events-direct-summary.py
        \\      - name: Check current Phase 9 trace-events summary-preservation packet
        \\        run: python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py
        \\      - name: Run current Phase 9 shared loader command-environment boundary guard tests
        \\        run: zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig
        \\      - name: Run current Phase 9 shared loader allocator-init-flow packet
        \\        run: zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig
        \\      - name: Run current Phase 9 trace-events runtime sample tests
        \\        run: zig test samples/zigux/runtime_trace_events.zig
        \\      - name: Run current Phase 9 unregistered gate companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_unregistered_gate.zig
        \\      - name: Run current Phase 9 exit rollback guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig
        \\      - name: Run current Phase 9 registration reentry companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig
        \\      - name: Run current Phase 9 reinit rollback guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig
        \\      - name: Run current Phase 9 reinit reexit guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig
        \\      - name: Run current Phase 9 trace-events survey witness
        \\        run: zig test zigux/tests/runtime_trace_events_survey.zig
        \\      - name: Self-test current Phase 7 shared-control gap checker
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test
    ;

    try validateWorkflow(workflow);
}

test "trace-events runtime sample command must stay attached to its workflow step" {
    const workflow =
        \\      - name: Run current Phase 9 trace-events runtime sample tests
        \\      - name: Run current Phase 9 trace-events survey witness
        \\        run: zig test samples/zigux/runtime_trace_events.zig
        \\        run: zig test zigux/tests/runtime_trace_events_survey.zig
    ;

    try std.testing.expectError(
        ContractError.OutOfOrderMarker,
        requireAdjacentCommand(
            workflow,
            "Run current Phase 9 trace-events runtime sample tests",
            "zig test samples/zigux/runtime_trace_events.zig",
        ),
    );
}

test "Phase 7 handoff must remain after the Phase 9 survey witness" {
    const workflow =
        \\      - name: Self-test current Phase 9 review-checklist boundaries checker
        \\      - name: Check current Phase 9 review-checklist boundaries packet
        \\      - name: Self-test current Phase 7 shared-control gap checker
        \\      - name: Self-test current Phase 9 freeze-map study-boundaries checker
        \\      - name: Check current Phase 9 build-only surface packet
        \\      - name: Self-test current Phase 9 trace-events runtime packet checker
        \\      - name: Check current Phase 9 trace-events runtime packet
        \\      - name: Check current Phase 9 trace-events direct-summary packet
        \\      - name: Check current Phase 9 trace-events summary-preservation packet
        \\      - name: Run current Phase 9 shared loader command-environment boundary guard tests
        \\      - name: Run current Phase 9 shared loader allocator-init-flow packet
        \\      - name: Run current Phase 9 trace-events runtime sample tests
        \\        run: zig test samples/zigux/runtime_trace_events.zig
        \\      - name: Run current Phase 9 unregistered gate companion tests
        \\      - name: Run current Phase 9 exit rollback guard companion tests
        \\      - name: Run current Phase 9 registration reentry companion tests
        \\      - name: Run current Phase 9 reinit rollback guard companion tests
        \\      - name: Run current Phase 9 reinit reexit guard companion tests
        \\      - name: Run current Phase 9 trace-events survey witness
        \\        run: zig test zigux/tests/runtime_trace_events_survey.zig
    ;

    try std.testing.expectError(ContractError.OutOfOrderMarker, validateWorkflow(workflow));
}
