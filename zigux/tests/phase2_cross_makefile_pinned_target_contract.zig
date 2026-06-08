const std = @import("std");

const makefile_path = "zigux/Makefile";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

const route = "make -C zigux phase2-cross";
const pinned_target = "x86_64-linux";
const route_only_target = "aarch64-linux";
const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_digest = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.Options.debug_io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "Makefile derives pinned target from policy archive scope" {
    const allocator = std.testing.allocator;
    const makefile = try readFile(allocator, makefile_path);
    defer allocator.free(makefile);

    try expectContains(makefile, "PHASE2_TOOLCHAIN_POLICY := $(PHASE2_SCRIPT_ROOT)/zig-toolchain-policy.json");
    try expectContains(makefile, "ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"channel\"])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)");
    try expectContains(makefile, "ZIG_PINNED_TARGET := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"upgrade_policy\"][\"archive_target_scope\"][0])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)");
    try expectContains(makefile, "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)");
    try expectOrder(makefile, "ZIG_PINNED_CHANNEL :=", "ZIG_PINNED_TARGET :=");
    try expectOrder(makefile, "ZIG_PINNED_TARGET :=", "ZIG_PINNED_EXTRACT_ROOT :=");
}

test "Makefile prefers pinned archive executable before local toolchain and PATH export" {
    const allocator = std.testing.allocator;
    const makefile = try readFile(allocator, makefile_path);
    defer allocator.free(makefile);

    try expectContains(makefile, "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))");
    try expectContains(makefile, "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))");
    try expectContains(makefile, "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))");
    try expectContains(makefile, "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)");
    try expectContains(makefile, "ZIG_REPO_ROOT_DIR := $(dir $(ZIG_REPO_ROOT))");
    try expectContains(makefile, "export PATH := $(ZIG_REPO_ROOT_DIR):$(PATH)");
    try expectOrder(makefile, "ZIG_PINNED_EXECUTABLE :=", "ZIG_LOCAL_TOOLCHAIN :=");
    try expectOrder(makefile, "ZIG_LOCAL_TOOLCHAIN :=", "ZIG_PINNED_TOOLCHAIN :=");
    try expectOrder(makefile, "ZIG_REPO_ROOT_DIR :=", "export PATH :=");
}

test "policy keeps single archive-backed target used by Makefile derivation" {
    const allocator = std.testing.allocator;
    const policy = try readFile(allocator, policy_path);
    defer allocator.free(policy);

    try expectContains(policy, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"x86_64-linux\": \"" ++ pinned_digest ++ "\"");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"" ++ pinned_target ++ "\"\n    ]");
    try expectContains(policy, "\"phase2-cross\"");
    try expectNotContains(policy, "\"aarch64-linux\": \"");
    try expectNotContains(policy, "riscv64-linux");
}

test "fixture remains aligned with pinned target and route-only target boundary" {
    const allocator = std.testing.allocator;
    const fixture = try readFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try expectContains(fixture, "\"route\": \"" ++ route ++ "\"");
    try expectContains(fixture, "\"archive_target_scope\": [\n    \"" ++ pinned_target ++ "\"\n  ]");
    try expectContains(fixture, "\"target\": \"" ++ pinned_target ++ "\"");
    try expectContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"" ++ route_only_target ++ "\"");
    try expectContains(fixture, "\"review_status\": \"route contract only\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");
}
