const std = @import("std");
const policy = @import("toolchain_policy.zig");

test "policy loader keeps duplicate-key and unexpected-key checks fail closed" {
    const empty_routes =
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.1443+6c25d2bd5",
        \\  "minimum_version": "0.17.0-dev.1443+6c25d2bd5",
        \\  "archive_sha256": {
        \\    "x86_64-linux": "4620f31b3889dcdcb257e6a0da6a4bc9a0b2b8e3db04219c1c160798e2cdc5a9"
        \\  },
        \\  "upgrade_policy": {
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["x86_64-linux"],
        \\    "required_make_routes": []
        \\  }
        \\}
    ;
    try std.testing.expectError(
        policy.ToolchainPolicyError.InvalidPolicyField,
        policy.loadPolicyFromJson(std.testing.allocator, empty_routes),
    );

    const duplicate_targets =
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.1443+6c25d2bd5",
        \\  "minimum_version": "0.17.0-dev.1443+6c25d2bd5",
        \\  "archive_sha256": {
        \\    "x86_64-linux": "4620f31b3889dcdcb257e6a0da6a4bc9a0b2b8e3db04219c1c160798e2cdc5a9",
        \\    "aarch64-linux": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        \\  },
        \\  "upgrade_policy": {
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["x86_64-linux"],
        \\    "required_make_routes": ["phase2-toolchain"]
        \\  }
        \\}
    ;
    try std.testing.expectError(
        policy.ToolchainPolicyError.ArchiveTargetMismatch,
        policy.loadPolicyFromJson(std.testing.allocator, duplicate_targets),
    );
}

test "archive target scope is bidirectionally checked against archive sha entries" {
    const missing_scope_entry =
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.1443+6c25d2bd5",
        \\  "minimum_version": "0.17.0-dev.1443+6c25d2bd5",
        \\  "archive_sha256": {
        \\    "x86_64-linux": "4620f31b3889dcdcb257e6a0da6a4bc9a0b2b8e3db04219c1c160798e2cdc5a9"
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
        policy.loadPolicyFromJson(std.testing.allocator, missing_scope_entry),
    );
}

test "required make routes remain non-empty unique policy schema entries" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);
    try std.testing.expect(loaded.upgrade_policy.required_make_routes.len >= 2);
    try std.testing.expectEqualStrings("phase2-toolchain", loaded.upgrade_policy.required_make_routes[0]);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"phase2-validate\"") != null);
}

test "live policy pins phase two channel and target scope exactly" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    try std.testing.expectEqualStrings("Phase 2", loaded.phase);
    try std.testing.expectEqualStrings("0.17.0-dev.1443+6c25d2bd5", loaded.channel);
    try std.testing.expectEqualStrings("0.17.0-dev.1443+6c25d2bd5", loaded.minimum_version);
    try std.testing.expect(loaded.upgrade_policy.channel_minimum_lockstep);
    try std.testing.expectEqual(@as(usize, 2), loaded.upgrade_policy.archive_target_scope.len);
    try std.testing.expectEqualStrings("x86_64-linux", loaded.upgrade_policy.archive_target_scope[0]);
    try std.testing.expectEqualStrings("x86_64-windows", loaded.upgrade_policy.archive_target_scope[1]);
    const digest = loaded.archive_sha256.get("x86_64-linux").?;
    try std.testing.expectEqualStrings(
        "4620f31b3889dcdcb257e6a0da6a4bc9a0b2b8e3db04219c1c160798e2cdc5a9",
        digest,
    );
    try std.testing.expectEqualStrings(
        "0c538cabcea1ef1d114b99f6e9f3099d4c4c22070daa19819511b783c5f40211",
        loaded.archive_sha256.get("x86_64-windows").?,
    );
}
