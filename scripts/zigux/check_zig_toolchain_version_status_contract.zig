const std = @import("std");
const policy = @import("toolchain_policy.zig");
const resolver = @import("toolchain_resolver.zig");
const checker = @import("check_zig_toolchain.zig");

test "toolchain version status decisions remain exact and ordered" {
    const too_old = try policy.evaluateToolchainVersion(
        "0.17.0-dev.757+abcdef",
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
    );
    try std.testing.expectEqual(policy.ToolchainStatus.too_old, too_old.status);

    const not_pinned = try policy.evaluateToolchainVersion(
        "0.17.0",
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
    );
    try std.testing.expectEqual(policy.ToolchainStatus.not_pinned, not_pinned.status);
    try std.testing.expect(not_pinned.note != null);

    const present = try policy.evaluateToolchainVersion(
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
    );
    try std.testing.expectEqual(policy.ToolchainStatus.present, present.status);
}

test "toolchain status names map to machine-readable CLI values" {
    try std.testing.expectEqualStrings("present", resolver.toolchainStatusName(.present));
    try std.testing.expectEqualStrings("too_old", resolver.toolchainStatusName(.too_old));
    try std.testing.expectEqualStrings("not_pinned", resolver.toolchainStatusName(.not_pinned));
}

test "checker self-test catalog covers present not-pinned and too-old outcomes" {
    const present = try policy.evaluateToolchainVersion(
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
    );
    try std.testing.expectEqual(policy.ToolchainStatus.present, present.status);

    const not_pinned = try policy.evaluateToolchainVersion(
        "0.17.0-dev.877+stalehash",
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
    );
    try std.testing.expectEqual(policy.ToolchainStatus.not_pinned, not_pinned.status);

    const too_old = try policy.evaluateToolchainVersion(
        "0.17.0-dev.757+abcdef",
        "0.17.0-dev.877+a3ae499dc",
        null,
    );
    try std.testing.expectEqual(policy.ToolchainStatus.too_old, too_old.status);
    _ = checker.fallback_min_version;
}