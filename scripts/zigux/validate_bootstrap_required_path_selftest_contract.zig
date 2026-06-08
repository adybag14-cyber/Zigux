const std = @import("std");
const validate_bootstrap = @embedFile("validate-bootstrap.py");

const required_paths = [_][]const u8{
    "\"scripts/zigux/check-zig-toolchain.py\"",
    "\"scripts/zigux/check-lane05-local-first-archive-workflow.py\"",
    "\"scripts/zigux/check-lane05-local-archive-readme.py\"",
    "\"scripts/zigux/check-lane05-install-zig-archive-verification.py\"",
    "\"scripts/zigux/stage-pinned-zig-archive.py\"",
    "\"scripts/zigux/check-lane05-stage-helper-contract.py\"",
    "\"scripts/zigux/check-lane05-stage-helper-selftest.py\"",
    "\"scripts/zigux/check-phase1-route-summary-counts.py\"",
    "\"scripts/zigux/install-zig.py\"",
    "\"scripts/zigux/validate-bootstrap.py\"",
    "\"scripts/zigux/zig-toolchain-policy.json\"",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "validate-bootstrap keeps required toolchain and stage paths" {
    try expectContains(validate_bootstrap, "REQUIRED_PATHS = (");
    try expectContains(validate_bootstrap, "for rel in REQUIRED_PATHS:");
    try expectContains(validate_bootstrap, "(\"MISSING_REQUIRED_PATH\", rel)");

    inline for (required_paths) |path| {
        try expectContains(validate_bootstrap, path);
    }

    try expectBefore(
        validate_bootstrap,
        "\"scripts/zigux/check-zig-toolchain.py\"",
        "\"scripts/zigux/install-zig.py\"",
    );
    try expectBefore(
        validate_bootstrap,
        "\"scripts/zigux/install-zig.py\"",
        "\"scripts/zigux/zig-toolchain-policy.json\"",
    );
}

test "validate-bootstrap pins full required path and marker inventory" {
    const required_start = "REQUIRED_PATHS = (";
    try expectContains(validate_bootstrap, required_start);
    const required_block = validate_bootstrap[std.mem.indexOf(u8, validate_bootstrap, required_start).?..];
    const required_tuple_end = std.mem.indexOf(u8, required_block, "\n)\n") orelse return error.RequiredTupleEndMissing;
    const required_tuple = required_block[0..required_tuple_end];

    const required_inventory = [_][]const u8{
        "\"zigux-alpha/README.md\"",
        "\"zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md\"",
        "\"zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md\"",
        "\"Documentation/zigux/README.md\"",
        "\"Documentation/zigux/review-checklist.md\"",
        "\"Documentation/zigux/freeze-map.md\"",
        "\"scripts/zigux/README.md\"",
        "\"scripts/zigux/check-zig-toolchain.py\"",
        "\"scripts/zigux/check-lane01-bootstrap-charter-alignment.py\"",
        "\"scripts/zigux/check-lane05-local-first-archive-workflow.py\"",
        "\"scripts/zigux/check-lane05-local-archive-readme.py\"",
        "\"scripts/zigux/check-lane05-install-zig-archive-verification.py\"",
        "\"scripts/zigux/stage-pinned-zig-archive.py\"",
        "\"scripts/zigux/check-lane05-stage-helper-contract.py\"",
        "\"scripts/zigux/check-lane05-stage-helper-selftest.py\"",
        "\"scripts/zigux/check-phase1-route-summary-counts.py\"",
        "\"scripts/zigux/install-zig.py\"",
        "\"scripts/zigux/validate-bootstrap.py\"",
        "\"scripts/zigux/zig-toolchain-policy.json\"",
        "\"zigux/tests/README.md\"",
        "WORKFLOW,",
    };
    try std.testing.expectEqual(@as(usize, 21), required_inventory.len);
    inline for (required_inventory) |path| {
        try expectContains(required_tuple, path);
    }

    try expectBefore(required_tuple, required_inventory[0], required_inventory[3]);
    try expectBefore(required_tuple, required_inventory[3], required_inventory[7]);
    try expectBefore(required_tuple, required_inventory[7], required_inventory[16]);
    try expectBefore(required_tuple, required_inventory[18], required_inventory[19]);
    try expectBefore(required_tuple, required_inventory[19], required_inventory[20]);

    const marker_groups = [_][]const u8{
        "README_MARKERS = (",
        "ROADMAP_MARKERS = (",
        "LEDGER_MARKERS = (",
        "DOCS_README_MARKERS = (",
        "FREEZE_MAP_MARKERS = (",
        "SCRIPTS_README_MARKERS = (",
    };
    inline for (marker_groups) |group| {
        try expectContains(validate_bootstrap, group);
    }
    try expectBefore(validate_bootstrap, marker_groups[0], marker_groups[1]);
    try expectBefore(validate_bootstrap, marker_groups[1], marker_groups[2]);
    try expectBefore(validate_bootstrap, marker_groups[2], marker_groups[3]);
    try expectBefore(validate_bootstrap, marker_groups[3], marker_groups[4]);
    try expectBefore(validate_bootstrap, marker_groups[4], marker_groups[5]);

    try expectBefore(validate_bootstrap, "for marker in README_MARKERS:", "for marker in ROADMAP_MARKERS:");
    try expectBefore(validate_bootstrap, "for marker in ROADMAP_MARKERS:", "for marker in LEDGER_MARKERS:");
    try expectBefore(validate_bootstrap, "for marker in LEDGER_MARKERS:", "for marker in DOCS_README_MARKERS:");
    try expectBefore(validate_bootstrap, "for marker in DOCS_README_MARKERS:", "for marker in FREEZE_MAP_MARKERS:");
    try expectBefore(validate_bootstrap, "for marker in FREEZE_MAP_MARKERS:", "for marker in SCRIPTS_README_MARKERS:");
}

test "validate-bootstrap self-test covers missing path diagnostics" {
    const self_test_start = "def run_self_test() -> int:";
    try expectContains(validate_bootstrap, self_test_start);
    const self_test = validate_bootstrap[std.mem.indexOf(u8, validate_bootstrap, self_test_start).?..];

    const missing_path_expectations = [_][]const u8{
        "\"scripts/zigux/check-zig-toolchain.py\"",
        "\"scripts/zigux/check-phase1-route-summary-counts.py\"",
        "\"scripts/zigux/stage-pinned-zig-archive.py\"",
        "\"scripts/zigux/check-lane05-stage-helper-selftest.py\"",
        "\"scripts/zigux/install-zig.py\"",
        "\"scripts/zigux/zig-toolchain-policy.json\"",
    };

    inline for (missing_path_expectations) |path| {
        try expectContains(self_test, path ++ ").unlink()");
        try std.testing.expect(countOccurrences(self_test, path) >= 2);
    }

    try std.testing.expect(countOccurrences(self_test, "\"MISSING_REQUIRED_PATH\"") >= missing_path_expectations.len);
    try expectContains(self_test, "BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT={checks}");
}

test "validate-bootstrap self-test covers workflow line drift" {
    const self_test_start = "def run_self_test() -> int:";
    try expectContains(validate_bootstrap, self_test_start);
    const self_test = validate_bootstrap[std.mem.indexOf(u8, validate_bootstrap, self_test_start).?..];

    const missing_workflow_lines = [_][]const u8{
        "\"run: python3 scripts/zigux/install-zig.py --self-test\"",
        "\"run: python3 scripts/zigux/check-lane05-stage-helper-contract.py\"",
    };
    inline for (missing_workflow_lines) |line| {
        try expectContains(self_test, "replace_exact_line(");
        try expectContains(self_test, line);
        try expectContains(self_test, "\"MISSING_WORKFLOW_LINE\"");
    }

    const duplicate_workflow_lines = [_][]const u8{
        "REQUIRED_WORKFLOW_LINES[2]",
        "REQUIRED_WORKFLOW_LINES[-1]",
    };
    inline for (duplicate_workflow_lines) |line| {
        try expectContains(self_test, "duplicate_exact_line(");
        try expectContains(self_test, line);
    }

    try expectContains(self_test, "\"DUPLICATE_WORKFLOW_LINE\"");
    try expectContains(self_test, ":count=2");
    try expectBefore(self_test, "\"MISSING_WORKFLOW_LINE\"", "\"DUPLICATE_WORKFLOW_LINE\"");
}

test "validate-bootstrap pins workflow inventory and diagnostics" {
    const workflow_start = "REQUIRED_WORKFLOW_LINES = (";
    try expectContains(validate_bootstrap, "WORKFLOW = \".github/workflows/zigux-bootstrap.yml\"");
    try expectContains(validate_bootstrap, workflow_start);
    const workflow_block = validate_bootstrap[std.mem.indexOf(u8, validate_bootstrap, workflow_start).?..];
    const workflow_tuple_end = std.mem.indexOf(u8, workflow_block, "\n)\n") orelse return error.WorkflowTupleEndMissing;
    const workflow_tuple = workflow_block[0..workflow_tuple_end];

    const workflow_lines = [_][]const u8{
        "\"run: python3 scripts/zigux/check-zig-toolchain.py --self-test\"",
        "\"run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\"",
        "\"run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\"",
        "\"run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test\"",
        "\"run: python3 scripts/zigux/install-zig.py --self-test\"",
        "\"run: python3 scripts/zigux/validate-bootstrap.py --self-test\"",
        "\"run: python3 scripts/zigux/validate-bootstrap.py\"",
    };
    inline for (workflow_lines) |line| {
        try expectContains(workflow_tuple, line);
    }

    try std.testing.expectEqual(@as(usize, 23), countOccurrences(workflow_tuple, "\"run: "));
    try expectBefore(workflow_tuple, workflow_lines[0], workflow_lines[3]);
    try expectBefore(workflow_tuple, workflow_lines[3], workflow_lines[4]);
    try expectBefore(workflow_tuple, workflow_lines[4], workflow_lines[5]);
    try expectBefore(workflow_tuple, workflow_lines[5], workflow_lines[6]);

    try expectContains(validate_bootstrap, "for marker in REQUIRED_WORKFLOW_LINES:");
    try expectContains(validate_bootstrap, "count = count_exact_lines(workflow, marker)");
    try expectContains(validate_bootstrap, "issues.append((\"MISSING_WORKFLOW_LINE\", marker))");
    try expectContains(validate_bootstrap, "issues.append((\"DUPLICATE_WORKFLOW_LINE\", f\"{marker}:count={count}\"))");
    try expectBefore(
        validate_bootstrap,
        "issues.append((\"MISSING_WORKFLOW_LINE\", marker))",
        "issues.append((\"DUPLICATE_WORKFLOW_LINE\", f\"{marker}:count={count}\"))",
    );
}

test "validate-bootstrap emits summary counts for downstream gates" {
    try expectContains(validate_bootstrap, "BOOTSTRAP_VALIDATION=pass");
    try expectContains(validate_bootstrap, "BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}");
    try expectContains(validate_bootstrap, "BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}");
    try expectBefore(
        validate_bootstrap,
        "BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}",
        "BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}",
    );
}
