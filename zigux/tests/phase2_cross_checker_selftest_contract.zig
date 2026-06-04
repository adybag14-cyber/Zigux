const std = @import("std");

const direct_checker_packet =
    \\EXPECTED_SELF_TEST_CASE_COUNT = 17
    \\PHASE2_DIRECT_CROSS_ROUTE=pass
    \\PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT
    \\PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT
    \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass
    \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT
    \\MISSING_MAKEFILE_LINE
    \\DUPLICATE_MAKEFILE_LINE
    \\INVALID_FIXTURE_FIELD
    \\ARCHIVE_SCOPE_MISMATCH
    \\INVALID_CROSS_TARGET_ROUTE
    \\INVALID_CROSS_TARGET_MODE
    \\ARCHIVE_REQUIRED_TARGET_SET_MISMATCH
    \\DUPLICATE_CROSS_TARGET
    \\INVALID_CROSS_TARGET_ENTRY
;

const current_fixture_packet =
    \\Phase 2
    \\active
    \\make -C zigux phase2-cross
    \\x86_64-linux
    \\pinned bootstrap archive
    \\archive_required
    \\aarch64-linux
    \\route contract only
    \\route_contract_only
;

const alignment_checker_packet =
    \\SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")
    \\PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass
    \\PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT
    \\MISSING_MAKEFILE_LINE
    \\DUPLICATE_MAKEFILE_LINE
    \\INVALID_CROSS_TARGET_MATRIX
    \\INVALID_CROSS_TARGET_FIXTURE_FIELD
;

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(haystack, needle));
}

test "direct checker self-test count stays pinned" {
    try expectContains(direct_checker_packet, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(direct_checker_packet, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try expectContains(direct_checker_packet, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT");
}

test "direct checker pass output keeps matrix summary markers" {
    try expectContains(direct_checker_packet, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(direct_checker_packet, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT");
    try expectContains(direct_checker_packet, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT");
}

test "direct checker self-test covers route and fixture failure families" {
    const issue_markers = [_][]const u8{
        "MISSING_MAKEFILE_LINE",
        "DUPLICATE_MAKEFILE_LINE",
        "INVALID_FIXTURE_FIELD",
        "ARCHIVE_SCOPE_MISMATCH",
        "INVALID_CROSS_TARGET_ROUTE",
        "INVALID_CROSS_TARGET_MODE",
        "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH",
        "DUPLICATE_CROSS_TARGET",
        "INVALID_CROSS_TARGET_ENTRY",
    };

    for (issue_markers) |marker| {
        try expectContains(direct_checker_packet, marker);
    }
}

test "current fixture terms stay aligned with checker self-test root" {
    const fixture_terms = [_][]const u8{
        "Phase 2",
        "active",
        "make -C zigux phase2-cross",
        "x86_64-linux",
        "pinned bootstrap archive",
        "archive_required",
        "aarch64-linux",
        "route contract only",
        "route_contract_only",
    };

    for (fixture_terms) |term| {
        try expectContains(current_fixture_packet, term);
    }
}

test "alignment checker still names the same self-test summary and target set" {
    try expectContains(alignment_checker_packet, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(alignment_checker_packet, "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");
    try expectContains(alignment_checker_packet, "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT");
    try expectContains(alignment_checker_packet, "INVALID_CROSS_TARGET_MATRIX");
}
