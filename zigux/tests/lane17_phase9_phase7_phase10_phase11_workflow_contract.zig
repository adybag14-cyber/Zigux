const std = @import("std");

const workflow_path = @import("build_options").workflow_path;

const WorkflowContractError = error{
    MissingMarker,
    MarkerOutOfOrder,
    DuplicateMarker,
};

fn loadWorkflow(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, allocator, .limited(1024 * 1024));
}

fn markerEndsAtLineBoundary(haystack: []const u8, end: usize) bool {
    return end == haystack.len or haystack[end] == '\n' or haystack[end] == '\r';
}

fn requireOnce(haystack: []const u8, needle: []const u8) !usize {
    var first_valid: ?usize = null;
    var search_start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, search_start, needle)) |index| {
        const end = index + needle.len;
        if (markerEndsAtLineBoundary(haystack, end)) {
            if (first_valid != null) return WorkflowContractError.DuplicateMarker;
            first_valid = index;
        }
        search_start = end;
    }
    return first_valid orelse WorkflowContractError.MissingMarker;
}

fn requireAfter(haystack: []const u8, needle: []const u8, previous: usize) !usize {
    const index = try requireOnce(haystack, needle);
    if (index <= previous) return WorkflowContractError.MarkerOutOfOrder;
    return index;
}

fn requireSequence(haystack: []const u8, markers: []const []const u8) !void {
    var previous: usize = 0;
    var have_previous = false;
    for (markers) |marker| {
        const index = try requireOnce(haystack, marker);
        if (have_previous and index <= previous) return WorkflowContractError.MarkerOutOfOrder;
        previous = index;
        have_previous = true;
    }
}

test "phase9 runtime witnesses hand off to phase7 shared-control gates" {
    const allocator = std.testing.allocator;

    const workflow = try loadWorkflow(allocator);
    defer allocator.free(workflow);

    try requireSequence(workflow, &.{
        "- name: Run current Phase 9 trace-events runtime sample tests",
        "run: zig test samples/zigux/runtime_trace_events.zig",
        "- name: Run current Phase 9 unregistered gate companion tests",
        "run: zig test samples/zigux/runtime_trace_events_unregistered_gate.zig",
        "- name: Run current Phase 9 exit rollback guard companion tests",
        "run: zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
        "- name: Run current Phase 9 registration reentry companion tests",
        "run: zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
        "- name: Run current Phase 9 reinit rollback guard companion tests",
        "run: zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
        "- name: Run current Phase 9 reinit reexit guard companion tests",
        "run: zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
        "- name: Run current Phase 9 trace-events survey witness",
        "run: zig test zigux/tests/runtime_trace_events_survey.zig",
        "- name: Self-test current Phase 7 shared-control gap checker",
        "run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
        "- name: Check current Phase 7 shared-control gap packet",
        "run: python3 scripts/zigux/check-phase7-shared-control-gap.py",
    });
}

test "phase7 make-wrapper alignment stays before phase10 bootstrap routes" {
    const allocator = std.testing.allocator;

    const workflow = try loadWorkflow(allocator);
    defer allocator.free(workflow);

    const phase7_check = try requireOnce(workflow, "- name: Check current Phase 7 make-wrapper selftest alignment packet");
    _ = try requireAfter(workflow, "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py", phase7_check);

    try requireSequence(workflow, &.{
        "- name: Self-test current Phase 7 make-wrapper selftest alignment checker",
        "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "- name: Check current Phase 7 make-wrapper selftest alignment packet",
        "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "- name: Self-test current Phase 10 bootstrap route checker",
        "run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test",
        "- name: Check current Phase 10 bootstrap route",
        "run: python3 scripts/zigux/check-phase10-bootstrap-route.py",
    });
}

test "phase10 validation and test routes remain ahead of phase11 inventory" {
    const allocator = std.testing.allocator;

    const workflow = try loadWorkflow(allocator);
    defer allocator.free(workflow);

    try requireSequence(workflow, &.{
        "- name: Validate Phase 10 checker-backed review packet",
        "run: make -C zigux phase10-validate",
        "- name: Run Phase 10 helper tests",
        "run: make -C zigux phase10-test",
        "- name: Self-test current Phase 11 build inventory checker",
        "run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test",
        "- name: Check current Phase 11 build inventory packet",
        "run: python3 scripts/zigux/check-phase11-build-inventory.py",
    });
}

test "phase11 support bundle anchors the phase12 entry" {
    const allocator = std.testing.allocator;

    const workflow = try loadWorkflow(allocator);
    defer allocator.free(workflow);

    try requireSequence(workflow, &.{
        "- name: Validate current Phase 11 support bundle",
        "run: make -C zigux phase11-validate",
        "- name: Self-test current Phase 12 build-only surface checker",
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "- name: Check current Phase 12 build-only surface",
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py",
    });
}
