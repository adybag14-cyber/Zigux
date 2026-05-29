const std = @import("std");

const shared_reminder_self_test_step =
    "      - name: Self-test current Phase 1 shared reminder checker\n" ++
    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test";

const shared_reminder_live_check_step =
    "      - name: Check current Phase 1 shared reminder packet\n" ++
    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py";

const closure_self_test_step =
    "      - name: Self-test current Phase 1 closure validator\n" ++
    "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test";

const closure_live_check_step =
    "      - name: Check current Phase 1 closure packet\n" ++
    "        run: python3 scripts/zigux/validate-phase1-closure.py";

const phase3_self_test_step =
    "      - name: Self-test current Phase 3 interop packet\n" ++
    "        run: python3 scripts/zigux/validate_phase3_selftest.py";

const phase3_live_check_step =
    "      - name: Check current Phase 3 interop packet\n" ++
    "        run: python3 scripts/zigux/run-phase3-checks.py";

const expected_closure_handoff_cluster =
    shared_reminder_self_test_step ++
    "\n\n" ++
    shared_reminder_live_check_step ++
    "\n\n" ++
    closure_self_test_step ++
    "\n\n" ++
    closure_live_check_step ++
    "\n\n" ++
    phase3_self_test_step ++
    "\n\n" ++
    phase3_live_check_step ++
    "\n";

fn requireSingleMarker(source: []const u8, marker: []const u8) !usize {
    const first = std.mem.indexOf(u8, source, marker) orelse return error.MissingWorkflowMarker;
    if (std.mem.indexOfPos(u8, source, first + marker.len, marker) != null) {
        return error.DuplicateWorkflowMarker;
    }
    return first;
}

fn requireBefore(earlier: usize, later: usize) !void {
    if (earlier >= later) return error.WorkflowMarkerOutOfOrder;
}

fn requirePhase1ClosureToPhase3WorkflowCluster(workflow: []const u8) !void {
    const shared_reminder_self_test = try requireSingleMarker(workflow, shared_reminder_self_test_step);
    const shared_reminder_live_check = try requireSingleMarker(workflow, shared_reminder_live_check_step);
    const closure_self_test = try requireSingleMarker(workflow, closure_self_test_step);
    const closure_live_check = try requireSingleMarker(workflow, closure_live_check_step);
    const phase3_self_test = try requireSingleMarker(workflow, phase3_self_test_step);
    const phase3_live_check = try requireSingleMarker(workflow, phase3_live_check_step);

    try requireBefore(shared_reminder_self_test, shared_reminder_live_check);
    try requireBefore(shared_reminder_live_check, closure_self_test);
    try requireBefore(closure_self_test, closure_live_check);
    try requireBefore(closure_live_check, phase3_self_test);
    try requireBefore(phase3_self_test, phase3_live_check);
}

test "lane17 phase1 closure to phase3 workflow cluster accepts intended order" {
    try requirePhase1ClosureToPhase3WorkflowCluster(expected_closure_handoff_cluster);
}

test "lane17 phase1 closure to phase3 workflow cluster rejects missing closure live check" {
    const missing_closure_live_check =
        shared_reminder_self_test_step ++
        "\n\n" ++
        shared_reminder_live_check_step ++
        "\n\n" ++
        closure_self_test_step ++
        "\n\n" ++
        phase3_self_test_step ++
        "\n\n" ++
        phase3_live_check_step ++
        "\n";

    try std.testing.expectError(
        error.MissingWorkflowMarker,
        requirePhase1ClosureToPhase3WorkflowCluster(missing_closure_live_check),
    );
}

test "lane17 phase1 closure to phase3 workflow cluster rejects closure live check before self-test" {
    const closure_live_check_before_self_test =
        shared_reminder_self_test_step ++
        "\n\n" ++
        shared_reminder_live_check_step ++
        "\n\n" ++
        closure_live_check_step ++
        "\n\n" ++
        closure_self_test_step ++
        "\n\n" ++
        phase3_self_test_step ++
        "\n\n" ++
        phase3_live_check_step ++
        "\n";

    try std.testing.expectError(
        error.WorkflowMarkerOutOfOrder,
        requirePhase1ClosureToPhase3WorkflowCluster(closure_live_check_before_self_test),
    );
}

test "lane17 phase1 closure to phase3 workflow cluster rejects duplicate phase3 self-test" {
    const duplicate_phase3_self_test =
        shared_reminder_self_test_step ++
        "\n\n" ++
        shared_reminder_live_check_step ++
        "\n\n" ++
        closure_self_test_step ++
        "\n\n" ++
        closure_live_check_step ++
        "\n\n" ++
        phase3_self_test_step ++
        "\n\n" ++
        phase3_self_test_step ++
        "\n\n" ++
        phase3_live_check_step ++
        "\n";

    try std.testing.expectError(
        error.DuplicateWorkflowMarker,
        requirePhase1ClosureToPhase3WorkflowCluster(duplicate_phase3_self_test),
    );
}

test "lane17 phase1 closure to phase3 workflow cluster rejects phase3 before closure packet" {
    const phase3_before_closure_packet =
        shared_reminder_self_test_step ++
        "\n\n" ++
        shared_reminder_live_check_step ++
        "\n\n" ++
        closure_self_test_step ++
        "\n\n" ++
        phase3_self_test_step ++
        "\n\n" ++
        closure_live_check_step ++
        "\n\n" ++
        phase3_live_check_step ++
        "\n";

    try std.testing.expectError(
        error.WorkflowMarkerOutOfOrder,
        requirePhase1ClosureToPhase3WorkflowCluster(phase3_before_closure_packet),
    );
}
