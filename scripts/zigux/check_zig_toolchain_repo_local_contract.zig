const std = @import("std");
const resolver = @import("toolchain_resolver.zig");

test "repo local zig search roots include workspace and parent fallbacks" {
    const roots = try resolver.iterZigSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);

    var seen_dot = false;
    var seen_toolchains = false;
    var seen_hidden = false;
    for (roots) |root| {
        if (std.mem.endsWith(u8, root, "/.zig-toolchain")) seen_dot = true;
        if (std.mem.endsWith(u8, root, "/toolchains")) seen_toolchains = true;
        if (std.mem.endsWith(u8, root, "/.toolchains")) seen_hidden = true;
    }
    try std.testing.expect(seen_dot);
    try std.testing.expect(seen_toolchains);
    try std.testing.expect(seen_hidden);
}

test "pinned channel candidate search is preferred before generic repo local zig" {
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
    try std.testing.expect(candidates.len >= 2);
    try std.testing.expect(std.mem.endsWith(u8, candidates[0], "/zig") or std.mem.endsWith(u8, candidates[0], "/bin/zig"));
}

test "missing zig diagnostic names both PATH and repo local roots" {
    const roots = try resolver.iterZigSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);
    const diagnostic = try resolver.describeMissingZig(
        std.testing.allocator,
        "0.17.0-dev.877+a3ae499dc",
        roots,
    );
    defer resolver.freeMissingZigDiagnostic(std.testing.allocator, diagnostic);
    try std.testing.expect(std.mem.indexOf(u8, diagnostic.message, "repo-local toolchain search roots") != null);
    try std.testing.expect(std.mem.indexOf(u8, diagnostic.message, "0.17.0-dev.877+a3ae499dc") != null);
    try std.testing.expect(diagnostic.search_roots_summary.len > 0);
}