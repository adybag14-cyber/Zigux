const std = @import("std");
const policy = @import("toolchain_policy.zig");
const resolver = @import("toolchain_resolver.zig");

test "multi-target policy requires explicit archive target when archive path is explicit" {
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
        \\    "archive_target_scope": ["x86_64-linux", "aarch64-linux"],
        \\    "required_make_routes": ["phase2-toolchain"]
        \\  }
        \\}
    ;
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    const resolved = resolver.resolvePolicyArchive(
        std.testing.io,
        std.testing.allocator,
        &loaded,
        ".",
        "third_party/explicit.tar.xz",
        null,
    );
    try std.testing.expectError(resolver.ResolverError.InvalidArgument, resolved);
}

test "out-of-scope explicit archive targets fail closed" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    const resolved = resolver.resolvePolicyArchive(
        std.testing.io,
        std.testing.allocator,
        &loaded,
        ".",
        "third_party/explicit.tar.xz",
        "aarch64-linux",
    );
    try std.testing.expectError(resolver.ResolverError.InvalidArgument, resolved);

    const note = try resolver.formatResolvePolicyArchiveError(
        std.testing.allocator,
        resolver.ResolverError.InvalidArgument,
        &loaded,
        "aarch64-linux",
        "third_party/explicit.tar.xz",
    );
    defer std.testing.allocator.free(note);
    try std.testing.expect(std.mem.indexOf(u8, note, "outside archive_target_scope") != null);
}

test "invalid explicit archive path diagnostics keep target metadata available" {
    const io = std.testing.io;
    const note = try resolver.describeInvalidExplicitArchivePath(io, std.testing.allocator, ".");
    defer if (note) |text| std.testing.allocator.free(text);
    try std.testing.expect(note != null);
    try std.testing.expect(std.mem.indexOf(u8, note.?, "regular file") != null);
}