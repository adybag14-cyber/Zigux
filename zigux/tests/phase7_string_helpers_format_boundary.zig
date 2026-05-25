const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn isBlockedBroadFormatSample(name: []const u8) bool {
    if (!std.mem.endsWith(u8, name, ".zig")) return false;
    if (std.mem.eql(u8, name, "trace_events_string_formatting_sample.zig")) return false;
    if (std.mem.indexOf(u8, name, "vsprintf") != null) return true;
    if (std.mem.indexOf(u8, name, "printf") != null) return true;
    if (std.mem.indexOf(u8, name, "format") != null) return true;
    return false;
}

test "phase 7 string helper format boundary keeps the trace-events formatting companion as the only sample-root exception" {
    const io = std.testing.io;
    try std.Io.Dir.cwd().access(io, "samples/zigux/trace_events_string_formatting_sample.zig", .{});

    var dir = try std.Io.Dir.cwd().openDir(io, "samples/zigux", .{ .iterate = true });
    defer dir.close(io);

    var blocked_format_file_found = false;
    var allowed_format_companion_count: usize = 0;

    var iterator = dir.iterate();
    while (try iterator.next(io)) |entry| {
        if (entry.kind != .file) continue;
        if (!std.mem.endsWith(u8, entry.name, ".zig")) continue;

        if (std.mem.eql(u8, entry.name, "trace_events_string_formatting_sample.zig")) {
            allowed_format_companion_count += 1;
            continue;
        }

        if (isBlockedBroadFormatSample(entry.name)) blocked_format_file_found = true;
    }

    try std.testing.expectEqual(@as(usize, 1), allowed_format_companion_count);
    try std.testing.expect(!blocked_format_file_found);
}

test "phase 7 string helper format boundary stays on sample-boundary review surfaces only" {
    const allocator = std.testing.allocator;
    const io = std.testing.io;

    try std.Io.Dir.cwd().access(io, "samples/zigux/README.md", .{});
    try std.Io.Dir.cwd().access(io, "Documentation/zigux/phase7-string-helpers-slice.md", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers_sample_boundary.zig", .{});

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);
    try expectContains(samples_readme, "Current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`");
    try expectContains(samples_readme, "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.");
    try expectContains(samples_readme, "* `*printf*`");
    try expectContains(samples_readme, "* `*vsprintf*`");

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "Current `master` still ships no standalone `samples/zigux/*string*` helper sample for this packet");
    try expectContains(slice_note, "but it does ship the bounded `samples/zigux/trace_events_string_formatting_sample.zig` companion plus the shared `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` reminder under the non-runtime `trace_events` anchor");

    const sample_boundary = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    defer allocator.free(sample_boundary);
    try expectContains(sample_boundary, "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.");
    try expectContains(sample_boundary, "* `*printf*`");
    try expectContains(sample_boundary, "* `*vsprintf*`");
}
