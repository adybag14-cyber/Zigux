const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "toolchain policy summary preserves status and pin fields" {
    const checker_source = try readRepoFile(std.testing.allocator, "scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker_source);
    const policy_json = try readRepoFile(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy_json);

    try expectContains(checker_source, "def emit_policy_summary(policy_path: Path = TOOLCHAIN_POLICY) -> None:");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_POLICY_STATUS=present");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_PINNED_CHANNEL={payload['channel']}");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_MIN_SUPPORTED={payload['minimum_version']}");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_PIN_POLICY=");

    try expectContains(policy_json, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy_json, "\"minimum_version\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy_json, "\"channel_minimum_lockstep\": true");
}

test "toolchain policy summary preserves archive target fields" {
    const checker_source = try readRepoFile(std.testing.allocator, "scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker_source);
    const policy_json = try readRepoFile(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy_json);

    try expectContains(checker_source, "ZIG_TOOLCHAIN_ARCHIVE_TARGET_COUNT={len(archive_sha256)}");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_ARCHIVE_TARGETS=");
    try expectContains(checker_source, "archive_target_scope");

    try expectContains(policy_json, "\"archive_sha256\"");
    try expectContains(policy_json, "\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"");
    try expectContains(policy_json, "\"archive_target_scope\"");
    try expectContains(policy_json, "\"x86_64-linux\"");
}

test "toolchain policy summary preserves required make route fields" {
    const checker_source = try readRepoFile(std.testing.allocator, "scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker_source);
    const policy_json = try readRepoFile(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy_json);

    try expectContains(checker_source, "ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=");
    try expectContains(checker_source, "required_make_routes");

    try expectContains(policy_json, "\"phase2-toolchain\"");
    try expectContains(policy_json, "\"phase2-tools\"");
    try expectContains(policy_json, "\"phase2-kconfig\"");
    try expectContains(policy_json, "\"phase2-cross\"");
    try expectContains(policy_json, "\"phase2-genksyms\"");
    try expectContains(policy_json, "\"phase2-fixdep\"");
    try expectContains(policy_json, "\"phase2-validate\"");
}
