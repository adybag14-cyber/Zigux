const std = @import("std");
const testing = std.testing;

const required_workflow_lines = [_][]const u8{
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py --self-test",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: make -C zigux phase6-validate",
    "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    "run: python3 scripts/zigux/validate-bootstrap.py",
};

const validator_source = @embedFile("validate-bootstrap.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

test "bootstrap validator pins the complete workflow command roster" {
    try expectContains(validator_source, "REQUIRED_WORKFLOW_LINES = (");
    try testing.expectEqual(@as(usize, 23), required_workflow_lines.len);

    for (required_workflow_lines) |line| {
        try expectContains(validator_source, line);
        try testing.expect(countOccurrences(validator_source, line) >= 1);
    }
}

test "workflow line validation fails closed on missing or duplicated exact lines" {
    try expectContains(validator_source, "count_exact_lines(workflow, marker)");
    try expectContains(validator_source, "if count == 0:");
    try expectContains(validator_source, "issues.append((\"MISSING_WORKFLOW_LINE\", marker))");
    try expectContains(validator_source, "elif count != 1:");
    try expectContains(validator_source, "issues.append((\"DUPLICATE_WORKFLOW_LINE\", f\"{marker}:count={count}\"))");
    try expectContains(validator_source, "def duplicate_exact_line(text: str, marker: str) -> str:");
    try expectContains(validator_source, "REQUIRED_WORKFLOW_LINES[2]");
    try expectContains(validator_source, "REQUIRED_WORKFLOW_LINES[-1]");
}

test "self-test mutates the critical bootstrap workflow and path sentinels" {
    const self_test_needles = [_][]const u8{
        "run: python3 scripts/zigux/install-zig.py --self-test",
        "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
        "scripts/zigux/check-zig-toolchain.py",
        "scripts/zigux/check-phase1-route-summary-counts.py",
        "scripts/zigux/stage-pinned-zig-archive.py",
        "scripts/zigux/check-lane05-stage-helper-selftest.py",
        "scripts/zigux/install-zig.py",
        "scripts/zigux/zig-toolchain-policy.json",
    };

    try expectContains(validator_source, "def run_self_test() -> int:");
    try expectContains(validator_source, "BOOTSTRAP_VALIDATION_SELF_TEST=pass");
    for (self_test_needles) |needle| {
        try expectContains(validator_source, needle);
    }
}

test "validator reports stable bootstrap pass/fail and count status keys" {
    const status_needles = [_][]const u8{
        "BOOTSTRAP_VALIDATION=fail",
        "MISSING_REQUIRED_PATH_START",
        "MISSING_WORKFLOW_LINE",
        "DUPLICATE_WORKFLOW_LINE",
        "BOOTSTRAP_VALIDATION=pass",
        "BOOTSTRAP_REQUIRED_PATH_COUNT",
        "BOOTSTRAP_WORKFLOW_LINE_COUNT",
        "BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT",
    };

    for (status_needles) |needle| {
        try expectContains(validator_source, needle);
    }
}
