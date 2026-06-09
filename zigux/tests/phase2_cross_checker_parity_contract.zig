const std = @import("std");

const direct_checker_path = "scripts/zigux/check-phase2-cross.py";
const alignment_checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

const route = "make -C zigux phase2-cross";
const x86_target = "x86_64-linux";
const aarch64_target = "aarch64-linux";
const archive_required = "archive_required";
const route_contract_only = "route_contract_only";

fn readFixture(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOfPos(u8, haystack, first_index + first.len, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(second_index > first_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

fn expectAtLeast(haystack: []const u8, needle: []const u8, minimum: usize) !void {
    try std.testing.expect(countOccurrences(haystack, needle) >= minimum);
}

test "direct cross checker keeps matrix failure vocabulary explicit" {
    const checker = try readFixture(direct_checker_path);
    defer std.testing.allocator.free(checker);

    const required_failure_labels = [_][]const u8{
        "MISSING_MAKEFILE_LINE",
        "DUPLICATE_MAKEFILE_LINE",
        "ARCHIVE_SCOPE_MISMATCH",
        "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH",
        "DUPLICATE_CROSS_TARGET",
        "INVALID_CROSS_TARGET_ROUTE",
        "INVALID_CROSS_TARGET_ENTRY",
        "INVALID_CROSS_TARGET_MODE",
        "PHASE2_DIRECT_CROSS_ROUTE=fail",
    };

    for (required_failure_labels) |label| {
        try expectContains(checker, label);
    }

    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=");
    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker, route);
    try expectContains(checker, x86_target);
    try expectContains(checker, aarch64_target);
    try expectContains(checker, archive_required);
    try expectContains(checker, route_contract_only);
    try expectOrdered(checker, "archive_required_targets.add(target)", "archive_required_targets != set(archive_target_scope)");
}

test "alignment checker models the same supported target modes" {
    const checker = try readFixture(alignment_checker_path);
    defer std.testing.allocator.free(checker);

    const shared_markers = [_][]const u8{
        "SUPPORTED_CROSS_TARGETS",
        x86_target,
        aarch64_target,
        route,
        archive_required,
        route_contract_only,
        "INVALID_CROSS_TARGET_MATRIX",
        "INVALID_CROSS_TARGET_ROUTE",
        "DUPLICATE_CROSS_TARGET_ENTRY",
        "unsupported archive_target_scope targets",
        "invalid required_make_routes",
        "PHASE2_CROSS_ALIGNMENT=fail",
        "PHASE2_CROSS_ALIGNMENT=pass",
        "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=",
    };

    for (shared_markers) |marker| {
        try expectContains(checker, marker);
    }

    try expectContains(checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(checker, "\"phase2-cross\",");
    try expectContains(checker, "target: (\"archive_required\" if target in seen_scope else \"route_contract_only\")");
    try expectOrdered(checker, "archive_target_scope", "expected_modes");
}

test "fixture keeps one archive-backed target and one route-only target" {
    const fixture = try readFixture(fixture_path);
    defer std.testing.allocator.free(fixture);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\"");
    try expectContains(fixture, "\"cross_targets\"");
    try expectAtLeast(fixture, route, 3);
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectOrdered(fixture, "\"target\": \"x86_64-linux\"", "\"validation_mode\": \"archive_required\"");
    try expectOrdered(fixture, "\"target\": \"aarch64-linux\"", "\"validation_mode\": \"route_contract_only\"");
}

test "cross checker surfaces stay disjoint from unsupported target expansion" {
    const direct_checker = try readFixture(direct_checker_path);
    defer std.testing.allocator.free(direct_checker);
    const alignment_checker = try readFixture(alignment_checker_path);
    defer std.testing.allocator.free(alignment_checker);
    const fixture = try readFixture(fixture_path);
    defer std.testing.allocator.free(fixture);

    try expectNotContains(fixture, "riscv64-linux");
    try expectNotContains(fixture, "powerpc64-linux");
    try expectNotContains(direct_checker, "riscv64-linux");
    try expectContains(alignment_checker, "unsupported archive_target_scope targets");
    try expectContains(alignment_checker, "riscv64-linux");
}
