const std = @import("std");
const testing = std.testing;

const max_file_size = 512 * 1024;

fn readRepoFile(path: []const u8) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, testing.allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
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

test "direct cross checker keeps stable output envelope and issue taxonomy" {
    const source = try readRepoFile("scripts/zigux/check-phase2-cross.py");
    defer testing.allocator.free(source);

    try expectContains(source, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(source, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try expectContains(source, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
    try expectContains(source, "PHASE2_DIRECT_CROSS_ROUTE=fail");
    try expectContains(source, "print(f\"{code}_START\")");
    try expectContains(source, "print(f\"{code}_END\")");

    try expectContains(source, "\"MISSING_MAKEFILE_LINE\"");
    try expectContains(source, "\"DUPLICATE_MAKEFILE_LINE\"");
    try expectContains(source, "\"INVALID_FIXTURE_SHAPE\"");
    try expectContains(source, "\"INVALID_FIXTURE_FIELD\"");
    try expectContains(source, "\"ARCHIVE_SCOPE_MISMATCH\"");
    try expectContains(source, "\"INVALID_CROSS_TARGET_ENTRY\"");
    try expectContains(source, "\"DUPLICATE_CROSS_TARGET\"");
    try expectContains(source, "\"INVALID_CROSS_TARGET_ROUTE\"");
    try expectContains(source, "\"INVALID_CROSS_TARGET_MODE\"");
    try expectContains(source, "\"ARCHIVE_REQUIRED_TARGET_SET_MISMATCH\"");
}

test "direct cross self-test count covers each guarded failure family" {
    const source = try readRepoFile("scripts/zigux/check-phase2-cross.py");
    defer testing.allocator.free(source);

    try expectContains(source, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(source, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try expectContains(source, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=");
    try expectContains(source, "assert collect_issues(root) == []");

    try expectContains(source, "fixture[\"archive_target_scope\"] = [\"aarch64-linux\"]");
    try expectContains(source, "fixture[\"cross_targets\"][0][\"validation_mode\"] = \"route_contract_only\"");
    try expectContains(source, "fixture[\"cross_targets\"].append(dict(fixture[\"cross_targets\"][0]))");
    try expectContains(source, "fixture[\"cross_targets\"][1][\"route\"] = \"make -C zigux phase2\"");
    try expectContains(source, "fixture[\"cross_targets\"][1][\"review_status\"] = \"\"");
    try expectContains(source, "fixture[\"cross_targets\"][1][\"validation_mode\"] = \"unexpected_mode\"");
    try expectContains(source, "policy[\"upgrade_policy\"][\"archive_target_scope\"] = [\"x86_64-linux\", \"x86_64-linux\"]");
}

test "direct cross fixture and policy preserve current two-target matrix boundary" {
    const fixture = try readRepoFile("zigux/tests/fixtures/phase2_cross_targets.json");
    defer testing.allocator.free(fixture);
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json");
    defer testing.allocator.free(policy);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\"");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "\"target\": \"riscv64-linux\"");
    try testing.expectEqual(@as(usize, 2), countOccurrences(fixture, "\"target\": "));

    try expectContains(policy, "\"archive_sha256\"");
    try expectContains(policy, "\"x86_64-linux\"");
    try expectNotContains(policy, "\"riscv64-linux\"");
    try expectContains(policy, "\"phase2-cross\"");
}

test "phase2-cross make route runs the direct checker before alignment" {
    const makefile = try readRepoFile("zigux/Makefile");
    defer testing.allocator.free(makefile);

    try expectOrdered(makefile, "phase2-cross:", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try expectOrdered(
        makefile,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    );
    try expectOrdered(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross", "phase2: phase2-validate");
}
