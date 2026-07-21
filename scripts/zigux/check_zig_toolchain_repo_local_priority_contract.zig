const std = @import("std");
const resolver = @import("toolchain_resolver.zig");

test "repo-local search roots include pinned and adjacent toolchain directories" {
    const roots = try resolver.iterZigSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);
    try std.testing.expect(roots.len >= 3);
    try std.testing.expect(std.mem.endsWith(u8, roots[0], "/.zig-toolchain"));
}

test "pinned channel candidates are enumerated before generic local candidates" {
    const candidates = try resolver.iterRepoLocalZigCandidates(
        std.testing.io,
        std.testing.allocator,
        ".",
        "0.17.0-dev.1443+6c25d2bd5",
    );
    defer {
        for (candidates) |candidate| std.testing.allocator.free(candidate);
        std.testing.allocator.free(candidates);
    }

    const pinned_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "zig-{s}-0.17.0-dev.1443+6c25d2bd5",
        .{resolver.hostArchiveTarget().?},
    );
    defer std.testing.allocator.free(pinned_marker);
    var pinned_index: ?usize = null;
    var generic_index: ?usize = null;
    for (candidates, 0..) |candidate, index| {
        if (std.mem.indexOf(u8, candidate, pinned_marker) != null) pinned_index = index;
        if (std.mem.endsWith(u8, candidate, "/.zig-toolchain/zig")) generic_index = index;
    }
    try std.testing.expect(pinned_index != null);
    if (generic_index) |generic| {
        try std.testing.expect(pinned_index.? < generic);
    }
}

test "explicit zig path stays ahead of repo-local resolution" {
    const explicit = resolver.resolveZigExecutable(
        std.testing.io,
        std.testing.allocator,
        ".",
        "missing-explicit-zig",
        "0.17.0-dev.1443+6c25d2bd5",
    );
    try std.testing.expectError(resolver.ResolverError.InvalidArgument, explicit);
}
