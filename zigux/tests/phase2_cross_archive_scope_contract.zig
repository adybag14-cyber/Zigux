const std = @import("std");

const fixture = @embedFile("fixtures/phase2_cross_targets.json");
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

const archive_scope_block =
    \\"archive_target_scope": [
    \\    "x86_64-linux"
    \\  ]
;
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

fn validateFixtureArchiveScope(text: []const u8) !void {
    try requireContains(text, "\"phase\": \"Phase 2\"");
    try requireContains(text, "\"status\": \"active\"");
    try requireContains(text, "\"route\": \"make -C zigux phase2-cross\"");
    try requireContains(text, archive_scope_block);
    try requireOnce(text, "\"target\": \"x86_64-linux\"");
    try requireOnce(text, "\"target\": \"aarch64-linux\"");
    try requireOnce(text, "\"validation_mode\": \"archive_required\"");
    try requireOnce(text, "\"validation_mode\": \"route_contract_only\"");
    try requireOnce(text, "\"review_status\": \"pinned bootstrap archive\"");
    try requireOnce(text, "\"review_status\": \"route contract only\"");
    try requireAbsent(text, "\"target\": \"aarch64-linux\",\n      \"review_status\": \"route contract only\",\n      \"validation_mode\": \"archive_required\"");
    try requireAbsent(text, "\"target\": \"x86_64-linux\",\n      \"review_status\": \"pinned bootstrap archive\",\n      \"validation_mode\": \"route_contract_only\"");
    try requireAbsent(text, "\"target\": \"riscv64-linux\"");
}

fn validatePolicyArchiveScope(text: []const u8) !void {
    try requireContains(text, "\"phase\": \"Phase 2\"");
    try requireContains(text, "\"archive_sha256\": {");
    try requireContains(text, "\"archive_target_scope\": [");
    try requireContains(text, "\"required_make_routes\": [");
    try requireOnce(text, "\"phase2-cross\"");
    try requireOnce(text, "\"archive_target_scope\"");
    try requireCount(text, "\"x86_64-linux\"", 2);
    try requireAbsent(text, "\"aarch64-linux\"");
    try requireAbsent(text, "\"riscv64-linux\"");
}

test "fixture keeps archive-backed x86 and route-only aarch64 separated" {
    try validateFixtureArchiveScope(fixture);
}

test "policy keeps archive scope pinned to the x86 bootstrap archive" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);

    try validatePolicyArchiveScope(policy);
}

test "contract catches fixture archive-scope drift" {
    const missing_scope =
        \\"phase": "Phase 2",
        \\"status": "active",
        \\"route": "make -C zigux phase2-cross",
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
        \\    "validation_mode": "route_contract_only",
        \\    "route": "make -C zigux phase2-cross"
        \\  }
        \\]
    ;
    try std.testing.expectError(ContractError.MissingMarker, validateFixtureArchiveScope(missing_scope));

    const promoted_aarch64 =
        \\"phase": "Phase 2",
        \\"status": "active",
        \\"route": "make -C zigux phase2-cross",
        \\"archive_target_scope": [
        \\    "x86_64-linux"
        \\  ],
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
    try std.testing.expectError(ContractError.DuplicateMarker, validateFixtureArchiveScope(promoted_aarch64));
}

test "contract catches policy archive-scope drift" {
    const missing_cross_route =
        \\"phase": "Phase 2",
        \\"archive_sha256": {
        \\  "x86_64-linux": "0"
        \\},
        \\"upgrade_policy": {
        \\  "archive_target_scope": [
        \\    "x86_64-linux"
        \\  ],
        \\  "required_make_routes": [
        \\    "phase2-toolchain",
        \\    "phase2-validate"
        \\  ]
        \\}
    ;
    try std.testing.expectError(ContractError.MissingMarker, validatePolicyArchiveScope(missing_cross_route));

    const widened_archive_scope =
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
        \\    "phase2-toolchain",
        \\    "phase2-tools",
        \\    "phase2-kconfig",
        \\    "phase2-cross",
        \\    "phase2-genksyms",
        \\    "phase2-fixdep",
        \\    "phase2-validate"
        \\  ]
        \\}
    ;
    try std.testing.expectError(ContractError.ForbiddenMarkerPresent, validatePolicyArchiveScope(widened_archive_scope));
}
