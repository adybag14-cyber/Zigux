const std = @import("std");
const resolver = @import("toolchain_resolver.zig");

test "toolchain checker keeps repo-local zig search roots ahead of PATH fallback" {
    const roots = try resolver.iterZigSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);

    try std.testing.expect(roots.len >= 3);
    try std.testing.expect(std.mem.endsWith(u8, roots[0], "/.zig-toolchain"));
    try std.testing.expect(std.mem.endsWith(u8, roots[1], "/toolchains"));
    try std.testing.expect(std.mem.endsWith(u8, roots[2], "/.toolchains"));

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
}

test "toolchain checker keeps current pinned archive search roots explicit" {
    const roots = try resolver.iterArchiveSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);

    var third_party_index: ?usize = null;
    var agent_files_index: ?usize = null;
    var dot_toolchain_index: ?usize = null;
    for (roots, 0..) |root, index| {
        if (std.mem.endsWith(u8, root, "/.zig-toolchain")) dot_toolchain_index = index;
        if (std.mem.endsWith(u8, root, "/third_party")) third_party_index = index;
        if (std.mem.endsWith(u8, root, "/agent_files")) agent_files_index = index;
    }
    try std.testing.expect(dot_toolchain_index != null);
    try std.testing.expect(third_party_index != null);
    try std.testing.expect(agent_files_index != null);
    try std.testing.expect(dot_toolchain_index.? < third_party_index.?);
    try std.testing.expect(third_party_index.? < agent_files_index.?);
}

test "toolchain checker keeps archive-only reporting separate from executable probing" {
    const policy = @import("toolchain_policy.zig");
    const checker = @import("check_zig_toolchain.zig");

    const default_archive_options = checker.ArchiveOnlyOptions{};
    const default_zig_options = checker.ZigCheckOptions{};
    try std.testing.expect(!default_archive_options.allow_missing);
    try std.testing.expect(!default_zig_options.allow_missing);

    const archive_roots = try resolver.iterArchiveSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, archive_roots);
    const missing_archive = try resolver.describeMissingArchive(
        std.testing.allocator,
        null,
        null,
        archive_roots,
    );
    defer resolver.freeMissingArchiveDiagnostic(std.testing.allocator, missing_archive);
    try std.testing.expect(std.mem.indexOf(u8, missing_archive.message, "archive search roots") != null);

    const missing_zig_roots = try resolver.iterZigSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, missing_zig_roots);
    const missing_zig = try resolver.describeMissingZig(std.testing.allocator, null, missing_zig_roots);
    defer resolver.freeMissingZigDiagnostic(std.testing.allocator, missing_zig);
    try std.testing.expect(std.mem.indexOf(u8, missing_zig.message, "repo-local toolchain search roots") != null);
    _ = policy.ToolchainStatus;
}