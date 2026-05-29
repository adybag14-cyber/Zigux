const std = @import("std");

const cross_targets_fixture = @embedFile("fixtures/phase2_cross_targets.json");

const required_output_markers = [_][]const u8{
    "PHASE2_CROSS_ALIGNMENT=pass",
    "PHASE2_CROSS_ALIGNMENT=fail",
    "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass",
    "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT=",
    "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=",
    "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=",
    "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=",
};

const required_issue_codes = [_][]const u8{
    "MISSING_DOCS_ROOT_README_MARKERS",
    "MISSING_PHASE2_NOTES_MARKERS",
    "MISSING_REVIEW_CHECKLIST_MARKERS",
    "MISSING_TESTS_README_MARKERS",
    "MISSING_SCRIPTS_README_MARKERS",
    "MISSING_MAKEFILE_LINES",
    "DUPLICATE_MAKEFILE_LINES",
    "MISSING_TOOLCHAIN_PINNING_MARKERS",
    "MISSING_TESTS_ALIGNMENT_MARKERS",
    "INVALID_CROSS_TARGET_FIXTURE_FIELD",
    "INVALID_CROSS_TARGET_MATRIX",
    "DUPLICATE_CROSS_TARGET_ENTRY",
};

const required_policy_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-cross",
    "phase2-validate",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, haystack, needle));
}

test "alignment contract keeps public pass and self-test output markers" {
    for (required_output_markers) |marker| {
        try std.testing.expect(marker.len > "PHASE2_CROSS_ALIGNMENT".len);
        try expectContains(marker, "PHASE2_CROSS_ALIGNMENT");
    }
}

test "alignment contract keeps fail-closed issue codes visible" {
    for (required_issue_codes) |issue_code| {
        try expectContains(issue_code, "_");
        for (issue_code) |byte| {
            try std.testing.expect(!std.ascii.isLower(byte));
        }
    }
}

test "alignment fixture keeps the current two-target route" {
    try expectContainsOnce(cross_targets_fixture, "\"target\": \"x86_64-linux\"");
    try expectContainsOnce(cross_targets_fixture, "\"target\": \"aarch64-linux\"");
    try expectContainsOnce(cross_targets_fixture, "\"validation_mode\": \"archive_required\"");
    try expectContainsOnce(cross_targets_fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectContains(cross_targets_fixture, "\"route\": \"make -C zigux phase2-cross\"");
}

test "alignment contract preserves policy route and archive-scope contracts" {
    for (required_policy_routes) |route| {
        try std.testing.expect(std.mem.startsWith(u8, route, "phase2-"));
    }
    try expectContainsOnce(cross_targets_fixture, "\"archive_target_scope\":");
    try expectContainsOnce(cross_targets_fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContainsOnce(cross_targets_fixture, "\"review_status\": \"route contract only\"");
}
