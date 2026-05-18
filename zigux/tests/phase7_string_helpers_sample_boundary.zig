const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn isStandaloneStringSample(name: []const u8) bool {
    if (!std.mem.endsWith(u8, name, ".zig")) return false;
    if (std.mem.eql(u8, name, "trace_events_string_formatting_sample.zig")) return false;
    if (std.mem.startsWith(u8, name, "string")) return true;
    if (std.mem.indexOf(u8, name, "string_helper") != null) return true;
    if (std.mem.indexOf(u8, name, "string_helpers") != null) return true;
    return false;
}

test "phase 7 string helper boundary keeps the no-string-sample policy lane-local" {
    const io = std.testing.io;
    try std.testing.expectError(error.FileNotFound, std.Io.Dir.cwd().access(io, "samples/zigux/string_helpers_sample.zig", .{}));

    var dir = try std.Io.Dir.cwd().openDir(io, "samples/zigux", .{ .iterate = true });
    defer dir.close(io);

    var saw_string_file = false;
    var total_zig_files: usize = 0;

    var iterator = dir.iterate();
    while (try iterator.next(io)) |entry| {
        if (entry.kind != .file) continue;
        if (!std.mem.endsWith(u8, entry.name, ".zig")) continue;

        total_zig_files += 1;
        if (isStandaloneStringSample(entry.name)) saw_string_file = true;
    }

    try std.testing.expect(!saw_string_file);
    try std.testing.expect(total_zig_files >= 1);
}

test "phase 7 string helper boundary stays on sample-boundary surfaces only" {
    const allocator = std.testing.allocator;
    const io = std.testing.io;

    try std.Io.Dir.cwd().access(io, "lib/string_helpers.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers_survey.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers_manifest.json", .{});
    try std.Io.Dir.cwd().access(io, "samples/zigux/README.md", .{});

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "expanded starter packet");
    try expectContains(slice_note, "Current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(slice_note, "bounded parse-int-array decoding for comma-separated lists, positive ranges, first-NUL and explicit-count limits, trailing-invalid-token stop behavior, and clean allocation-failure replay");
    try expectContains(slice_note, "The next bounded follow-through should realign the dedicated survey and sample-boundary replays so they treat `parse_int_array()` as landed");
    try expectNotContains(slice_note, "`parse_int_array()` can join the same helper-local packet");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub fn parseIntArray");
    try expectContains(helper, "pub fn parse_int_array");
    try expectContains(helper, "pub fn kstrdupQuotableCmdline");
    try expectContains(helper, "pub fn memcpyAndPad");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter parses bounded comma lists and positive ranges");
    try expectContains(helper_tests, "phase 7 string helpers starter stops at invalid trailing tokens while respecting count and first NUL");
    try expectContains(helper_tests, "phase 7 string helpers starter reports NoEntry when no integers are available");
    try expectContains(helper_tests, "phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators");
    try expectContains(helper_tests, "phase 7 string helpers starter pads bounded copies without reading past the provided source slice");

    const survey = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_survey.zig");
    defer allocator.free(survey);
    try expectContains(survey, "phase 7 string helpers survey keeps the helper-local packet truthful");
    try expectContains(survey, "bounded parse-int-array helper pair");
    try expectContains(survey, "Sync `zigux/tests/phase7_string_helpers_survey.zig` and `zigux/tests/phase7_string_helpers_sample_boundary.zig`");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"current_master_state\": \"expanded_starter_packet\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(manifest, "\"parseIntArray\"");
    try expectContains(manifest, "\"parse_int_array\"");
    try expectContains(manifest, "bounded parse-int-array helper pair");
    try expectContains(manifest, "Sync `zigux/tests/phase7_string_helpers_survey.zig` and `zigux/tests/phase7_string_helpers_sample_boundary.zig`");
    try expectNotContains(manifest, "`parse_int_array()` belongs in the same helper-local packet");

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);
    try expectContains(samples_readme, "Current `master` still ships no standalone Phase 5 sample-root files here for:");
    try expectContains(samples_readme, "* `*string*`");
    try expectContains(samples_readme, "* `*cmdline*`");
    try expectContains(samples_readme, "* `*argv*`");
    try expectContains(samples_readme, "* `*rbtree*`");
}
