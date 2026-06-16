const std = @import("std");
const resolver = @import("toolchain_resolver.zig");

test "explicit zig path stays first resolver priority" {
    const result = resolver.resolveZigExecutable(
        std.testing.io,
        std.testing.allocator,
        ".",
        "missing-explicit-zig",
        null,
    );
    try std.testing.expectError(resolver.ResolverError.InvalidArgument, result);
}

test "pinned repo local layouts stay before PATH fallback" {
    const candidates = try resolver.iterRepoLocalZigCandidates(
        std.testing.io,
        std.testing.allocator,
        ".",
        "0.17.0-dev.877+a3ae499dc",
    );
    defer {
        for (candidates) |candidate| std.testing.allocator.free(candidate);
        std.testing.allocator.free(candidates);
    }
    try std.testing.expect(candidates.len > 0);
    try std.testing.expect(std.mem.indexOf(u8, candidates[0], "0.17.0-dev.877+a3ae499dc") != null);
}

test "missing zig diagnostic names both PATH and repo local roots" {
    const roots = try resolver.iterZigSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);
    const diagnostic = try resolver.describeMissingZig(std.testing.allocator, null, roots);
    defer resolver.freeMissingZigDiagnostic(std.testing.allocator, diagnostic);
    try std.testing.expectEqualStrings(
        "zig not found on PATH or in repo-local toolchain search roots",
        diagnostic.message,
    );
    try std.testing.expect(diagnostic.search_roots_summary.len > 0);
}