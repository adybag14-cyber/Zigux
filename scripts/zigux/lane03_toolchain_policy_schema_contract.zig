const std = @import("std");
const policy = @import("toolchain_policy.zig");

test "toolchain policy schema parser keeps duplicate-aware strict key gates" {
    const duplicate_routes =
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.877+a3ae499dc",
        \\  "minimum_version": "0.17.0-dev.877+a3ae499dc",
        \\  "archive_sha256": {
        \\    "x86_64-linux": "c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8"
        \\  },
        \\  "upgrade_policy": {
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["x86_64-linux"],
        \\    "required_make_routes": ["phase2-toolchain", "phase2-toolchain"]
        \\  }
        \\}
    ;
    try std.testing.expectError(
        policy.ToolchainPolicyError.DuplicatePolicyKey,
        policy.loadPolicyFromJson(std.testing.allocator, duplicate_routes),
    );
}

test "toolchain policy parser fail-closes malformed archive and route fields" {
    const bad_digest =
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.877+a3ae499dc",
        \\  "minimum_version": "0.17.0-dev.877+a3ae499dc",
        \\  "archive_sha256": {
        \\    "x86_64-linux": "oops"
        \\  },
        \\  "upgrade_policy": {
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["x86_64-linux"],
        \\    "required_make_routes": ["phase2-toolchain"]
        \\  }
        \\}
    ;
    try std.testing.expectError(
        policy.ToolchainPolicyError.InvalidPolicyField,
        policy.loadPolicyFromJson(std.testing.allocator, bad_digest),
    );

    const scope_mismatch =
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.877+a3ae499dc",
        \\  "minimum_version": "0.17.0-dev.877+a3ae499dc",
        \\  "archive_sha256": {
        \\    "x86_64-linux": "c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8"
        \\  },
        \\  "upgrade_policy": {
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["aarch64-linux"],
        \\    "required_make_routes": ["phase2-toolchain"]
        \\  }
        \\}
    ;
    try std.testing.expectError(
        policy.ToolchainPolicyError.ArchiveTargetMismatch,
        policy.loadPolicyFromJson(std.testing.allocator, scope_mismatch),
    );
}

test "toolchain policy parser keeps pinned channel lockstep explicit" {
    const lockstep_mismatch =
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.877+a3ae499dc",
        \\  "minimum_version": "0.17.0-dev.90+abcdef",
        \\  "archive_sha256": {
        \\    "x86_64-linux": "c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8"
        \\  },
        \\  "upgrade_policy": {
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["x86_64-linux"],
        \\    "required_make_routes": ["phase2-toolchain"]
        \\  }
        \\}
    ;
    try std.testing.expectError(
        policy.ToolchainPolicyError.ChannelLockstepMismatch,
        policy.loadPolicyFromJson(std.testing.allocator, lockstep_mismatch),
    );
}

test "policy-only invalid schema reports actionable status through checker" {
    const checker = @import("check_zig_toolchain.zig");
    try std.testing.expectEqualStrings("scripts/zigux/zig-toolchain-policy.json", checker.default_policy_path);
    try std.testing.expectEqualStrings("0.16.0", checker.fallback_min_version);
}