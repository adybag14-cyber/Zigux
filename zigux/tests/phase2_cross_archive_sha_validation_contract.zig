const std = @import("std");
const testing = std.testing;

const max_file_size = 512 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "direct cross checker validates scoped archive sha256 values" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-cross.py");
    defer allocator.free(checker);

    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 21");
    try expectContains(checker, "def is_sha256_hex(value: object) -> bool:");
    try expectContains(checker, "isinstance(value, str)");
    try expectContains(checker, "len(value) == 64");
    try expectContains(checker, "all(char in \"0123456789abcdefABCDEF\" for char in value)");
    try expectContains(checker, "archive_sha256 = payload.get(\"archive_sha256\")");
    try expectContains(checker, "if not isinstance(archive_sha256, dict):");
    try expectContains(checker, "if not is_sha256_hex(archive_sha256.get(target)):");
    try expectContains(checker, "raise SystemExit(f\"invalid archive_sha256 for {target} in required file: {policy_path}\")");
    try expectBefore(checker, "archive_sha256 = payload.get(\"archive_sha256\")", "normalized: list[str] = []");
    try expectBefore(checker, "target = value.strip()", "if not is_sha256_hex(archive_sha256.get(target)):");
}

test "checker self-test covers missing short non-hex and extra scoped archive hashes" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-cross.py");
    defer allocator.free(checker);

    try expectContains(checker, "policy[\"archive_sha256\"] = {}");
    try expectContains(checker, "raise AssertionError(\"missing archive_sha256 target did not abort\")");
    try expectContains(checker, "policy[\"archive_sha256\"][\"x86_64-linux\"] = \"3\" * 63");
    try expectContains(checker, "raise AssertionError(\"short archive_sha256 did not abort\")");
    try expectContains(checker, "policy[\"archive_sha256\"][\"x86_64-linux\"] = \"g\" * 64");
    try expectContains(checker, "raise AssertionError(\"non-hex archive_sha256 did not abort\")");
    try expectContains(checker, "policy[\"archive_sha256\"][\"aarch64-linux\"] = \"4\" * 64");
    try expectContains(checker, "archive_sha256 targets outside archive_target_scope");
    try expectContains(checker, "raise AssertionError(\"extra archive_sha256 target did not abort\")");
    try testing.expectEqual(@as(usize, 3), countOccurrences(checker, "invalid archive_sha256 for x86_64-linux"));
    try expectContains(checker, "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT={checks_run}");
}

test "policy and fixture keep the current single archive-backed target boundary" {
    const allocator = testing.allocator;
    const policy = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);
    const fixture = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_cross_targets.json");
    defer allocator.free(fixture);

    try expectContains(policy,
        \\"archive_sha256": {
        \\
    );
    try expectContains(policy,
        \\"x86_64-linux": "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6"
        \\
    );
    try expectContains(policy,
        \\"archive_target_scope": [
        \\      "x86_64-linux"
        \\    ]
    );
    try testing.expectEqual(@as(usize, 2), countOccurrences(policy, "\"x86_64-linux\""));
    try testing.expectEqual(@as(usize, 0), countOccurrences(policy, "\"aarch64-linux\""));
    try testing.expectEqual(@as(usize, 0), countOccurrences(policy, "\"riscv64-linux\""));

    try expectContains(fixture,
        \\"target": "x86_64-linux",
        \\      "review_status": "pinned bootstrap archive",
        \\      "validation_mode": "archive_required"
    );
    try expectContains(fixture,
        \\"target": "aarch64-linux",
        \\      "review_status": "route contract only",
        \\      "validation_mode": "route_contract_only"
    );
    try testing.expectEqual(@as(usize, 2), countOccurrences(fixture, "\"target\""));
    try testing.expectEqual(@as(usize, 1), countOccurrences(fixture, "\"validation_mode\": \"archive_required\""));
    try expectNotContains(fixture, "archive_sha256");
}

test "direct checker still emits archive scope count from the validated policy" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-cross.py");
    defer allocator.free(checker);

    try expectContains(checker, "print(\"PHASE2_DIRECT_CROSS_ROUTE=pass\")");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}");
    try expectContains(checker, "\"archive_sha256\": {\"x86_64-linux\": \"3\" * 64}");
    try expectContains(checker, "\"archive_target_scope\": [\"x86_64-linux\"]");
    try expectBefore(checker, "issues = collect_issues(args.root.resolve())", "print(\"PHASE2_DIRECT_CROSS_ROUTE=pass\")");
}

test "direct checker rejects stale archive hash targets outside archive scope" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-cross.py");
    defer allocator.free(checker);

    try expectContains(checker, "extra_hash_targets = sorted(str(target) for target in archive_sha256.keys() if target not in seen_targets)");
    try expectContains(checker, "if extra_hash_targets:");
    try expectContains(checker, "archive_sha256 targets outside archive_target_scope in required file");
    try expectContains(checker, "f\"{policy_path}: {', '.join(extra_hash_targets)}\"");
    try expectBefore(checker, "extra_hash_targets = sorted", "return normalized");
}
