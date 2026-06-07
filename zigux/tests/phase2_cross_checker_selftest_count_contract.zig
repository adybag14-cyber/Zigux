const std = @import("std");
const testing = std.testing;

const checker_path = "scripts/zigux/check-phase2-cross.py";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase2 cross checker pins explicit self-test case count" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker, "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT={checks_run}");
}

test "phase2 cross checker self-test keeps current 17-case accounting surface" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "assert collect_issues(root) == []");
    try expectContains(checker, "(\"MISSING_MAKEFILE_LINE\", marker)");
    try expectContains(checker, "(\"DUPLICATE_MAKEFILE_LINE\", f\"{marker}:count=2\")");
    try expectContains(checker, "(\"ARCHIVE_SCOPE_MISMATCH\", \"x86_64-linux\")");
    try expectContains(checker, "(\"ARCHIVE_REQUIRED_TARGET_SET_MISMATCH\", \"\")");
    try expectContains(checker, "(\"DUPLICATE_CROSS_TARGET\", \"x86_64-linux\")");
    try expectContains(checker, "(\"INVALID_CROSS_TARGET_ROUTE\", \"aarch64-linux\")");
    try expectContains(checker, "(\"INVALID_CROSS_TARGET_ENTRY\", \"aarch64-linux:review_status\")");
    try expectContains(checker, "(\"INVALID_CROSS_TARGET_MODE\", \"aarch64-linux\")");
    try expectContains(checker, "duplicate archive_target_scope entry");
    try expectContains(checker, "for primary_path in (TOOLCHAIN_POLICY, MAKEFILE, FIXTURE):");
    try expectContains(checker, "required file missing");
}

test "phase2 cross checker self-test still exercises all makefile markers both ways" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "MAKEFILE_LINES = (");
    try expectContains(checker, "\"phase2-cross:\"");
    try expectContains(checker, "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py\"");
    try expectContains(checker, "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py\"");
    try expectContains(checker, "path.write_text(replace_exact_line(path.read_text(encoding=\"utf-8\"), marker, \"# removed\"), encoding=\"utf-8\")");
    try expectContains(checker, "path.write_text(duplicate_exact_line(path.read_text(encoding=\"utf-8\"), marker), encoding=\"utf-8\")");
}

test "phase2 cross fixture remains the two-target count boundary reported by checker" {
    const allocator = testing.allocator;
    const fixture = try readRepoFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectContains(fixture, "\"archive_target_scope\"");
    try expectNotContains(fixture, "riscv64-linux");
}
