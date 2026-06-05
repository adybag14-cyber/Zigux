const std = @import("std");
const testing = std.testing;

const validator_source = @embedFile("validate-bootstrap.py");

const marker_tuple_names = [_][]const u8{
    "README_MARKERS = (",
    "ROADMAP_MARKERS = (",
    "LEDGER_MARKERS = (",
    "DOCS_README_MARKERS = (",
    "FREEZE_MAP_MARKERS = (",
    "SCRIPTS_README_MARKERS = (",
};

const marker_issue_codes = [_][]const u8{
    "MISSING_README_MARKER",
    "MISSING_ROADMAP_MARKER",
    "MISSING_LEDGER_MARKER",
    "MISSING_DOCS_README_MARKER",
    "MISSING_FREEZE_MAP_MARKER",
    "MISSING_SCRIPTS_README_MARKER",
};

const required_doc_markers = [_][]const u8{
    "`zigux-alpha` is the Zigux bootstrap workspace.",
    "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "## Bootstrap Status Note",
    "## Phase 1: Alpha Host-Side Helpers",
    "3. `build(scripts/zigux): add bootstrap validation and toolchain checks`",
    "- `scripts/zigux/validate-bootstrap.py`",
    "# Zigux Documentation This directory is the product documentation root for Zigux.",
    "- review rules",
    "## Freeze In C Initially",
    "- `kernel/workqueue.c`",
    "# scripts/zigux",
    "This directory holds shipped Zigux validation helpers and compact reminder surfaces.",
};

fn expectContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, validator_source, needle) != null);
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, validator_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, validator_source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn countOccurrences(needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, validator_source, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

test "validate-bootstrap keeps each documentation marker family wired to issue codes" {
    for (marker_tuple_names) |tuple_name| {
        try expectContains(tuple_name);
    }

    inline for (marker_issue_codes) |issue_code| {
        try expectContains(issue_code);
        try expectContains(issue_code ++ "_START");
        try expectContains(issue_code ++ "_END");
    }

    for (required_doc_markers) |marker| {
        try expectContains(marker);
    }
}

test "marker family checks remain ordered before workflow checks" {
    try expectBefore("for marker in README_MARKERS:", "for marker in ROADMAP_MARKERS:");
    try expectBefore("for marker in ROADMAP_MARKERS:", "for marker in LEDGER_MARKERS:");
    try expectBefore("for marker in LEDGER_MARKERS:", "for marker in DOCS_README_MARKERS:");
    try expectBefore("for marker in DOCS_README_MARKERS:", "for marker in FREEZE_MAP_MARKERS:");
    try expectBefore("for marker in FREEZE_MAP_MARKERS:", "for marker in SCRIPTS_README_MARKERS:");
    try expectBefore("for marker in SCRIPTS_README_MARKERS:", "for marker in REQUIRED_WORKFLOW_LINES:");
}

test "built-in self-test still exercises representative marker failures" {
    try expectContains("assert (\"MISSING_README_MARKER\", README_MARKERS[1]) in collect_issues(root)");
    try expectContains("assert (\"MISSING_ROADMAP_MARKER\", ROADMAP_MARKERS[1]) in collect_issues(root)");
    try expectContains("assert (\"MISSING_LEDGER_MARKER\", LEDGER_MARKERS[1]) in collect_issues(root)");
    try expectContains("assert (\"MISSING_FREEZE_MAP_MARKER\", FREEZE_MAP_MARKERS[3]) in collect_issues(root)");
    try expectContains("BOOTSTRAP_VALIDATION_SELF_TEST=pass");
    try expectContains("BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT");
}

test "validator pass output keeps marker checks within bootstrap status contract" {
    try expectContains("BOOTSTRAP_VALIDATION=fail");
    try expectContains("BOOTSTRAP_VALIDATION=pass");
    try expectContains("BOOTSTRAP_REQUIRED_PATH_COUNT");
    try expectContains("BOOTSTRAP_WORKFLOW_LINE_COUNT");
    try testing.expectEqual(@as(usize, 1), countOccurrences("DOCS_README_MARKERS = ("));
    try testing.expectEqual(@as(usize, 1), countOccurrences("SCRIPTS_README_MARKERS = ("));
}
