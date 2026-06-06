const std = @import("std");

const fixture = @embedFile("fixtures/phase2_cross_targets.json");
const direct_checker_path = "scripts/zigux/check-phase2-cross.py";
const alignment_checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    ForbiddenMarkerPresent,
};

fn count(haystack: []const u8, needle: []const u8) usize {
    return std.mem.count(u8, haystack, needle);
}

fn requireContains(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) == null) return ContractError.MissingMarker;
}

fn requireOnce(text: []const u8, marker: []const u8) !void {
    const matches = count(text, marker);
    if (matches == 0) return ContractError.MissingMarker;
    if (matches != 1) return ContractError.DuplicateMarker;
}

fn requireCount(text: []const u8, marker: []const u8, expected: usize) !void {
    const matches = count(text, marker);
    if (matches == 0) return ContractError.MissingMarker;
    if (matches != expected) return ContractError.DuplicateMarker;
}

fn requireAbsent(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) != null) return ContractError.ForbiddenMarkerPresent;
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024)) catch |err| switch (err) {
        error.FileNotFound => blk: {
            const fallback = try std.mem.concat(allocator, u8, &.{ "../../", path });
            defer allocator.free(fallback);
            break :blk try std.Io.Dir.cwd().readFileAlloc(std.testing.io, fallback, allocator, .limited(1024 * 1024));
        },
        else => return err,
    };
}

fn validateFixtureBoundary(text: []const u8) !void {
    try requireContains(text, "\"phase\": \"Phase 2\"");
    try requireContains(text, "\"status\": \"active\"");
    try requireContains(text, "\"route\": \"make -C zigux phase2-cross\"");
    try requireContains(text, "\"archive_target_scope\": [");
    try requireOnce(text, "\"target\": \"x86_64-linux\"");
    try requireOnce(text, "\"target\": \"aarch64-linux\"");
    try requireOnce(text, "\"validation_mode\": \"archive_required\"");
    try requireOnce(text, "\"validation_mode\": \"route_contract_only\"");
    try requireOnce(text, "\"review_status\": \"pinned bootstrap archive\"");
    try requireOnce(text, "\"review_status\": \"route contract only\"");
    try requireAbsent(text, "\"target\": \"riscv64-linux\"");
}

fn validatePolicyBoundary(text: []const u8) !void {
    try requireContains(text, "\"phase\": \"Phase 2\"");
    try requireContains(text, "\"archive_sha256\": {");
    try requireContains(text, "\"archive_target_scope\": [");
    try requireOnce(text, "\"phase2-cross\"");
    try requireCount(text, "\"x86_64-linux\"", 2);
    try requireAbsent(text, "\"aarch64-linux\"");
    try requireAbsent(text, "\"riscv64-linux\"");
}

fn validateDirectChecker(text: []const u8) !void {
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE=fail");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
    try requireContains(text, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try requireContains(text, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
    try requireContains(text, "\"archive_target_scope\": [\"x86_64-linux\"]");
    try requireContains(text, "\"target\": \"aarch64-linux\"");
    try requireContains(text, "\"validation_mode\": \"route_contract_only\"");
    try requireContains(text, "(\"ARCHIVE_SCOPE_MISMATCH\", \",\".join(archive_target_scope))");
    try requireContains(text, "(\"ARCHIVE_REQUIRED_TARGET_SET_MISMATCH\", \",\".join(sorted(archive_required_targets)))");
    try requireContains(text, "(\"DUPLICATE_CROSS_TARGET\", target)");
    try requireContains(text, "(\"INVALID_CROSS_TARGET_ROUTE\", target)");
    try requireContains(text, "(\"INVALID_CROSS_TARGET_MODE\", target)");
}

fn validateAlignmentChecker(text: []const u8) !void {
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT=pass");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT=fail");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT=");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=");
    try requireContains(text, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try requireContains(text, "ROUTE = \"make -C zigux phase2-cross\"");
    try requireContains(text, "\"archive_required\" if target in seen_scope else \"route_contract_only\"");
    try requireContains(text, "\"unsupported archive_target_scope targets in required file: \"");
    try requireContains(text, "(\"INVALID_CROSS_TARGET_FIXTURE_FIELD\", \"archive_target_scope\")");
    try requireContains(text, "(\"INVALID_CROSS_TARGET_MATRIX\", json.dumps(actual_modes, sort_keys=True))");
    try requireContains(text, "(\"DUPLICATE_CROSS_TARGET_ENTRY\", target)");
    try requireContains(text, "(\"INVALID_CROSS_TARGET_ROUTE\", target)");
}

test "fixture and policy keep one archive-backed target and one route-only target" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);

    try validateFixtureBoundary(fixture);
    try validatePolicyBoundary(policy);
}

test "direct and alignment checkers expose synchronized count output vocabulary" {
    const allocator = std.testing.allocator;
    const direct = try readRepoFile(allocator, direct_checker_path);
    defer allocator.free(direct);
    const alignment = try readRepoFile(allocator, alignment_checker_path);
    defer allocator.free(alignment);

    try validateDirectChecker(direct);
    try validateAlignmentChecker(alignment);
}

test "contract catches fixture and policy matrix drift" {
    const promoted_aarch64_fixture =
        \\"phase": "Phase 2",
        \\"status": "active",
        \\"route": "make -C zigux phase2-cross",
        \\"archive_target_scope": [
        \\  "x86_64-linux"
        \\],
        \\"cross_targets": [
        \\  {
        \\    "target": "x86_64-linux",
        \\    "review_status": "pinned bootstrap archive",
        \\    "validation_mode": "archive_required",
        \\    "route": "make -C zigux phase2-cross"
        \\  },
        \\  {
        \\    "target": "aarch64-linux",
        \\    "review_status": "route contract only",
        \\    "validation_mode": "archive_required",
        \\    "route": "make -C zigux phase2-cross"
        \\  }
        \\]
    ;
    try std.testing.expectError(ContractError.DuplicateMarker, validateFixtureBoundary(promoted_aarch64_fixture));

    const widened_policy =
        \\"phase": "Phase 2",
        \\"archive_sha256": {
        \\  "x86_64-linux": "0",
        \\  "aarch64-linux": "1"
        \\},
        \\"upgrade_policy": {
        \\  "archive_target_scope": [
        \\    "x86_64-linux",
        \\    "aarch64-linux"
        \\  ],
        \\  "required_make_routes": [
        \\    "phase2-cross"
        \\  ]
        \\}
    ;
    try std.testing.expectError(ContractError.ForbiddenMarkerPresent, validatePolicyBoundary(widened_policy));
}

test "contract catches checker output and mutation coverage drift" {
    const direct_missing_count = "PHASE2_DIRECT_CROSS_ROUTE=pass\nEXPECTED_SELF_TEST_CASE_COUNT = 17\n";
    try std.testing.expectError(ContractError.MissingMarker, validateDirectChecker(direct_missing_count));

    const alignment_missing_matrix = "PHASE2_CROSS_ALIGNMENT=pass\nSUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")\n";
    try std.testing.expectError(ContractError.MissingMarker, validateAlignmentChecker(alignment_missing_matrix));
}
