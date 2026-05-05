const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

test "phase 7 string helper boundary keeps sample root free of string samples" {
    const io = std.testing.io;
    try std.testing.expectError(error.FileNotFound, std.Io.Dir.cwd().access(io, "samples/zigux/string_helpers_sample.zig", .{}));

    var dir = try std.Io.Dir.cwd().openDir(io, "samples/zigux", .{ .iterate = true });
    defer dir.close(io);

    var saw_string_file = false;
    var iterator = dir.iterate();
    while (try iterator.next(io)) |entry| {
        if (entry.kind != .file) continue;
        if (!std.mem.endsWith(u8, entry.name, ".zig")) continue;
        if (std.mem.indexOf(u8, entry.name, "string") != null) {
            saw_string_file = true;
            break;
        }
    }

    try std.testing.expect(!saw_string_file);
}

test "phase 7 sample root notes keep the no-string-sample boundary explicit" {
    const allocator = std.testing.allocator;
    const readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(readme);

    try expectContains(readme, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;");
    try expectContains(readme, "treat any new `samples/zigux/*string*.zig` file as review-blocking");
    try expectContains(readme, "Documentation/zigux/phase7-string-helpers-slice.md");
    try expectContains(readme, "lib/string_helpers.zig");
    try expectContains(readme, "zigux/tests/phase7_build.zig");
}

test "phase 7 helper packet keeps the dedicated sample-boundary guard wired" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(slice_note, "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.");
    try expectContains(slice_note, "no `samples/zigux/*string*` Phase 5 reference sample is expected here;");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(build_file, "\"phase7-string-helpers-sample-boundary-tests\"");
    try expectContains(build_file, "setCwd(b.path(\"../..\"))");
    try expectNotContains(build_file, "\"phase7_string_helpers_sample.zig\"");
    try expectNotContains(build_file, "\"phase7-string-helpers-sample-tests\"");
}
