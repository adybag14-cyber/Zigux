const std = @import("std");
const testing = std.testing;

const policy =
    \\{
    \\  "phase": "Phase 2",
    \\  "channel": "0.17.0-dev.758+748e7c5e3",
    \\  "minimum_version": "0.17.0-dev.758+748e7c5e3",
    \\  "archive_sha256": {
    \\    "x86_64-linux": "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6"
    \\  },
    \\  "upgrade_policy": {
    \\    "channel_minimum_lockstep": true,
    \\    "archive_target_scope": [
    \\      "x86_64-linux"
    \\    ],
    \\    "required_make_routes": [
    \\      "phase2-toolchain",
    \\      "phase2-tools",
    \\      "phase2-kconfig",
    \\      "phase2-cross",
    \\      "phase2-genksyms",
    \\      "phase2-fixdep",
    \\      "phase2-validate"
    \\    ]
    \\  }
    \\}
;

const fixture =
    \\{
    \\  "phase": "Phase 2",
    \\  "status": "active",
    \\  "route": "make -C zigux phase2-cross",
    \\  "archive_target_scope": [
    \\    "x86_64-linux"
    \\  ],
    \\  "cross_targets": [
    \\    {
    \\      "target": "x86_64-linux",
    \\      "review_status": "pinned bootstrap archive",
    \\      "validation_mode": "archive_required",
    \\      "route": "make -C zigux phase2-cross"
    \\    },
    \\    {
    \\      "target": "aarch64-linux",
    \\      "review_status": "route contract only",
    \\      "validation_mode": "route_contract_only",
    \\      "route": "make -C zigux phase2-cross"
    \\    }
    \\  ]
    \\}
;

const pinned_target = "x86_64-linux";
const route_only_target = "aarch64-linux";
const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const direct_cross_route = "make -C zigux phase2-cross";

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn count(haystack: []const u8, needle: []const u8) usize {
    return std.mem.count(u8, haystack, needle);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(contains(haystack, needle));
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(!contains(haystack, needle));
}

test "policy pins the current Phase 2 x86 archive identity" {
    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"minimum_version\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"" ++ pinned_target ++ "\": \"" ++ pinned_sha256 ++ "\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try testing.expectEqual(@as(usize, 2), count(policy, "\"" ++ pinned_target ++ "\""));
    try expectNotContains(policy, "\"" ++ route_only_target ++ "\":");
}

test "policy keeps phase2-cross in the ordered required route packet" {
    const tools_index = std.mem.indexOf(u8, policy, "\"phase2-tools\"").?;
    const kconfig_index = std.mem.indexOf(u8, policy, "\"phase2-kconfig\"").?;
    const cross_index = std.mem.indexOf(u8, policy, "\"phase2-cross\"").?;
    const genksyms_index = std.mem.indexOf(u8, policy, "\"phase2-genksyms\"").?;
    const fixdep_index = std.mem.indexOf(u8, policy, "\"phase2-fixdep\"").?;
    const validate_index = std.mem.indexOf(u8, policy, "\"phase2-validate\"").?;

    try testing.expect(tools_index < kconfig_index);
    try testing.expect(kconfig_index < cross_index);
    try testing.expect(cross_index < genksyms_index);
    try testing.expect(genksyms_index < fixdep_index);
    try testing.expect(fixdep_index < validate_index);
    try testing.expectEqual(@as(usize, 1), count(policy, "\"phase2-cross\""));
}

test "fixture mirrors the archive-backed and route-only target split" {
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"" ++ direct_cross_route ++ "\"");
    try expectContains(fixture, "\"archive_target_scope\"");
    try testing.expectEqual(@as(usize, 2), count(fixture, "\"" ++ pinned_target ++ "\""));
    try testing.expectEqual(@as(usize, 1), count(fixture, "\"" ++ route_only_target ++ "\""));
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture, "\"review_status\": \"route contract only\"");
}

test "policy and fixture reject stale historical matrix vocabulary" {
    try expectNotContains(policy, "0.17.0-dev.87+9b177a7d2");
    try expectNotContains(policy, "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77");
    try expectNotContains(fixture, "\"target_count\"");
    try expectNotContains(fixture, "\"zig_test_files\"");
    try expectNotContains(fixture, "\"riscv64-linux\"");
    try expectNotContains(fixture, "x86_64-linux-musl");
    try expectNotContains(fixture, "aarch64-linux-musl");
}
