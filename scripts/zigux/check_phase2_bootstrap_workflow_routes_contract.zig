const std = @import("std");

const checker_source = @embedFile("check-phase2-bootstrap-workflow-routes.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 bootstrap workflow route checker keeps public self-test action path" {
    try expectContains(checker_source, "def run_self_test() -> int:");
    try expectContains(checker_source, "EXPECTED_SELF_TEST_CASE_COUNT = 24");
    try expectContains(checker_source, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST=pass");
    try expectContains(checker_source, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST_CASE_COUNT");
    try expectContains(checker_source, "--self-test");
    try expectContains(checker_source, "--write-sample-root");
    try expectContains(checker_source, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES=pass");
}

test "phase2 bootstrap workflow route checker anchors policy driven route surfaces" {
    try expectContains(checker_source, "scripts/zigux/zig-toolchain-policy.json");
    try expectContains(checker_source, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    try expectContains(checker_source, ".github/workflows/zigux-bootstrap.yml");
    try expectContains(checker_source, "zigux/Makefile");
    try expectContains(checker_source, "required_make_routes");
    try expectContains(checker_source, "AGGREGATE_ROUTE = \"phase2\"");
}

test "phase2 bootstrap workflow route checker preserves current route list" {
    try expectContains(checker_source, "phase2-toolchain");
    try expectContains(checker_source, "phase2-tools");
    try expectContains(checker_source, "phase2-kconfig");
    try expectContains(checker_source, "phase2-cross");
    try expectContains(checker_source, "phase2-genksyms");
    try expectContains(checker_source, "phase2-fixdep");
    try expectContains(checker_source, "phase2-validate");
}

test "phase2 bootstrap workflow route checker guards note workflow and makefile markers" {
    try expectContains(checker_source, "def note_markers(routes: tuple[str, ...]) -> tuple[str, ...]:");
    try expectContains(checker_source, "`make -C zigux {route}`");
    try expectContains(checker_source, "def workflow_lines(routes: tuple[str, ...]) -> tuple[str, ...]:");
    try expectContains(checker_source, "run: make -C zigux {route}");
    try expectContains(checker_source, "def makefile_rule_lines(routes: tuple[str, ...]) -> tuple[str, ...]:");
    try expectContains(checker_source, "{AGGREGATE_ROUTE}: {routes[-1]}");
    try expectContains(checker_source, "def phony_tokens(routes: tuple[str, ...]) -> tuple[str, ...]:");
}

test "phase2 bootstrap workflow route checker keeps fail closed diagnostics" {
    try expectContains(checker_source, "missing_file:");
    try expectContains(checker_source, "invalid_policy:");
    try expectContains(checker_source, "invalid required_make_routes");
    try expectContains(checker_source, "duplicate required_make_routes");
    try expectContains(checker_source, "expected_once:actual_count");
    try expectContains(checker_source, "phase2-future");
}
