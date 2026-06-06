const std = @import("std");
const build_options = @import("build_options");

const workflow = build_options.workflow_text;

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    ReorderedMarker,
    StaleMarker,
};

const Gate = struct {
    name: []const u8,
    command: []const u8,
};

const phase6_phase8_bridge = [_]Gate{
    .{
        .name = "Check current Phase 4 artifact-diff validator replay packet",
        .command = "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    },
    .{
        .name = "Validate current Phase 6 helper packet",
        .command = "make -C zigux phase6-validate",
    },
    .{
        .name = "Run current Phase 6 leaf helper tests",
        .command = "zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    },
    .{
        .name = "Run current Phase 6 shared perf route",
        .command = "make -C zigux phase6-perf",
    },
    .{
        .name = "Validate Phase 8 tooling routes",
        .command = "make -C zigux phase8-validate",
    },
    .{
        .name = "Run focused Phase 8 exec-cmd tests",
        .command = "make -C zigux phase8-exec-cmd-test",
    },
    .{
        .name = "Run focused Phase 8 libbpf segment tests",
        .command = "make -C zigux phase8-libbpf-segments-test",
    },
    .{
        .name = "Run Phase 8 tooling tests",
        .command = "make -C zigux phase8-test",
    },
};

const phase9_checker_ladder = [_]Gate{
    .{
        .name = "Self-test current Phase 9 review-checklist boundaries checker",
        .command = "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
    },
    .{
        .name = "Check current Phase 9 review-checklist boundaries packet",
        .command = "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    },
    .{
        .name = "Self-test current Phase 9 freeze-map study-boundaries checker",
        .command = "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test",
    },
    .{
        .name = "Check current Phase 9 freeze-map study-boundaries packet",
        .command = "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
    },
    .{
        .name = "Self-test current Phase 9 build-only surface checker",
        .command = "python3 scripts/zigux/check-phase9-build-only-surface.py --self-test",
    },
    .{
        .name = "Check current Phase 9 build-only surface packet",
        .command = "python3 scripts/zigux/check-phase9-build-only-surface.py",
    },
    .{
        .name = "Self-test current Phase 9 trace-events runtime packet checker",
        .command = "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 9 trace-events runtime packet",
        .command = "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py",
    },
};

const phase9_runtime_ladder = [_]Gate{
    .{
        .name = "Run current Phase 9 shared loader command-environment boundary guard tests",
        .command = "zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig",
    },
    .{
        .name = "Run current Phase 9 shared loader allocator-init-flow packet",
        .command = "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
    },
    .{
        .name = "Run current Phase 9 trace-events runtime sample tests",
        .command = "zig test samples/zigux/runtime_trace_events.zig",
    },
    .{
        .name = "Run current Phase 9 unregistered gate companion tests",
        .command = "zig test samples/zigux/runtime_trace_events_unregistered_gate.zig",
    },
    .{
        .name = "Run current Phase 9 exit rollback guard companion tests",
        .command = "zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    },
    .{
        .name = "Run current Phase 9 registration reentry companion tests",
        .command = "zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    },
    .{
        .name = "Run current Phase 9 reinit rollback guard companion tests",
        .command = "zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
    },
    .{
        .name = "Run current Phase 9 reinit reexit guard companion tests",
        .command = "zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    },
    .{
        .name = "Run current Phase 9 trace-events survey witness",
        .command = "zig test zigux/tests/runtime_trace_events_survey.zig",
    },
    .{
        .name = "Self-test current Phase 7 shared-control gap checker",
        .command = "python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
    },
};

fn countExactLines(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, line, needle)) count += 1;
    }
    return count;
}

fn indexOfExactLine(haystack: []const u8, needle: []const u8) ?usize {
    var start: usize = 0;
    while (start <= haystack.len) {
        const end = std.mem.indexOfScalarPos(u8, haystack, start, '\n') orelse haystack.len;
        if (std.mem.eql(u8, haystack[start..end], needle)) return start;
        if (end == haystack.len) break;
        start = end + 1;
    }
    return null;
}

fn requireOnce(haystack: []const u8, needle: []const u8) WorkflowError!usize {
    const first = indexOfExactLine(haystack, needle) orelse return error.MissingMarker;
    if (countExactLines(haystack, needle) != 1) return error.DuplicateMarker;
    return first;
}

fn requireAfter(previous: *?usize, haystack: []const u8, needle: []const u8) WorkflowError!void {
    const index = try requireOnce(haystack, needle);
    if (previous.*) |previous_index| {
        if (index <= previous_index) return error.ReorderedMarker;
    }
    previous.* = index;
}

fn requireGateAfter(previous: *?usize, text: []const u8, gate: Gate) WorkflowError!void {
    var name_buf: [192]u8 = undefined;
    var command_buf: [192]u8 = undefined;
    const name_line = std.fmt.bufPrint(&name_buf, "      - name: {s}", .{gate.name}) catch unreachable;
    const command_line = std.fmt.bufPrint(&command_buf, "        run: {s}", .{gate.command}) catch unreachable;
    try requireAfter(previous, text, name_line);
    try requireAfter(previous, text, command_line);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) WorkflowError!void {
    if (std.mem.indexOf(u8, haystack, needle) != null) return error.StaleMarker;
}

fn validatePhase6Phase8Phase9Workflow(text: []const u8) WorkflowError!void {
    var previous: ?usize = null;

    for (phase6_phase8_bridge) |gate| {
        try requireGateAfter(&previous, text, gate);
    }
    for (phase9_checker_ladder) |gate| {
        try requireGateAfter(&previous, text, gate);
    }
    for (phase9_runtime_ladder) |gate| {
        try requireGateAfter(&previous, text, gate);
    }

    try requireAbsent(text, "        run: make -C zigux phase6\n");
    try requireAbsent(text, "        run: make -C zigux phase8\n");
    try requireAbsent(text, "        run: make -C zigux phase9\n");
    try requireAbsent(text, "        run: make -C zigux phase9-validate\n");
}

test "current bootstrap workflow keeps the Phase 6, Phase 8, and Phase 9 bridge ordered" {
    try validatePhase6Phase8Phase9Workflow(workflow);
}

test "contract rejects a missing Phase 8 aggregate marker before Phase 9 starts" {
    const fixture =
        \\      - name: Check current Phase 4 artifact-diff validator replay packet
        \\        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py
        \\      - name: Validate current Phase 6 helper packet
        \\        run: make -C zigux phase6-validate
        \\      - name: Run current Phase 6 leaf helper tests
        \\        run: zig build test --build-file zigux/tests/phase6_build.zig --summary all
        \\      - name: Run current Phase 6 shared perf route
        \\        run: make -C zigux phase6-perf
        \\      - name: Validate Phase 8 tooling routes
        \\        run: make -C zigux phase8-validate
        \\      - name: Run focused Phase 8 exec-cmd tests
        \\        run: make -C zigux phase8-exec-cmd-test
        \\      - name: Run focused Phase 8 libbpf segment tests
        \\        run: make -C zigux phase8-libbpf-segments-test
        \\      - name: Self-test current Phase 9 review-checklist boundaries checker
        \\        run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test
    ;

    try std.testing.expectError(error.MissingMarker, validatePhase6Phase8Phase9Workflow(fixture));
}

test "contract rejects a runtime-only Phase 9 ladder as incomplete" {
    const fixture =
        \\      - name: Check current Phase 4 artifact-diff validator replay packet
        \\        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py
        \\      - name: Validate current Phase 6 helper packet
        \\        run: make -C zigux phase6-validate
        \\      - name: Run current Phase 6 leaf helper tests
        \\        run: zig build test --build-file zigux/tests/phase6_build.zig --summary all
        \\      - name: Run current Phase 6 shared perf route
        \\        run: make -C zigux phase6-perf
        \\      - name: Validate Phase 8 tooling routes
        \\        run: make -C zigux phase8-validate
        \\      - name: Run focused Phase 8 exec-cmd tests
        \\        run: make -C zigux phase8-exec-cmd-test
        \\      - name: Run focused Phase 8 libbpf segment tests
        \\        run: make -C zigux phase8-libbpf-segments-test
        \\      - name: Run Phase 8 tooling tests
        \\        run: make -C zigux phase8-test
        \\      - name: Run current Phase 9 shared loader command-environment boundary guard tests
        \\        run: zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig
        \\      - name: Self-test current Phase 9 review-checklist boundaries checker
        \\        run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test
    ;

    try std.testing.expectError(error.MissingMarker, validatePhase6Phase8Phase9Workflow(fixture));
}

test "contract rejects duplicate middle-bridge commands" {
    const duplicate = workflow ++ "\n        run: make -C zigux phase8-test\n";

    try std.testing.expectError(error.DuplicateMarker, validatePhase6Phase8Phase9Workflow(duplicate));
}

test "contract rejects stale broad Phase 6, Phase 8, or Phase 9 aggregate routes" {
    const stale = workflow ++ "\n        run: make -C zigux phase9\n";

    try std.testing.expectError(error.StaleMarker, validatePhase6Phase8Phase9Workflow(stale));
}
