const std = @import("std");
const testing = std.testing;

const note_path = "Documentation/zigux/phase3-docs-root-helper-slice-index.md";

fn expectContains(note: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, note, needle) != null);
}

test "docs-root Phase 3 helper slice index names bitmap/cpumask and list/hlist slices" {
    const note = try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        note_path,
        testing.allocator,
        .limited(64 * 1024),
    );
    defer testing.allocator.free(note);

    try expectContains(note, "Backup audit B correction");
    try expectContains(note, "docs-root Phase 3 reminder index");
    try expectContains(note, "Documentation/zigux/phase3-bitmap-cpumask-slice.md");
    try expectContains(note, "Documentation/zigux/phase3-list-hlist-slice.md");
}

test "docs-root Phase 3 helper slice correction stays bounded" {
    const note = try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        note_path,
        testing.allocator,
        .limited(64 * 1024),
    );
    defer testing.allocator.free(note);

    try expectContains(note, "This correction is an index and reminder truthfulness fix.");
    try expectContains(note, "does not widen Phase 3 into broader shared replay");
    try expectContains(note, "broader header-family completion");
    try expectContains(note, "full interop parity claims");
}
