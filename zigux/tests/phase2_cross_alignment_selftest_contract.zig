const std = @import("std");

const alignment_checker_paths = [_][]const u8{
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "../../scripts/zigux/check-phase2-cross-selftest-alignment.py",
};

const fixture_paths = [_][]const u8{
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "fixtures/phase2_cross_targets.json",
};

fn readFirstExisting(allocator: std.mem.Allocator, paths: []const []const u8) ![]u8 {
    for (paths) |path| {
        if (std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            path,
            allocator,
            .limited(1024 * 1024),
        )) |content| {
            return content;
        } else |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        }
    }
    return error.FileNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "alignment self-test accounting stays explicit" {
    const text = try readFirstExisting(std.testing.allocator, &alignment_checker_paths);
    defer std.testing.allocator.free(text);

    try expectContains(text, "def run_self_test() -> int:");
    try expectContains(text, "expected_case_count = (");
    try expectContains(text, "assert checks_run == expected_case_count");
    try expectContains(text, "print(\"PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass\")");
    try expectContains(text, "print(f\"PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}\")");
    try expectContains(text, "with tempfile.TemporaryDirectory(prefix=\"zigux_phase2_cross_alignment_\")");
    try expectOrdered(text, "assert checks_run == expected_case_count", "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");
}

test "alignment self-test case count formula covers every marker family" {
    const text = try readFirstExisting(std.testing.allocator, &alignment_checker_paths);
    defer std.testing.allocator.free(text);

    const formula_terms = [_][]const u8{
        "len(DOCS_ROOT_README_MARKERS)",
        "len(PHASE2_NOTES_MARKERS)",
        "len(REVIEW_CHECKLIST_MARKERS)",
        "len(TESTS_README_MARKERS)",
        "len(SCRIPTS_README_MARKERS)",
        "len(MAKEFILE_LINES)",
        "len(TOOLCHAIN_PINNING_MARKERS)",
        "len(TESTS_ALIGNMENT_MARKERS)",
        "+ 19",
        "+ 10",
    };

    try expectContains(text, "expected_case_count = (");
    for (formula_terms) |term| {
        try expectContains(text, term);
    }
    try expectOrdered(text, "expected_case_count = (", "+ 19");
    try expectOrdered(text, "+ 19", "+ 10");
    try expectOrdered(text, "+ 10", "with tempfile.TemporaryDirectory");
}

test "alignment pass and failure marker envelope remains machine-readable" {
    const text = try readFirstExisting(std.testing.allocator, &alignment_checker_paths);
    defer std.testing.allocator.free(text);

    try expectContains(text, "print(\"PHASE2_CROSS_ALIGNMENT=fail\")");
    try expectContains(text, "print(f\"{code}_START\")");
    try expectContains(text, "print(f\"{code}_END\")");
    try expectContains(text, "print(\"PHASE2_CROSS_ALIGNMENT=pass\")");
    try expectContains(text, "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT=");
    try expectContains(text, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=");
    try expectContains(text, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=");
    try expectOrdered(text, "issues = collect_issues(args.root.resolve())", "print(\"PHASE2_CROSS_ALIGNMENT=pass\")");
}

test "alignment issue vocabulary covers route, docs, policy, and fixture drift" {
    const text = try readFirstExisting(std.testing.allocator, &alignment_checker_paths);
    defer std.testing.allocator.free(text);

    const issue_codes = [_][]const u8{
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
        "INVALID_CROSS_TARGET_ENTRY",
        "INVALID_CROSS_TARGET_ROUTE",
        "INVALID_CROSS_TARGET_MATRIX",
        "DUPLICATE_CROSS_TARGET_ENTRY",
    };

    for (issue_codes) |code| {
        try expectContains(text, code);
    }
}

test "alignment checker and fixture keep current two-target route vocabulary" {
    const checker = try readFirstExisting(std.testing.allocator, &alignment_checker_paths);
    defer std.testing.allocator.free(checker);
    const fixture = try readFirstExisting(std.testing.allocator, &fixture_paths);
    defer std.testing.allocator.free(fixture);

    try expectContains(checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(checker, "ROUTE = \"make -C zigux phase2-cross\"");
    try expectContains(checker, "\"archive_required\" if target in seen_scope else \"route_contract_only\"");
    try expectContains(checker, "\"unsupported archive_target_scope targets in required file: \"");

    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectNotContains(fixture, "\"target\": \"riscv64-linux\"");
}
