const std = @import("std");

const alignment_checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";
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

fn validateAlignmentCheckerPolicy(text: []const u8) !void {
    try requireContains(text, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try requireContains(text, "EXPECTED_REQUIRED_MAKE_ROUTES = (");
    try requireContains(text, "\"phase2-toolchain\"");
    try requireContains(text, "\"phase2-tools\"");
    try requireContains(text, "\"phase2-kconfig\"");
    try requireContains(text, "\"phase2-cross\"");
    try requireContains(text, "\"phase2-genksyms\"");
    try requireContains(text, "\"phase2-fixdep\"");
    try requireContains(text, "\"phase2-validate\"");
    try requireContains(text, "required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES)");
    try requireContains(text, "unsupported archive_target_scope targets");
    try requireContains(text, "\"archive_required\" if target in seen_scope else \"route_contract_only\"");
    try requireContains(text, "\"INVALID_CROSS_TARGET_MATRIX\"");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT=pass");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT=fail");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT=");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");
    try requireContains(text, "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=");
}

fn validatePolicyAndFixtureBoundary(policy_text: []const u8, fixture_text: []const u8) !void {
    try requireContains(policy_text, "\"archive_target_scope\": [");
    try requireContains(policy_text, "\"x86_64-linux\"");
    try requireOnce(policy_text, "\"phase2-cross\"");
    try requireContains(policy_text, "\"required_make_routes\": [");
    try requireContains(policy_text, "\"phase2-toolchain\"");
    try requireContains(policy_text, "\"phase2-tools\"");
    try requireContains(policy_text, "\"phase2-kconfig\"");
    try requireContains(policy_text, "\"phase2-genksyms\"");
    try requireContains(policy_text, "\"phase2-fixdep\"");
    try requireContains(policy_text, "\"phase2-validate\"");

    try requireContains(fixture_text, "\"archive_target_scope\": [");
    try requireOnce(fixture_text, "\"target\": \"x86_64-linux\"");
    try requireOnce(fixture_text, "\"target\": \"aarch64-linux\"");
    try requireOnce(fixture_text, "\"validation_mode\": \"archive_required\"");
    try requireOnce(fixture_text, "\"validation_mode\": \"route_contract_only\"");
    try requireAbsent(fixture_text, "\"target\": \"riscv64-linux\"");
    try requireAbsent(fixture_text, "\"target\": \"riscv64-linux-musl\"");
}

test "alignment checker keeps policy-derived two-target matrix explicit" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, alignment_checker_path);
    defer allocator.free(checker);

    try validateAlignmentCheckerPolicy(checker);
}

test "policy and fixture keep x86 archive scope with aarch64 route-only handoff" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);
    const fixture = try readRepoFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try validatePolicyAndFixtureBoundary(policy, fixture);
}

test "contract catches alignment checker policy drift" {
    try std.testing.expectError(ContractError.MissingMarker, validateAlignmentCheckerPolicy(
        \\\\SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")
        \\\\EXPECTED_REQUIRED_MAKE_ROUTES = (
        \\\\    "phase2-toolchain",
        \\\\    "phase2-tools",
        \\\\    "phase2-kconfig",
        \\\\    "phase2-genksyms",
        \\\\    "phase2-fixdep",
        \\\\    "phase2-validate",
        \\\\)
        \\\\required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES)
        \\\\unsupported archive_target_scope targets
        \\\\"archive_required" if target in seen_scope else "route_contract_only"
        \\\\"INVALID_CROSS_TARGET_MATRIX"
        \\\\PHASE2_CROSS_ALIGNMENT=pass
        \\\\PHASE2_CROSS_ALIGNMENT=fail
        \\\\PHASE2_CROSS_ALIGNMENT_MARKER_COUNT=
        \\\\PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=
        \\\\PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=
        \\\\PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass
        \\\\PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=
    ));

    try std.testing.expectError(ContractError.MissingMarker, validateAlignmentCheckerPolicy(
        \\\\SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")
        \\\\EXPECTED_REQUIRED_MAKE_ROUTES = (
        \\\\    "phase2-toolchain",
        \\\\    "phase2-tools",
        \\\\    "phase2-kconfig",
        \\\\    "phase2-cross",
        \\\\    "phase2-genksyms",
        \\\\    "phase2-fixdep",
        \\\\    "phase2-validate",
        \\\\)
        \\\\required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES)
        \\\\unsupported archive_target_scope targets
        \\\\"INVALID_CROSS_TARGET_MATRIX"
        \\\\PHASE2_CROSS_ALIGNMENT=pass
        \\\\PHASE2_CROSS_ALIGNMENT=fail
        \\\\PHASE2_CROSS_ALIGNMENT_MARKER_COUNT=
        \\\\PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=
        \\\\PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=
        \\\\PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass
        \\\\PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=
    ));
}

test "contract catches policy and fixture target drift" {
    const allocator = std.testing.allocator;
    const current_policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(current_policy);

    try std.testing.expectError(ContractError.MissingMarker, validatePolicyAndFixtureBoundary(
        \\\\"archive_target_scope": [
        \\\\  "aarch64-linux"
        \\\\],
        \\\\"required_make_routes": [
        \\\\  "phase2-toolchain",
        \\\\  "phase2-tools",
        \\\\  "phase2-kconfig",
        \\\\  "phase2-cross",
        \\\\  "phase2-genksyms",
        \\\\  "phase2-fixdep",
        \\\\  "phase2-validate"
        \\\\]
    ,
        \\\\"archive_target_scope": [
        \\\\    "x86_64-linux"
        \\\\  ],
        \\\\"target": "x86_64-linux",
        \\\\"target": "aarch64-linux",
        \\\\"validation_mode": "archive_required",
        \\\\"validation_mode": "route_contract_only"
    ));

    try std.testing.expectError(ContractError.DuplicateMarker, validatePolicyAndFixtureBoundary(current_policy,
        \\\\"archive_target_scope": [
        \\\\    "x86_64-linux"
        \\\\  ],
        \\\\"target": "x86_64-linux",
        \\\\"target": "x86_64-linux",
        \\\\"target": "aarch64-linux",
        \\\\"validation_mode": "archive_required",
        \\\\"validation_mode": "route_contract_only"
    ));

    try std.testing.expectError(ContractError.ForbiddenMarkerPresent, validatePolicyAndFixtureBoundary(current_policy,
        \\\\"archive_target_scope": [
        \\\\    "x86_64-linux"
        \\\\  ],
        \\\\"target": "x86_64-linux",
        \\\\"target": "aarch64-linux",
        \\\\"target": "riscv64-linux-musl",
        \\\\"validation_mode": "archive_required",
        \\\\"validation_mode": "route_contract_only"
    ));
}
