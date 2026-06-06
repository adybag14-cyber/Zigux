const std = @import("std");
const testing = std.testing;

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, testing.allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectInOrder(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOf(u8, haystack[cursor..], marker) orelse return error.MissingExpectedMarker;
        cursor += found + marker.len;
    }
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var cursor: usize = 0;
    var count: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |found| {
        count += 1;
        cursor += found + needle.len;
    }
    try testing.expectEqual(expected, count);
}

test "phase2 closure note keeps direct cross target packet parked in shared tooling" {
    const closure = try readFile("Documentation/zigux/phase2-closure.md");
    defer testing.allocator.free(closure);

    try expectInOrder(closure, &.{
        "## Current Shared Repo-Tooling Evidence",
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "PHASE2_SHARED_TOOLING_CHECKERS=",
        "python3 scripts/zigux/check-phase2-cross.py",
        "## Shared Replay Routes",
        "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2",
    });
    try expectContains(closure, "direct cross-route");
    try expectContains(closure, "fixdep governance/parity packet");
}

test "phase2 tool manifest and tests-root reminder agree on cross target surfaces" {
    const manifest = try readFile("zigux/tests/fixtures/phase2_tool_manifest.json");
    defer testing.allocator.free(manifest);
    const tests_readme = try readFile("zigux/tests/README.md");
    defer testing.allocator.free(tests_readme);

    try expectInOrder(manifest, &.{
        "\"cross_route_support\": [",
        "\"scripts/zigux/check-phase2-cross.py\"",
        "\"zigux/tests/fixtures/phase2_cross_targets.json\"",
    });
    try expectContains(manifest, "\"scripts/zigux/check-phase2-cross-selftest-alignment.py\"");
    try expectContains(manifest, "\"make -C zigux phase2-cross\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");

    try expectInOrder(tests_readme, &.{
        "## Phase 2 review packet",
        "`scripts/zigux/check-phase2-cross.py`",
        "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
        "`zigux/tests/fixtures/phase2_cross_targets.json`",
        "`make -C zigux phase2-cross`",
    });
    try expectContains(tests_readme, "direct cross-route");
    try expectContains(tests_readme, "cross-target fixture packet");
}

test "direct cross checker preserves the two target fixture contract vocabulary" {
    const checker = try readFile("scripts/zigux/check-phase2-cross.py");
    defer testing.allocator.free(checker);

    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
    try expectContains(checker, "ARCHIVE_SCOPE_MISMATCH");
    try expectContains(checker, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
    try expectContains(checker, "DUPLICATE_CROSS_TARGET");
    try expectContains(checker, "INVALID_CROSS_TARGET_ROUTE");
    try expectContains(checker, "INVALID_CROSS_TARGET_MODE");
}

test "phase2 cross fixture stays pinned to x86 archive plus aarch64 route contract" {
    const fixture = try readFile("zigux/tests/fixtures/phase2_cross_targets.json");
    defer testing.allocator.free(fixture);
    const policy = try readFile("scripts/zigux/zig-toolchain-policy.json");
    defer testing.allocator.free(policy);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectInOrder(fixture, &.{
        "\"archive_target_scope\": [",
        "\"x86_64-linux\"",
        "\"cross_targets\": [",
        "\"target\": \"x86_64-linux\"",
        "\"review_status\": \"pinned bootstrap archive\"",
        "\"validation_mode\": \"archive_required\"",
        "\"target\": \"aarch64-linux\"",
        "\"review_status\": \"route contract only\"",
        "\"validation_mode\": \"route_contract_only\"",
    });
    try expectExactCount(fixture, "\"target\":", 2);
    try expectNotContains(fixture, "\"target\": \"riscv64-linux\"");

    try expectInOrder(policy, &.{
        "\"archive_sha256\": {",
        "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"",
        "\"archive_target_scope\": [",
        "\"x86_64-linux\"",
    });
    try expectNotContains(policy, "\"aarch64-linux\": \"");
    try expectNotContains(policy, "\"riscv64-linux\"");
}
