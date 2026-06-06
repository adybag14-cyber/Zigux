const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.TestUnexpectedResult;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.TestUnexpectedResult;
    try std.testing.expect(earlier_index < later_index);
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.TestUnexpectedResult;
    const tail_start = first + needle.len;
    try std.testing.expect(std.mem.indexOf(u8, haystack[tail_start..], needle) == null);
}

test "phase 2 cross policy keeps the required route roster ordered and unique" {
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json", 16 * 1024);
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_sha256\": {\n    \"x86_64-linux\":");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectOnce(policy, "\"phase2-cross\"");

    try expectBefore(policy, "\"phase2-toolchain\"", "\"phase2-tools\"");
    try expectBefore(policy, "\"phase2-tools\"", "\"phase2-kconfig\"");
    try expectBefore(policy, "\"phase2-kconfig\"", "\"phase2-cross\"");
    try expectBefore(policy, "\"phase2-cross\"", "\"phase2-genksyms\"");
    try expectBefore(policy, "\"phase2-genksyms\"", "\"phase2-fixdep\"");
    try expectBefore(policy, "\"phase2-fixdep\"", "\"phase2-validate\"");

    try expectNotContains(policy, "\"aarch64-linux\": \"");
    try expectNotContains(policy, "\"riscv64-linux\": \"");
}

test "phase 2 cross policy remains aligned with the committed cross-target fixture" {
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json", 16 * 1024);
    defer std.testing.allocator.free(policy);
    const fixture = try readRepoFile("zigux/tests/fixtures/phase2_cross_targets.json", 16 * 1024);
    defer std.testing.allocator.free(fixture);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectBefore(fixture, "\"target\": \"x86_64-linux\"", "\"target\": \"aarch64-linux\"");

    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectNotContains(fixture, "\"target\": \"riscv64-linux\"");
    try expectNotContains(fixture, "\"target\": \"aarch64-linux\",\n      \"review_status\": \"route contract only\",\n      \"validation_mode\": \"archive_required\"");
}

test "phase 2 cross alignment checker derives the route policy instead of carrying a private list" {
    const alignment_checker = try readRepoFile("scripts/zigux/check-phase2-cross-selftest-alignment.py", 128 * 1024);
    defer std.testing.allocator.free(alignment_checker);

    try expectContains(alignment_checker, "EXPECTED_REQUIRED_MAKE_ROUTES = (");
    try expectContains(alignment_checker, "\"phase2-toolchain\",");
    try expectContains(alignment_checker, "\"phase2-tools\",");
    try expectContains(alignment_checker, "\"phase2-kconfig\",");
    try expectContains(alignment_checker, "\"phase2-cross\",");
    try expectContains(alignment_checker, "\"phase2-genksyms\",");
    try expectContains(alignment_checker, "\"phase2-fixdep\",");
    try expectContains(alignment_checker, "\"phase2-validate\",");
    try expectContains(alignment_checker, "required_make_routes = upgrade_policy.get(\"required_make_routes\")");
    try expectContains(alignment_checker, "if required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):");
    try expectContains(alignment_checker, "\"invalid required_make_routes in required file:");
    try expectContains(alignment_checker, "load_expected_fixture(args.root.resolve())");
}

test "phase 2 direct checker keeps archive scope delegated to the shared policy" {
    const direct_checker = try readRepoFile("scripts/zigux/check-phase2-cross.py", 64 * 1024);
    defer std.testing.allocator.free(direct_checker);

    try expectContains(direct_checker, "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"");
    try expectContains(direct_checker, "def load_archive_target_scope(root: Path) -> list[str]:");
    try expectContains(direct_checker, "archive_target_scope = upgrade_policy.get(\"archive_target_scope\")");
    try expectContains(direct_checker, "fixture_scope = fixture.get(\"archive_target_scope\")");
    try expectContains(direct_checker, "ARCHIVE_SCOPE_MISMATCH");
    try expectContains(direct_checker, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
    try expectContains(direct_checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
}
