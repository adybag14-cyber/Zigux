const std = @import("std");

const route_summary_checker_contract =
    \\REQUIRED_FILES = (
    \\"Documentation/zigux/README.md",
    \\"Documentation/zigux/phase1-closure.md",
    \\"Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    \\"scripts/zigux/README.md",
    \\"zigux/tests/README.md",
    \\"zigux/Makefile",
    \\".github/workflows/zigux-bootstrap.yml",
    \\)
    \\EXACT_LINE_MARKERS = {
    \\"- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    \\"- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    \\"- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    \\"- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
    \\"phase1-route-summary:",
    \\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    \\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    \\"run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    \\"run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    \\}
    \\FORBIDDEN_EXACT_LINES = {
    \\"phase1-validate:",
    \\"phase1-test:",
    \\"phase1-bench:",
    \\"phase1:",
    \\}
    \\PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass
    \\PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST_CASE_COUNT={len(cases)}
    \\PHASE1_ROUTE_SUMMARY_COUNTS=pass
    \\PHASE1_ROUTE_SUMMARY_COUNTS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}
    \\PHASE1_ROUTE_SUMMARY_COUNTS_REQUIRED_MARKER_COUNT=
;

const required_files = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
};

const workflow_commands = [_][]const u8{
    "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py\"",
    "\"run: python3 scripts/zigux/check-phase1-bench.py --self-test\"",
    "\"run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\"",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, haystack, needle));
}

test "route-summary checker keeps the current required file roster visible" {
    try expectContains(route_summary_checker_contract, "REQUIRED_FILES = (");
    for (required_files) |path| {
        try expectContains(route_summary_checker_contract, path);
    }

    try expectContains(route_summary_checker_contract, "EXACT_LINE_MARKERS = {");
    try expectContains(route_summary_checker_contract, "FORBIDDEN_EXACT_LINES = {");
    try expectContains(route_summary_checker_contract, "PHASE1_ROUTE_SUMMARY_COUNTS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}");
    try expectContains(route_summary_checker_contract, "PHASE1_ROUTE_SUMMARY_COUNTS_REQUIRED_MARKER_COUNT=");
}

test "route-summary checker pins workflow gate commands in order" {
    var previous_index: usize = 0;
    for (workflow_commands, 0..) |command, idx| {
        const found_index = std.mem.indexOf(u8, route_summary_checker_contract, command) orelse return error.MissingWorkflowCommand;
        if (idx != 0) {
            try std.testing.expect(found_index > previous_index);
        }
        previous_index = found_index;
    }

    try expectContainsOnce(route_summary_checker_contract, "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\"");
    try expectContainsOnce(route_summary_checker_contract, "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py\"");
}

test "route-summary checker guards Phase 1 Makefile route posture" {
    try expectContains(route_summary_checker_contract, "phase1-route-summary:");
    try expectContains(route_summary_checker_contract, "\"phase1-validate:\"");
    try expectContains(route_summary_checker_contract, "\"phase1-test:\"");
    try expectContains(route_summary_checker_contract, "\"phase1-bench:\"");
    try expectContains(route_summary_checker_contract, "\"phase1:\"");
    try expectContains(route_summary_checker_contract, "PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass");
    try expectContains(route_summary_checker_contract, "PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST_CASE_COUNT={len(cases)}");
}
