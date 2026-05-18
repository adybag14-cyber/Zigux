const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn isStandaloneCmdlineSample(name: []const u8) bool {
    if (!std.mem.endsWith(u8, name, ".zig")) return false;
    return std.mem.indexOf(u8, name, "cmdline") != null;
}

test "phase 7 cmdline boundary keeps the no-standalone-cmdline-sample policy helper-local" {
    const io = std.testing.io;
    try std.testing.expectError(error.FileNotFound, std.Io.Dir.cwd().access(io, "samples/zigux/cmdline_sample.zig", .{}));

    var dir = try std.Io.Dir.cwd().openDir(io, "samples/zigux", .{ .iterate = true });
    defer dir.close(io);

    var saw_cmdline_file = false;
    var total_zig_files: usize = 0;

    var iterator = dir.iterate();
    while (try iterator.next(io)) |entry| {
        if (entry.kind != .file) continue;
        if (!std.mem.endsWith(u8, entry.name, ".zig")) continue;

        total_zig_files += 1;
        if (isStandaloneCmdlineSample(entry.name)) saw_cmdline_file = true;
    }

    try std.testing.expect(!saw_cmdline_file);
    try std.testing.expect(total_zig_files >= 1);
}

test "phase 7 cmdline boundary stays rooted in the helper-local packet" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-cmdline-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "no-standalone-cmdline-sample boundary");
    try expectContains(slice_note, "`samples/zigux/README.md`");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_cmdline_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"samples/zigux/README.md\"");

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);
    try expectContains(samples_readme, "* `*cmdline*`");
}
