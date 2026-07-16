const std = @import("std");
const policy = @import("toolchain_policy.zig");
const resolver = @import("toolchain_resolver.zig");

test "explicit archive target must stay inside archive_target_scope" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    const resolved = resolver.resolvePolicyArchive(
        std.testing.io,
        std.testing.allocator,
        &loaded,
        ".",
        "third_party/missing.tar.xz",
        "aarch64-linux",
    );
    try std.testing.expectError(resolver.ResolverError.InvalidArgument, resolved);
}

test "expected archive metadata rejects out-of-scope targets" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    var filename_buffer: [160]u8 = undefined;
    const result = resolver.expectedArchiveMetadata(&loaded, "aarch64-linux", &filename_buffer);
    try std.testing.expectError(resolver.ResolverError.InvalidArgument, result);
}

test "multi-target policy requires an explicit target for an explicit archive path" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    const ambiguous = resolver.resolvePolicyArchive(
        std.testing.io,
        std.testing.allocator,
        &loaded,
        ".",
        "third_party/explicit.tar.xz",
        null,
    );
    try std.testing.expectError(resolver.ResolverError.InvalidArgument, ambiguous);

    const resolved = try resolver.resolvePolicyArchive(
        std.testing.io,
        std.testing.allocator,
        &loaded,
        ".",
        "third_party/explicit.tar.xz",
        "x86_64-linux",
    );
    defer resolver.freeResolvedArchive(std.testing.allocator, resolved);
    try std.testing.expectEqualStrings("x86_64-linux", resolved.target.?);
    try std.testing.expectEqualStrings("third_party/explicit.tar.xz", resolved.path.?);
}
