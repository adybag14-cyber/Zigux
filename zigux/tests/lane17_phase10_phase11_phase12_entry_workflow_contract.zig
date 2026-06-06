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

const phase7_bridge = [_]Gate{
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
};

const phase10_phase11_bridge = [_]Gate{
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
    .{
        .name = "Self-test current Phase 11 build inventory checker",
        .command = "python3 scripts/zigux/check-phase11-build-inventory.py --self-test",
    },
    .{
        .name = "Check current Phase 11 build inventory packet",
        .command = "python3 scripts/zigux/check-phase11-build-inventory.py",
    },
    .{
        .name = "Validate current Phase 11 support bundle",
        .command = "make -C zigux phase11-validate",
    },
};

const phase12_entry_bridge = [_]Gate{
    .{
        .name = "Self-test current Phase 12 build-only surface checker",
        .command = "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    },
    .{
        .name = "Check current Phase 12 build-only surface",
        .command = "python3 scripts/zigux/check-build-only-phase12-surface.py",
    },
    .{
        .name = "Self-test current Phase 12 build inventory checker",
        .command = "python3 scripts/zigux/check-phase12-build-inventory.py --self-test",
    },
    .{
        .name = "Check current Phase 12 build inventory packet",
        .command = "python3 scripts/zigux/check-phase12-build-inventory.py",
    },
    .{
        .name = "Self-test current Phase 12 complex-driver lane packet checker",
        .command = "python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 12 complex-driver lane packet",
        .command = "python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py",
    },
    .{
        .name = "Self-test current Phase 12 cross-compile smoke checker",
        .command = "python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test",
    },
    .{
        .name = "Check current Phase 12 cross-compile smoke packet",
        .command = "python3 scripts/zigux/check-phase12-cross-compile-smoke.py",
    },
    .{
        .name = "Self-test current Phase 12 release-readiness packet checker",
        .command = "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 12 release-readiness packet",
        .command = "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
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

fn validatePhase10Phase11Phase12EntryWorkflow(text: []const u8) WorkflowError!void {
    var previous: ?usize = null;

    for (phase7_bridge) |gate| {
        try requireGateAfter(&previous, text, gate);
    }
    for (phase10_phase11_bridge) |gate| {
        try requireGateAfter(&previous, text, gate);
    }
    for (phase12_entry_bridge) |gate| {
        try requireGateAfter(&previous, text, gate);
    }

    try requireAbsent(text, "        run: make -C zigux phase7\n");
    try requireAbsent(text, "        run: make -C zigux phase10\n");
    try requireAbsent(text, "        run: make -C zigux phase11\n");
    try requireAbsent(text, "        run: make -C zigux phase12-build\n");
}

test "current bootstrap workflow keeps the Phase 10, Phase 11, and Phase 12 entry bridge ordered" {
    try validatePhase10Phase11Phase12EntryWorkflow(workflow);
}

test "contract rejects a missing Phase 11 validation gate before Phase 12 starts" {
    const fixture =
        \\      - name: Self-test current Phase 7 shared-control gap checker
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test
        \\      - name: Check current Phase 7 shared-control gap packet
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py
        \\      - name: Self-test current Phase 7 make-wrapper selftest alignment checker
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test
        \\      - name: Check current Phase 7 make-wrapper selftest alignment packet
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py
        \\      - name: Self-test current Phase 10 bootstrap route checker
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test
        \\      - name: Check current Phase 10 bootstrap route
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py
        \\      - name: Validate Phase 10 checker-backed review packet
        \\        run: make -C zigux phase10-validate
        \\      - name: Run Phase 10 helper tests
        \\        run: make -C zigux phase10-test
        \\      - name: Self-test current Phase 11 build inventory checker
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test
        \\      - name: Check current Phase 11 build inventory packet
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py
        \\      - name: Self-test current Phase 12 build-only surface checker
        \\        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
    ;

    try std.testing.expectError(error.MissingMarker, validatePhase10Phase11Phase12EntryWorkflow(fixture));
}

test "contract rejects Phase 12 entry before the Phase 10 helper route" {
    const fixture =
        \\      - name: Self-test current Phase 7 shared-control gap checker
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test
        \\      - name: Check current Phase 7 shared-control gap packet
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py
        \\      - name: Self-test current Phase 7 make-wrapper selftest alignment checker
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test
        \\      - name: Check current Phase 7 make-wrapper selftest alignment packet
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py
        \\      - name: Self-test current Phase 10 bootstrap route checker
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test
        \\      - name: Check current Phase 10 bootstrap route
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py
        \\      - name: Validate Phase 10 checker-backed review packet
        \\        run: make -C zigux phase10-validate
        \\      - name: Self-test current Phase 12 build-only surface checker
        \\        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
        \\      - name: Run Phase 10 helper tests
        \\        run: make -C zigux phase10-test
        \\      - name: Self-test current Phase 11 build inventory checker
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test
        \\      - name: Check current Phase 11 build inventory packet
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py
        \\      - name: Validate current Phase 11 support bundle
        \\        run: make -C zigux phase11-validate
        \\      - name: Check current Phase 12 build-only surface
        \\        run: python3 scripts/zigux/check-build-only-phase12-surface.py
        \\      - name: Self-test current Phase 12 build inventory checker
        \\        run: python3 scripts/zigux/check-phase12-build-inventory.py --self-test
        \\      - name: Check current Phase 12 build inventory packet
        \\        run: python3 scripts/zigux/check-phase12-build-inventory.py
        \\      - name: Self-test current Phase 12 complex-driver lane packet checker
        \\        run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test
        \\      - name: Check current Phase 12 complex-driver lane packet
        \\        run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py
        \\      - name: Self-test current Phase 12 cross-compile smoke checker
        \\        run: python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test
        \\      - name: Check current Phase 12 cross-compile smoke packet
        \\        run: python3 scripts/zigux/check-phase12-cross-compile-smoke.py
        \\      - name: Self-test current Phase 12 release-readiness packet checker
        \\        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test
        \\      - name: Check current Phase 12 release-readiness packet
        \\        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py
    ;

    try std.testing.expectError(error.ReorderedMarker, validatePhase10Phase11Phase12EntryWorkflow(fixture));
}

test "contract rejects duplicate early Phase 12 checker commands" {
    const duplicate = workflow ++ "\n        run: python3 scripts/zigux/check-phase12-build-inventory.py\n";

    try std.testing.expectError(error.DuplicateMarker, validatePhase10Phase11Phase12EntryWorkflow(duplicate));
}

test "contract rejects stale broad aggregate routes in this bridge" {
    const stale = workflow ++ "\n        run: make -C zigux phase11\n";

    try std.testing.expectError(error.StaleMarker, validatePhase10Phase11Phase12EntryWorkflow(stale));
}
