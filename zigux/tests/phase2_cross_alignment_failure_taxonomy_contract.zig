const std = @import("std");

const checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |offset| {
        count += 1;
        cursor += offset + needle.len;
    }
    return count;
}

test "alignment checker keeps stable failure taxonomy names" {
    const checker = try readFile(std.testing.allocator, checker_path);
    defer std.testing.allocator.free(checker);

    const failure_codes = [_][]const u8{
        "MISSING_DOCS_ROOT_README_MARKERS",
        "MISSING_PHASE2_NOTES_MARKERS",
        "MISSING_REVIEW_CHECKLIST_MARKERS",
        "MISSING_TESTS_README_MARKERS",
        "MISSING_SCRIPTS_README_MARKERS",
        "MISSING_MAKEFILE_LINES",
        "DUPLICATE_MAKEFILE_LINES",
        "MISSING_TOOLCHAIN_PINNING_MARKERS",
        "MISSING_TESTS_ALIGNMENT_MARKERS",
        "INVALID_CROSS_TARGET_FIXTURE",
        "INVALID_CROSS_TARGET_FIXTURE_FIELD",
        "INVALID_CROSS_TARGET_ENTRY",
        "INVALID_CROSS_TARGET_ROUTE",
        "DUPLICATE_CROSS_TARGET_ENTRY",
        "INVALID_CROSS_TARGET_MATRIX",
    };

    for (failure_codes) |code| {
        try expectContains(checker, code);
    }
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT=fail");
    try expectContains(checker, "print(f\"{code}_START\")");
    try expectContains(checker, "print(f\"{code}_END\")");
}

test "alignment checker keeps grouped fail envelope and issue order" {
    const checker = try readFile(std.testing.allocator, checker_path);
    defer std.testing.allocator.free(checker);

    try expectOrder(checker, "print(\"PHASE2_CROSS_ALIGNMENT=fail\")", "print(f\"{code}_START\")");
    try expectOrder(checker, "MISSING_DOCS_ROOT_README_MARKERS", "MISSING_PHASE2_NOTES_MARKERS");
    try expectOrder(checker, "MISSING_PHASE2_NOTES_MARKERS", "MISSING_REVIEW_CHECKLIST_MARKERS");
    try expectOrder(checker, "MISSING_REVIEW_CHECKLIST_MARKERS", "MISSING_TESTS_README_MARKERS");
    try expectOrder(checker, "MISSING_TESTS_README_MARKERS", "MISSING_SCRIPTS_README_MARKERS");
    try expectOrder(checker, "MISSING_MAKEFILE_LINES", "DUPLICATE_MAKEFILE_LINES");
    try expectOrder(checker, "INVALID_CROSS_TARGET_FIXTURE", "INVALID_CROSS_TARGET_FIXTURE_FIELD");
    try expectOrder(checker, "INVALID_CROSS_TARGET_FIXTURE_FIELD", "INVALID_CROSS_TARGET_ENTRY");
    try expectOrder(checker, "INVALID_CROSS_TARGET_ENTRY", "INVALID_CROSS_TARGET_ROUTE");
    try expectOrder(checker, "INVALID_CROSS_TARGET_ROUTE", "DUPLICATE_CROSS_TARGET_ENTRY");
    try expectOrder(checker, "DUPLICATE_CROSS_TARGET_ENTRY", "INVALID_CROSS_TARGET_MATRIX");
}

test "alignment checker keeps pass markers and self-test accounting visible" {
    const checker = try readFile(std.testing.allocator, checker_path);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "expected_case_count = (");
    try expectContains(checker, "+ 19");
    try expectContains(checker, "+ 10");
    try expectContains(checker, "assert checks_run == expected_case_count");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT=pass");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT=");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=");
}

test "alignment checker keeps supported target and required route guardrails" {
    const checker = try readFile(std.testing.allocator, checker_path);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(checker, "EXPECTED_REQUIRED_MAKE_ROUTES = (");
    try expectContains(checker, "\"phase2-cross\",");
    try expectContains(checker, "unsupported archive_target_scope targets");
    try expectContains(checker, "invalid required_make_routes");
    try expectContains(checker, "route_contract_only");
    try expectContains(checker, "archive_required");
}

test "alignment policy and fixture preserve x86 archive plus aarch64 route-only taxonomy" {
    const policy = try readFile(std.testing.allocator, policy_path);
    defer std.testing.allocator.free(policy);
    const fixture = try readFile(std.testing.allocator, fixture_path);
    defer std.testing.allocator.free(fixture);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"archive_sha256\": {\n    \"x86_64-linux\"");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectContains(policy, "\"phase2-cross\"");
    try expectNotContains(policy, "aarch64-linux");
    try expectNotContains(policy, "riscv64-linux");

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");
    try std.testing.expectEqual(@as(usize, 3), countOccurrences(fixture, "\"route\": \"make -C zigux phase2-cross\""));
}
