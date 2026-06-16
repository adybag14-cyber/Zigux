const std = @import("std");
const policy = @import("toolchain_policy.zig");

test "policy parser rejects duplicate required make routes" {
    const json =
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
    try std.testing.expectError(policy.ToolchainPolicyError.DuplicatePolicyKey, policy.loadPolicyFromJson(std.testing.allocator, json));
}

test "policy schema rejects unexpected archive target scope mismatch" {
    const json =
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.877+a3ae499dc",
        \\  "minimum_version": "0.17.0-dev.877+a3ae499dc",
        \\  "archive_sha256": {
        \\    "x86_64-linux": "c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8",
        \\    "aarch64-linux": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        \\  },
        \\  "upgrade_policy": {
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["x86_64-linux"],
        \\    "required_make_routes": ["phase2-toolchain"]
        \\  }
        \\}
    ;
    try std.testing.expectError(policy.ToolchainPolicyError.ArchiveTargetMismatch, policy.loadPolicyFromJson(std.testing.allocator, json));
}

test "policy cross-field invariants are fail-closed" {
    const json =
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.877+a3ae499dc",
        \\  "minimum_version": "0.17.0-dev.100+stalehash",
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
    try std.testing.expectError(policy.ToolchainPolicyError.ChannelLockstepMismatch, policy.loadPolicyFromJson(std.testing.allocator, json));
}

test "live policy keeps exact pinned channel and route scope" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    try std.testing.expectEqualStrings("0.17.0-dev.877+a3ae499dc", loaded.channel);
    try std.testing.expectEqualStrings("0.17.0-dev.877+a3ae499dc", loaded.minimum_version);
    const digest = loaded.archive_sha256.get("x86_64-linux").?;
    try std.testing.expectEqualStrings(
        "c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8",
        digest,
    );
    try std.testing.expect(loaded.upgrade_policy.channel_minimum_lockstep);
    try std.testing.expectEqual(@as(usize, 7), loaded.upgrade_policy.required_make_routes.len);
}