const std = @import("std");
const options = @import("lane17_phase9_phase10_handoff_options");

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    ReorderedMarker,
    StaleMarker,
};

const workflow = options.workflow_text;

const Gate = struct {
    name: []const u8,
    command: []const u8,
};

const phase9_phase10_handoff = [_]Gate{
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
    .{
        .name = "Check current Phase 7 shared-control gap packet",
        .command = "python3 scripts/zigux/check-phase7-shared-control-gap.py",
    },
    .{
        .name = "Self-test current Phase 7 make-wrapper selftest alignment checker",
        .command = "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    },
    .{
        .name = "Check current Phase 7 make-wrapper selftest alignment packet",
        .command = "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    },
    .{
        .name = "Self-test current Phase 10 bootstrap route checker",
        .command = "python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test",
    },
    .{
        .name = "Check current Phase 10 bootstrap route",
        .command = "python3 scripts/zigux/check-phase10-bootstrap-route.py",
    },
    .{
        .name = "Validate Phase 10 checker-backed review packet",
        .command = "make -C zigux phase10-validate",
    },
    .{
        .name = "Run Phase 10 helper tests",
        .command = "make -C zigux phase10-test",
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

fn requireAbsent(haystack: []const u8, needle: []const u8) WorkflowError!void {
    if (std.mem.indexOf(u8, haystack, needle) != null) return error.StaleMarker;
}

fn validatePhase9Phase10Handoff(text: []const u8) WorkflowError!void {
    var previous: ?usize = null;

    for (phase9_phase10_handoff) |gate| {
        var name_buf: [192]u8 = undefined;
        var command_buf: [192]u8 = undefined;
        const name_line = std.fmt.bufPrint(&name_buf, "      - name: {s}", .{gate.name}) catch unreachable;
        const command_line = std.fmt.bufPrint(&command_buf, "        run: {s}", .{gate.command}) catch unreachable;
        try requireAfter(&previous, text, name_line);
        try requireAfter(&previous, text, command_line);
    }

    try requireAbsent(text, "        run: make -C zigux phase9\n");
    try requireAbsent(text, "        run: make -C zigux phase9-test\n");
    try requireAbsent(text, "        run: make -C zigux phase7\n");
    try requireAbsent(text, "        run: make -C zigux phase10\n");
}

test "current bootstrap workflow keeps the Phase 9 tail ordered into Phase 7 and Phase 10" {
    try validatePhase9Phase10Handoff(workflow);
}

test "contract rejects a missing Phase 7 handoff checker" {
    const fixture =
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
    ;

    try std.testing.expectError(error.MissingMarker, validatePhase9Phase10Handoff(fixture));
}

test "contract rejects Phase 10 routes before Phase 7 guardrails" {
    const fixture =
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
        \\      - name: Self-test current Phase 10 bootstrap route checker
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test
        \\      - name: Self-test current Phase 7 shared-control gap checker
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test
        \\      - name: Check current Phase 7 shared-control gap packet
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py
        \\      - name: Self-test current Phase 7 make-wrapper selftest alignment checker
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test
        \\      - name: Check current Phase 7 make-wrapper selftest alignment packet
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py
        \\      - name: Check current Phase 10 bootstrap route
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py
        \\      - name: Validate Phase 10 checker-backed review packet
        \\        run: make -C zigux phase10-validate
        \\      - name: Run Phase 10 helper tests
        \\        run: make -C zigux phase10-test
    ;

    try std.testing.expectError(error.ReorderedMarker, validatePhase9Phase10Handoff(fixture));
}

test "contract rejects duplicate handoff commands" {
    const duplicate = workflow ++ "\n        run: make -C zigux phase10-test\n";

    try std.testing.expectError(error.DuplicateMarker, validatePhase9Phase10Handoff(duplicate));
}

test "contract rejects stale broad aggregate workflow routes" {
    const stale = workflow ++ "\n        run: make -C zigux phase10\n";

    try std.testing.expectError(error.StaleMarker, validatePhase9Phase10Handoff(stale));
}
