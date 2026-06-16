const std = @import("std");
const resolver = @import("toolchain_resolver.zig");

test "explicit archive directory paths are invalid before missing handling" {
    const io = std.testing.io;
    const note = try resolver.describeInvalidExplicitArchivePath(io, std.testing.allocator, ".");
    defer if (note) |text| std.testing.allocator.free(text);
    try std.testing.expect(note != null);
    try std.testing.expect(std.mem.indexOf(u8, note.?, "directory") != null);
}

test "missing explicit archive keeps separate diagnostic from search-root misses" {
    const roots = try resolver.iterArchiveSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);
    const diagnostic = try resolver.describeMissingArchive(
        std.testing.allocator,
        null,
        "third_party/missing.tar.xz",
        roots,
    );
    defer resolver.freeMissingArchiveDiagnostic(std.testing.allocator, diagnostic);
    try std.testing.expect(std.mem.indexOf(u8, diagnostic.message, "explicit archive path does not exist") != null);
    try std.testing.expect(diagnostic.search_roots_summary == null);
}

test "missing search-root archive reports archive search roots" {
    const roots = try resolver.iterArchiveSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);
    const diagnostic = try resolver.describeMissingArchive(
        std.testing.allocator,
        null,
        null,
        roots,
    );
    defer resolver.freeMissingArchiveDiagnostic(std.testing.allocator, diagnostic);
    try std.testing.expectEqualStrings(
        "pinned Zig archive not found in archive search roots",
        diagnostic.message,
    );
    try std.testing.expect(diagnostic.search_roots_summary != null);
}