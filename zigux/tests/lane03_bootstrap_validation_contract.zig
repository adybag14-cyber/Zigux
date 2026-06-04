const std = @import("std");

const toolchain_checker_path = "scripts/zigux/check-zig-toolchain.py";
const bootstrap_validator_path = "scripts/zigux/validate-bootstrap.py";
const toolchain_policy_path = "scripts/zigux/zig-toolchain-policy.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactLineCount(haystack: []const u8, needle: []const u8, expected_count: usize) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(expected_count, count);
}

test "toolchain checker keeps policy and archive-only public entrypoints" {
    const checker = try readRepoFile(std.testing.allocator, toolchain_checker_path);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "parser.add_argument(\"--policy-only\"");
    try expectContains(checker, "parser.add_argument(\"--archive-only\"");
    try expectContains(checker, "parser.add_argument(\"--archive\"");
    try expectContains(checker, "parser.add_argument(\"--archive-target\"");
    try expectContains(checker, "ZIG_TOOLCHAIN_POLICY_STATUS=present");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS");
    try expectContains(checker, "archive_name_has_duplicate_suffix");
    try expectContains(checker, "multiple repo-local pinned archive candidates matched");
}

test "pinned policy stays lockstep with the Phase 2 bootstrap route set" {
    const policy = try readRepoFile(std.testing.allocator, toolchain_policy_path);
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"required_make_routes\"");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-tools\"");
    try expectContains(policy, "\"phase2-kconfig\"");
    try expectContains(policy, "\"phase2-cross\"");
    try expectContains(policy, "\"phase2-genksyms\"");
    try expectContains(policy, "\"phase2-fixdep\"");
    try expectContains(policy, "\"phase2-validate\"");
}

test "bootstrap validator requires the Lane 03 workflow commands exactly once" {
    const validator = try readRepoFile(std.testing.allocator, bootstrap_validator_path);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "REQUIRED_WORKFLOW_LINES");
    try expectExactLineCount(
        validator,
        "\"run: python3 scripts/zigux/check-zig-toolchain.py --self-test\",",
        1,
    );
    try expectExactLineCount(
        validator,
        "\"run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\",",
        1,
    );
    try expectExactLineCount(
        validator,
        "\"run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\",",
        1,
    );
    try expectContains(validator, "DUPLICATE_WORKFLOW_LINE");
    try expectContains(validator, "BOOTSTRAP_VALIDATION=pass");
}
