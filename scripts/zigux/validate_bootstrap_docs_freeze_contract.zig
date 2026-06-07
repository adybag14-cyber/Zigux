const std = @import("std");

const validator = @embedFile("validate-bootstrap.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "docs README marker tuple remains part of bootstrap validation" {
    try expectContains(validator, "DOCS_README_MARKERS = (");
    try expectContains(validator, "\"# Zigux Documentation This directory is the product documentation root for Zigux.\",");
    try expectContains(validator, "\"- review rules\",");
    try expectContains(validator, "\"- freeze map\",");
    try expectContains(validator, "issues.append((\"MISSING_DOCS_README_MARKER\", marker))");
}

test "freeze-map marker tuple keeps deep-core boundary anchors" {
    try expectContains(validator, "FREEZE_MAP_MARKERS = (");
    try expectContains(validator, "\"## Freeze In C Initially\",");
    try expectContains(validator, "\"- `kernel/sched/core.c`\",");
    try expectContains(validator, "\"## Study / Boundary Only\",");
    try expectContains(validator, "\"- `kernel/workqueue.c`\",");
    try expectContains(validator, "issues.append((\"MISSING_FREEZE_MAP_MARKER\", marker))");
}

test "docs and freeze marker checks happen before workflow line checks" {
    try expectOrdered(validator, "for marker in DOCS_README_MARKERS:", "for marker in FREEZE_MAP_MARKERS:");
    try expectOrdered(validator, "for marker in FREEZE_MAP_MARKERS:", "for marker in SCRIPTS_README_MARKERS:");
    try expectOrdered(validator, "for marker in SCRIPTS_README_MARKERS:", "for marker in REQUIRED_WORKFLOW_LINES:");
}

test "validator self-test fixture seeds the docs and freeze files" {
    try expectContains(validator, "write_text(\n        root,\n        \"Documentation/zigux/README.md\",");
    try expectContains(validator, "write_text(root, \"Documentation/zigux/review-checklist.md\", \"present\\n\")");
    try expectContains(validator, "write_text(\n        root,\n        \"Documentation/zigux/freeze-map.md\",");
    try expectOrdered(validator, "\"Documentation/zigux/README.md\"", "\"Documentation/zigux/freeze-map.md\"");
}
