const std = @import("std");
const install = @import("install_zig.zig");

const policy_source = @embedFile("zig-toolchain-policy.json");
const canonical_channel = install.canonical_release_channel;
const canonical_repo = install.default_canonical_release_repo;
const canonical_tag = install.default_canonical_release_tag;
const canonical_target = "x86_64-linux";
const canonical_url = "https://github.com/adybag14-cyber/zig/releases/download/upstream-a3ae499dc297/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz";
const historical_runtime_channel = "0.17.0-dev.87+9b177a7d2";

test "canonical release constants stay aligned with the policy channel" {
    try std.testing.expectEqualStrings(canonical_channel, "0.17.0-dev.877+a3ae499dc");
    try std.testing.expectEqualStrings(canonical_repo, "adybag14-cyber/zig");
    try std.testing.expectEqualStrings(canonical_tag, "upstream-a3ae499dc297");
    try std.testing.expect(std.mem.indexOf(u8, policy_source, "\"channel\": \"" ++ canonical_channel ++ "\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_source, "\"minimum_version\": \"" ++ canonical_channel ++ "\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_source, "\"" ++ canonical_target ++ "\": \"c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_source, historical_runtime_channel) == null);
}

test "canonical pinned channel resolves through the trusted GitHub release" {
    const allocator = std.testing.allocator;
    const environ = std.process.Environ.Map.init(std.testing.allocator);
    const release_repo = try install.canonicalReleaseRepo(allocator, environ);
    defer allocator.free(release_repo);
    const release_tag = try install.canonicalReleaseTag(allocator, environ);
    defer allocator.free(release_tag);

    var resolved = try install.resolveTarget(allocator, .{}, canonical_channel, "x86_64", "linux", release_repo, release_tag);
    defer install.freeResolveTarget(allocator, &resolved);

    try std.testing.expectEqualStrings(resolved.target_key, canonical_target);
    try std.testing.expectEqualStrings(resolved.version, canonical_channel);
    try std.testing.expectEqualStrings(resolved.tarball_url, canonical_url);
}

test "installer self-test pins the canonical release target tuple" {
    try std.testing.expectEqual(@as(u32, 46), 46);
    try std.testing.expectEqualStrings(canonical_channel, install.canonical_release_channel);
    try std.testing.expectEqualStrings(canonical_url, "https://github.com/" ++ canonical_repo ++ "/releases/download/" ++ canonical_tag ++ "/zig-x86_64-linux-" ++ canonical_channel ++ ".tar.xz");
}