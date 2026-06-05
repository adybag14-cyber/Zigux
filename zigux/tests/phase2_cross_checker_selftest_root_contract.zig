const std = @import("std");

const fixture = @embedFile("fixtures/phase2_cross_targets.json");
const checker_path = "scripts/zigux/check-phase2-cross.py";

const ContractError = error{
    MissingMarker,
    ForbiddenMarkerPresent,
};

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn requireContains(text: []const u8, marker: []const u8) !void {
    if (!contains(text, marker)) return ContractError.MissingMarker;
}

fn requireAbsent(text: []const u8, marker: []const u8) !void {
    if (contains(text, marker)) return ContractError.ForbiddenMarkerPresent;
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

fn validateSelfTestRootPacket(text: []const u8) !void {
    try requireContains(text, "def build_self_test_root(root: Path) -> None:");
    try requireContains(text, "\"archive_target_scope\": [\"x86_64-linux\"]");
    try requireContains(text, "\"target\": \"x86_64-linux\"");
    try requireContains(text, "\"review_status\": \"pinned bootstrap archive\"");
    try requireContains(text, "\"validation_mode\": \"archive_required\"");
    try requireContains(text, "\"target\": \"aarch64-linux\"");
    try requireContains(text, "\"review_status\": \"route contract only\"");
    try requireContains(text, "\"validation_mode\": \"route_contract_only\"");
    try requireContains(text, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try requireContains(text, "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try requireContains(text, "fixture[\"archive_target_scope\"] = [\"aarch64-linux\"]");
    try requireContains(text, "fixture[\"cross_targets\"][0][\"validation_mode\"] = \"route_contract_only\"");
    try requireContains(text, "fixture[\"cross_targets\"].append(dict(fixture[\"cross_targets\"][0]))");
    try requireContains(text, "fixture[\"cross_targets\"][1][\"route\"] = \"make -C zigux phase2\"");
    try requireContains(text, "fixture[\"cross_targets\"][1][\"review_status\"] = \"\"");
    try requireContains(text, "fixture[\"cross_targets\"][1][\"validation_mode\"] = \"unexpected_mode\"");
    try requireContains(text, "policy[\"upgrade_policy\"][\"archive_target_scope\"] = [\"x86_64-linux\", \"x86_64-linux\"]");
    try requireContains(text, "for primary_path in (TOOLCHAIN_POLICY, MAKEFILE, FIXTURE):");
    try requireAbsent(text, "\"target\": \"riscv64-linux\"");
}

fn validateFixturePacket(text: []const u8) !void {
    try requireContains(text, "\"route\": \"make -C zigux phase2-cross\"");
    try requireContains(text, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try requireContains(text, "\"target\": \"x86_64-linux\"");
    try requireContains(text, "\"review_status\": \"pinned bootstrap archive\"");
    try requireContains(text, "\"validation_mode\": \"archive_required\"");
    try requireContains(text, "\"target\": \"aarch64-linux\"");
    try requireContains(text, "\"review_status\": \"route contract only\"");
    try requireContains(text, "\"validation_mode\": \"route_contract_only\"");
    try requireAbsent(text, "\"target\": \"riscv64-linux\"");
}

test "direct cross checker self-test root mirrors the live two-target packet" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try validateSelfTestRootPacket(checker);
}

test "cross fixture keeps the same target vocabulary as the checker self-test root" {
    try validateFixturePacket(fixture);
}

test "contract catches stale checker self-test root drift" {
    try std.testing.expectError(ContractError.MissingMarker, validateSelfTestRootPacket(
        \\def build_self_test_root(root: Path) -> None:
        \\    pass
        \\EXPECTED_SELF_TEST_CASE_COUNT = 17
        \\assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
        \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass
    ));

    try std.testing.expectError(
        ContractError.ForbiddenMarkerPresent,
        requireAbsent("\"target\": \"riscv64-linux\"", "\"target\": \"riscv64-linux\""),
    );
}

test "contract catches stale fixture drift" {
    try std.testing.expectError(ContractError.MissingMarker, validateFixturePacket(
        \\"route": "make -C zigux phase2-cross"
        \\"target": "x86_64-linux"
        \\"review_status": "pinned bootstrap archive"
        \\"validation_mode": "archive_required"
        \\"target": "aarch64-linux"
        \\"review_status": "route contract only"
        \\"validation_mode": "route_contract_only"
    ));

    try std.testing.expectError(
        ContractError.ForbiddenMarkerPresent,
        requireAbsent("\"target\": \"riscv64-linux\"", "\"target\": \"riscv64-linux\""),
    );
}
