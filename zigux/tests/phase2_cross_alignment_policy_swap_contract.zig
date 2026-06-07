const std = @import("std");

const allocator = std.testing.allocator;

const alignment_checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

test "alignment checker keeps the supported cross-target swap boundary explicit" {
    const checker = try readRepoFile(alignment_checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(checker, "\"unsupported archive_target_scope targets\"");
    try expectContains(checker, "\"riscv64-linux\"");

    try expectContains(checker, "payload[\"upgrade_policy\"][\"archive_target_scope\"] = [\"aarch64-linux\"]");
    try expectContains(checker, "payload[\"archive_sha256\"] = {\"aarch64-linux\": \"3\" * 64}");
    try expectContains(checker, "fixture[\"archive_target_scope\"] = [\"aarch64-linux\"]");
    try expectContains(checker, "fixture[\"cross_targets\"][0][\"validation_mode\"] = \"route_contract_only\"");
    try expectContains(checker, "fixture[\"cross_targets\"][1][\"validation_mode\"] = \"archive_required\"");
    try expectContains(checker, "assert collect_issues(root) == []");

    try expectBefore(
        checker,
        "payload[\"upgrade_policy\"][\"archive_target_scope\"] = [\"aarch64-linux\"]",
        "payload[\"upgrade_policy\"][\"archive_target_scope\"] = [\"riscv64-linux\"]",
    );
}

test "alignment checker still fails closed on unmatched or unsupported policy swaps" {
    const checker = try readRepoFile(alignment_checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "assert (\"INVALID_CROSS_TARGET_FIXTURE_FIELD\", \"archive_target_scope\") in issues");
    try expectContains(checker, "assert any(code == \"INVALID_CROSS_TARGET_MATRIX\" for code, _ in issues)");
    try expectContains(checker, "assert \"unsupported archive_target_scope targets\" in str(exc)");
    try expectContains(checker, "raise AssertionError(\"unsupported policy target did not abort\")");

    try expectBefore(
        checker,
        "assert collect_issues(root) == []",
        "assert (\"INVALID_CROSS_TARGET_FIXTURE_FIELD\", \"archive_target_scope\") in issues",
    );
    try expectBefore(
        checker,
        "assert (\"INVALID_CROSS_TARGET_FIXTURE_FIELD\", \"archive_target_scope\") in issues",
        "payload[\"upgrade_policy\"][\"archive_target_scope\"] = [\"riscv64-linux\"]",
    );
}

test "current fixture and policy keep one archive-backed target plus one route-only target" {
    const policy = try readRepoFile(policy_path);
    defer allocator.free(policy);
    const fixture = try readRepoFile(fixture_path);
    defer allocator.free(fixture);

    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectContains(policy, "\"archive_sha256\": {\n    \"x86_64-linux\"");
    try expectNotContains(policy, "\"aarch64-linux\":");
    try expectNotContains(policy, "\"riscv64-linux\":");
    try expectContains(policy, "\"phase2-cross\"");

    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64");
    try expectNotContains(fixture, "-musl");
}

test "alignment success output remains tied to marker, archive-scope, and fixture counts" {
    const checker = try readRepoFile(alignment_checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT=pass");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT=");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=");

    try expectBefore(
        checker,
        "expected_fixture = load_expected_fixture(args.root.resolve())",
        "\"PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=\"",
    );
    try expectBefore(
        checker,
        "\"PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=\"",
        "\"PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=\"",
    );
}
