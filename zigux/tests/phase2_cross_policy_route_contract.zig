const std = @import("std");

const route = "make -C zigux phase2-cross";
const archive_target = "x86_64-linux";
const route_only_target = "aarch64-linux";

const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";
const makefile_path = "zigux/Makefile";
const direct_checker_path = "scripts/zigux/check-phase2-cross.py";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

fn expectOrderedAfter(
    haystack: []const u8,
    after: []const u8,
    first: []const u8,
    second: []const u8,
) !void {
    const base_index = std.mem.indexOf(u8, haystack, after) orelse return error.AnchorMarkerMissing;
    const first_index = std.mem.indexOfPos(u8, haystack, base_index, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOfPos(u8, haystack, first_index + first.len, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

test "policy keeps phase2 cross route tied to the archive target scope" {
    const policy = try readRepoFile(std.testing.allocator, policy_path);
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy, "\"archive_sha256\": {");
    try expectContains(policy, "\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectOnce(policy, "\"phase2-cross\"");
    try expectOrdered(policy, "\"phase2-kconfig\"", "\"phase2-cross\"");
    try expectOrdered(policy, "\"phase2-cross\"", "\"phase2-genksyms\"");
}

test "cross fixture mirrors policy archive and route-only target split" {
    const fixture = try readRepoFile(std.testing.allocator, fixture_path);
    defer std.testing.allocator.free(fixture);

    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"review_status\": \"route contract only\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");
    try std.testing.expectEqual(@as(usize, 3), countOccurrences(fixture, route));
}

test "make route runs direct checker before alignment checker" {
    const makefile = try readRepoFile(std.testing.allocator, makefile_path);
    defer std.testing.allocator.free(makefile);

    const route_anchor = "phase2-cross:\n";
    try expectContains(makefile, "phase2-cross:\n");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py\n");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py\n");
    try expectOrderedAfter(makefile, route_anchor, "check-phase2-cross.py --self-test", "check-phase2-cross.py\n");
    try expectOrderedAfter(makefile, route_anchor, "check-phase2-cross.py\n", "check-phase2-cross-selftest-alignment.py --self-test");
    try expectOrderedAfter(makefile, route_anchor, "check-phase2-cross-selftest-alignment.py --self-test", "check-phase2-cross-selftest-alignment.py\n");
}

test "direct checker still emits policy-backed route diagnostics" {
    const direct_checker = try readRepoFile(std.testing.allocator, direct_checker_path);
    defer std.testing.allocator.free(direct_checker);

    try expectContains(direct_checker, "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"");
    try expectContains(direct_checker, "FIXTURE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase2_cross_targets.json\"");
    try expectContains(direct_checker, "ROUTE = \"make -C zigux phase2-cross\"");
    try expectContains(direct_checker, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
    try expectContains(direct_checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(direct_checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try expectContains(direct_checker, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(direct_checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT");
    try expectContains(direct_checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT");
    try expectContains(direct_checker, "ARCHIVE_SCOPE_MISMATCH");
    try expectContains(direct_checker, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
    try expectContains(direct_checker, "INVALID_CROSS_TARGET_ROUTE");
    try expectContains(direct_checker, "INVALID_CROSS_TARGET_MODE");
    try expectContains(direct_checker, "DUPLICATE_CROSS_TARGET");
}

test "policy and fixture keep the same archive-backed target" {
    const policy = try readRepoFile(std.testing.allocator, policy_path);
    defer std.testing.allocator.free(policy);
    const fixture = try readRepoFile(std.testing.allocator, fixture_path);
    defer std.testing.allocator.free(fixture);

    try expectContains(policy, archive_target);
    try expectContains(fixture, archive_target);
    try expectContains(fixture, route_only_target);
    try expectNotContains(policy, route_only_target ++ "\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77");
}
