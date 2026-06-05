const std = @import("std");

const checker_path = "scripts/zigux/check-phase2-cross.py";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative_index| {
        count += 1;
        offset += relative_index + needle.len;
    }
    return count;
}

test "direct checker constants keep the current Phase 2 route packet narrow" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "ROUTE = \"make -C zigux phase2-cross\"");
    try expectContains(checker, "EXPECTED_FIXTURE_PHASE = \"Phase 2\"");
    try expectContains(checker, "EXPECTED_FIXTURE_STATUS = \"active\"");
    try expectContains(checker, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");

    try expectContains(checker, "\"phase2-cross:\"");
    try expectContains(checker, "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py\"");
    try expectContains(checker, "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py\"");

    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=");
}

test "direct checker still binds archive scope to validation modes" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "if fixture_scope != archive_target_scope:");
    try expectContains(checker, "issues.append((\"ARCHIVE_SCOPE_MISMATCH\", \",\".join(archive_target_scope)))");
    try expectContains(checker, "if validation_mode == \"archive_required\":");
    try expectContains(checker, "archive_required_targets.add(target)");
    try expectContains(checker, "if archive_required_targets != set(archive_target_scope):");
    try expectContains(checker, "issues.append((\"ARCHIVE_REQUIRED_TARGET_SET_MISMATCH\", \",\".join(sorted(archive_required_targets))))");
}

test "cross target fixture keeps the two-target Phase 2 boundary" {
    const allocator = std.testing.allocator;
    const fixture = try readFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"review_status\": \"route contract only\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectAbsent(fixture, "riscv64-linux");
    try std.testing.expectEqual(@as(usize, 2), countOccurrences(fixture, "\"target\": "));
}
