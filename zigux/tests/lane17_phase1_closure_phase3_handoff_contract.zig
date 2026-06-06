const std = @import("std");

const workflow_path = @import("lane17_phase1_closure_phase3_handoff_options").workflow_path;

const Phase1Phase3Markers = struct {
    direct_owner_selftest: []const u8 = "Self-test current Phase 1 direct-owner checker",
    shared_reminder_check: []const u8 = "Check current Phase 1 shared reminder packet",
    closure_selftest: []const u8 = "Self-test current Phase 1 closure validator",
    closure_check: []const u8 = "Check current Phase 1 closure packet",
    phase3_selftest: []const u8 = "Self-test current Phase 3 interop packet",
    phase3_check: []const u8 = "Check current Phase 3 interop packet",
    phase3_header_smoke: []const u8 = "Run current Phase 3 export/UAPI C header smoke",
    phase3_shared_tests: []const u8 = "Run current Phase 3 shared tests-root packet",
    phase1_tail_smoke: []const u8 = "Run current Phase 1 shared tests-root smoke",
    phase4_warning_selftest: []const u8 = "Self-test current Phase 4 repo-reality warning checker",
};

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingWorkflowMarker;
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = try indexOfRequired(haystack, before);
    const after_index = try indexOfRequired(haystack, after);
    try std.testing.expect(before_index < after_index);
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |offset| {
        count += 1;
        rest = rest[offset + needle.len ..];
    }
    if (count == 0) return error.MissingWorkflowMarker;
    if (count > 1) return error.DuplicateWorkflowMarker;
}

fn validatePhase1ClosurePhase3Handoff(workflow: []const u8) !void {
    const markers = Phase1Phase3Markers{};

    try expectOnce(workflow, markers.closure_selftest);
    try expectOnce(workflow, markers.closure_check);
    try expectOnce(workflow, markers.phase3_selftest);
    try expectOnce(workflow, markers.phase3_check);

    try expectBefore(workflow, markers.direct_owner_selftest, markers.shared_reminder_check);
    try expectBefore(workflow, markers.shared_reminder_check, markers.closure_selftest);
    try expectBefore(workflow, markers.closure_selftest, markers.closure_check);
    try expectBefore(workflow, markers.closure_check, markers.phase3_selftest);
    try expectBefore(workflow, markers.phase3_selftest, markers.phase3_check);
    try expectBefore(workflow, markers.phase3_check, markers.phase3_header_smoke);
    try expectBefore(workflow, markers.phase3_header_smoke, markers.phase3_shared_tests);
    try expectBefore(workflow, markers.phase3_shared_tests, markers.phase1_tail_smoke);
    try expectBefore(workflow, markers.phase1_tail_smoke, markers.phase4_warning_selftest);
}

test "lane17 current workflow keeps Phase 1 closure before Phase 3 checks" {
    const workflow = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, std.testing.allocator, .limited(512 * 1024));
    defer std.testing.allocator.free(workflow);

    try validatePhase1ClosurePhase3Handoff(workflow);
}

test "lane17 handoff contract rejects stale Phase 3 before closure order" {
    const stale_workflow =
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\      - name: Check current Phase 1 shared reminder packet
        \\      - name: Self-test current Phase 3 interop packet
        \\      - name: Check current Phase 3 interop packet
        \\      - name: Self-test current Phase 1 closure validator
        \\      - name: Check current Phase 1 closure packet
        \\      - name: Run current Phase 3 export/UAPI C header smoke
        \\      - name: Run current Phase 3 shared tests-root packet
        \\      - name: Run current Phase 1 shared tests-root smoke
        \\      - name: Self-test current Phase 4 repo-reality warning checker
        \\
    ;

    try std.testing.expectError(error.TestUnexpectedResult, validatePhase1ClosurePhase3Handoff(stale_workflow));
}

test "lane17 handoff contract rejects missing closure validator check" {
    const incomplete_workflow =
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\      - name: Check current Phase 1 shared reminder packet
        \\      - name: Self-test current Phase 1 closure validator
        \\      - name: Self-test current Phase 3 interop packet
        \\      - name: Check current Phase 3 interop packet
        \\      - name: Run current Phase 3 export/UAPI C header smoke
        \\      - name: Run current Phase 3 shared tests-root packet
        \\      - name: Run current Phase 1 shared tests-root smoke
        \\      - name: Self-test current Phase 4 repo-reality warning checker
        \\
    ;

    try std.testing.expectError(error.MissingWorkflowMarker, validatePhase1ClosurePhase3Handoff(incomplete_workflow));
}
