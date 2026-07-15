const std = @import("std");
const resolver = @import("toolchain_resolver.zig");

test "explicit zig path is validated before repo-local and PATH fallback" {
    const missing = resolver.resolveZigExecutable(
        std.testing.io,
        std.testing.allocator,
        ".",
        "missing-zig-path",
        null,
    );
    try std.testing.expectError(resolver.ResolverError.InvalidArgument, missing);

    const directory = resolver.resolveZigExecutable(
        std.testing.io,
        std.testing.allocator,
        ".",
        ".",
        null,
    );
    try std.testing.expectError(resolver.ResolverError.InvalidArgument, directory);
}

test "repo-local zig search roots include workspace and parent fallbacks" {
    const roots = try resolver.iterZigSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);
    var has_dot_toolchain = false;
    var has_toolchains = false;
    for (roots) |root| {
        if (std.mem.endsWith(u8, root, "/.zig-toolchain")) has_dot_toolchain = true;
        if (std.mem.endsWith(u8, root, "/toolchains")) has_toolchains = true;
    }
    try std.testing.expect(has_dot_toolchain);
    try std.testing.expect(has_toolchains);
}

test "pinned channel candidates are enumerated before generic local candidates" {
    const roots = try resolver.iterZigSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);
    const candidates = try resolver.iterRepoLocalZigCandidates(
        std.testing.io,
        std.testing.allocator,
        ".",
        "0.17.0-dev.1415+64dfaa568",
    );
    defer {
        for (candidates) |candidate| std.testing.allocator.free(candidate);
        std.testing.allocator.free(candidates);
    }
    try std.testing.expect(candidates.len > 0);
    const pinned_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "zig-{s}-0.17.0-dev.1415+64dfaa568",
        .{resolver.hostArchiveTarget().?},
    );
    defer std.testing.allocator.free(pinned_marker);
    try std.testing.expect(std.mem.indexOf(u8, candidates[0], pinned_marker) != null);
}
