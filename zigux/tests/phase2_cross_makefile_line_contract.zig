const std = @import("std");

const fixture = @embedFile("fixtures/phase2_cross_targets.json");
const checker_path = "scripts/zigux/check-phase2-cross.py";

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

fn validateCheckerMakefileEnvelope(text: []const u8) !void {
    try requireContains(text, "MAKEFILE_LINES = (");
    try requireContains(text, "\"phase2-cross:\"");
    try requireContains(text, "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py\"");
    try requireContains(text, "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py\"");
    try requireContains(text, "EXPECTED_FIXTURE_PHASE = \"Phase 2\"");
    try requireContains(text, "EXPECTED_FIXTURE_STATUS = \"active\"");
    try requireContains(text, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
    try requireContains(text, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE=fail");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=");
    try requireContains(text, "MISSING_MAKEFILE_LINE");
    try requireContains(text, "DUPLICATE_MAKEFILE_LINE");
    try requireContains(text, "INVALID_FIXTURE_FIELD");
    try requireContains(text, "ARCHIVE_SCOPE_MISMATCH");
    try requireContains(text, "INVALID_CROSS_TARGET_ENTRY");
    try requireContains(text, "DUPLICATE_CROSS_TARGET");
    try requireContains(text, "INVALID_CROSS_TARGET_ROUTE");
    try requireContains(text, "INVALID_CROSS_TARGET_MODE");
    try requireContains(text, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
}

fn validateFixtureMakefileBoundary(text: []const u8) !void {
    try requireContains(text, "\"phase\": \"Phase 2\"");
    try requireContains(text, "\"status\": \"active\"");
    try requireContains(text, "\"route\": \"make -C zigux phase2-cross\"");
    try requireContains(text, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try requireOnce(text, "\"target\": \"x86_64-linux\"");
    try requireOnce(text, "\"target\": \"aarch64-linux\"");
    try requireOnce(text, "\"validation_mode\": \"archive_required\"");
    try requireOnce(text, "\"validation_mode\": \"route_contract_only\"");
    try requireOnce(text, "\"review_status\": \"pinned bootstrap archive\"");
    try requireOnce(text, "\"review_status\": \"route contract only\"");
    try requireAbsent(text, "\"target\": \"riscv64-linux\"");
}

test "direct checker keeps Makefile line and issue-code envelope explicit" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try validateCheckerMakefileEnvelope(checker);
}

test "cross fixture keeps direct phase2-cross route and two-target boundary" {
    try validateFixtureMakefileBoundary(fixture);
}

test "contract catches checker Makefile-envelope drift" {
    try std.testing.expectError(ContractError.MissingMarker, validateCheckerMakefileEnvelope(
        \\MAKEFILE_LINES = (
        \\    "phase2-cross:"
        \\    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py"
        \\)
        \\EXPECTED_FIXTURE_PHASE = "Phase 2"
        \\EXPECTED_FIXTURE_STATUS = "active"
        \\ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")
        \\EXPECTED_SELF_TEST_CASE_COUNT = 17
        \\PHASE2_DIRECT_CROSS_ROUTE=pass
        \\PHASE2_DIRECT_CROSS_ROUTE=fail
        \\PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=
        \\PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=
        \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass
        \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=
        \\MISSING_MAKEFILE_LINE
        \\DUPLICATE_MAKEFILE_LINE
        \\INVALID_FIXTURE_FIELD
        \\ARCHIVE_SCOPE_MISMATCH
        \\INVALID_CROSS_TARGET_ENTRY
        \\DUPLICATE_CROSS_TARGET
        \\INVALID_CROSS_TARGET_ROUTE
        \\INVALID_CROSS_TARGET_MODE
        \\ARCHIVE_REQUIRED_TARGET_SET_MISMATCH
    ));

    try std.testing.expectError(ContractError.MissingMarker, validateCheckerMakefileEnvelope(
        \\MAKEFILE_LINES = (
        \\    "phase2-cross:"
        \\    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py"
        \\    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py"
        \\)
        \\EXPECTED_FIXTURE_PHASE = "Phase 2"
        \\EXPECTED_FIXTURE_STATUS = "active"
        \\ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")
        \\PHASE2_DIRECT_CROSS_ROUTE=pass
        \\PHASE2_DIRECT_CROSS_ROUTE=fail
        \\PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=
        \\PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=
        \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass
        \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=
        \\MISSING_MAKEFILE_LINE
        \\DUPLICATE_MAKEFILE_LINE
        \\INVALID_FIXTURE_FIELD
        \\ARCHIVE_SCOPE_MISMATCH
        \\INVALID_CROSS_TARGET_ENTRY
        \\DUPLICATE_CROSS_TARGET
        \\INVALID_CROSS_TARGET_ROUTE
        \\INVALID_CROSS_TARGET_MODE
        \\ARCHIVE_REQUIRED_TARGET_SET_MISMATCH
    ));
}

test "contract catches fixture route and target drift" {
    try std.testing.expectError(ContractError.MissingMarker, validateFixtureMakefileBoundary(
        \\"phase": "Phase 2",
        \\"status": "active",
        \\"route": "make -C zigux phase2-cross",
        \\"cross_targets": [
        \\  {"target": "x86_64-linux", "validation_mode": "archive_required"},
        \\  {"target": "aarch64-linux", "validation_mode": "route_contract_only"}
        \\]
    ));

    try std.testing.expectError(ContractError.DuplicateMarker, validateFixtureMakefileBoundary(
        \\"phase": "Phase 2",
        \\"status": "active",
        \\"route": "make -C zigux phase2-cross",
        \\"archive_target_scope": [
        \\    "x86_64-linux"
        \\  ],
        \\"cross_targets": [
        \\  {"target": "x86_64-linux", "review_status": "pinned bootstrap archive", "validation_mode": "archive_required"},
        \\  {"target": "x86_64-linux", "review_status": "route contract only", "validation_mode": "route_contract_only"}
        \\]
    ));

    try std.testing.expectError(ContractError.ForbiddenMarkerPresent, validateFixtureMakefileBoundary(
        \\"phase": "Phase 2",
        \\"status": "active",
        \\"route": "make -C zigux phase2-cross",
        \\"archive_target_scope": [
        \\    "x86_64-linux"
        \\  ],
        \\"cross_targets": [
        \\  {"target": "x86_64-linux", "review_status": "pinned bootstrap archive", "validation_mode": "archive_required"},
        \\  {"target": "aarch64-linux", "review_status": "route contract only", "validation_mode": "route_contract_only"},
        \\  {"target": "riscv64-linux", "review_status": "unsupported", "validation_mode": "unsupported"}
        \\]
    ));
}
