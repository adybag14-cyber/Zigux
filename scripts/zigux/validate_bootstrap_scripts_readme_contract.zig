const std = @import("std");

const validator_source = @embedFile("validate-bootstrap.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBefore;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfter;
    try std.testing.expect(before_index < after_index);
}

test "scripts README markers stay part of bootstrap validation" {
    try expectContains(validator_source, "SCRIPTS_README_MARKERS = (");
    try expectContains(validator_source, "\"# scripts/zigux\"");
    try expectContains(validator_source, "\"This directory holds shipped Zigux validation helpers and compact reminder surfaces.\"");
    try expectContains(validator_source, "\"scripts/zigux/check-zig-toolchain.py\"");
    try expectContains(validator_source, "\"scripts/zigux/check-lane01-bootstrap-charter-alignment.py\"");
    try expectContains(validator_source, "scripts_readme = read_text(root, \"scripts/zigux/README.md\")");
}

test "scripts README marker failures use grouped bootstrap diagnostics" {
    try expectContains(validator_source, "MISSING_SCRIPTS_README_MARKER");
    try expectContains(validator_source, "for marker in SCRIPTS_README_MARKERS:");
    try expectContains(validator_source, "if marker not in scripts_readme:");
    try expectContains(validator_source, "issues.append((\"MISSING_SCRIPTS_README_MARKER\", marker))");
    try expectContains(validator_source, "print(\"BOOTSTRAP_VALIDATION=fail\")");
    try expectContains(validator_source, "print(f\"{code}_START\")");
    try expectContains(validator_source, "print(f\"{code}_END\")");
}

test "self-test fixture keeps scripts README validation live" {
    try expectContains(validator_source, "write_text(\n        root,\n        \"scripts/zigux/README.md\",");
    try expectContains(validator_source, "\"# scripts/zigux\",");
    try expectContains(validator_source, "\"- `scripts/zigux/check-zig-toolchain.py`\",");
    try expectContains(validator_source, "\"- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py`\",");
    try expectContains(validator_source, "BOOTSTRAP_VALIDATION_SELF_TEST=pass");
    try expectContains(validator_source, "BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT");
}

test "scripts README validation runs after docs marker collection and before workflow lines" {
    try expectOrder(
        validator_source,
        "for marker in FREEZE_MAP_MARKERS:",
        "for marker in SCRIPTS_README_MARKERS:",
    );
    try expectOrder(
        validator_source,
        "for marker in SCRIPTS_README_MARKERS:",
        "for marker in REQUIRED_WORKFLOW_LINES:",
    );
    try expectOrder(
        validator_source,
        "scripts_readme = read_text(root, \"scripts/zigux/README.md\")",
        "for marker in SCRIPTS_README_MARKERS:",
    );
}
