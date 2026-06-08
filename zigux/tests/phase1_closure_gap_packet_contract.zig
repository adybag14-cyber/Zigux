const std = @import("std");

const gap_packet_marker =
    "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`";

const gap_paths = [_][]const u8{
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
};

const tests_readme_gap_paths = [_][]const u8{
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/phase1_helpers_c_harness.c",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative_index| {
        count += 1;
        offset += relative_index + needle.len;
    }
    return count;
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn requiredFilesBlock(validator: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, validator, "REQUIRED_FILES = (") orelse return error.MissingRequiredFilesStart;
    const rel_start = validator[start..];
    const end_rel = std.mem.indexOf(u8, rel_start, ")\n\nEXPECTED_HELPERS") orelse return error.MissingRequiredFilesEnd;
    return rel_start[0..end_rel];
}

test "phase 1 closure note keeps broader companions parked in the gap packet" {
    const closure_note = try readRepoFile("Documentation/zigux/phase1-closure.md", 512 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Current Reminder Packet");
    try expectContains(closure_note, "## Broader Closure Companions");
    try expectContains(closure_note, "## Closure Validation");
    try expectBefore(closure_note, "## Current Reminder Packet", "## Broader Closure Companions");
    try expectBefore(closure_note, "## Broader Closure Companions", "## Closure Validation");
    try expectOnce(closure_note, gap_packet_marker);
    try expectContains(closure_note, "broader closure-stack references rather than active current reminder-packet proof");
    try expectContains(closure_note, "parked as historical closure-stack vocabulary until direct current-master rereads restore them");

    inline for (gap_paths) |path| {
        try expectContains(closure_note, path);
    }
}

test "tests root mirrors the gap packet as broader companions outside active proof" {
    const tests_readme = try readRepoFile("zigux/tests/README.md", 512 * 1024);
    defer std.testing.allocator.free(tests_readme);

    try expectContains(tests_readme, "current direct-readback Phase 1 reminder packet");
    try expectContains(tests_readme, "broader Phase 1 closure companions stay outside the narrow direct-readback packet");
    try expectContains(tests_readme, "keep those paths framed as broader closure companions rather than as active tests-root proof");
    try expectContains(tests_readme, "keep the Phase 1 tests-root reminder truthful");
    try expectBefore(tests_readme, "current direct-readback Phase 1 reminder packet", "broader Phase 1 closure companions stay outside");

    inline for (tests_readme_gap_paths) |path| {
        try expectContains(tests_readme, path);
    }
}

test "closure validator owns the same gap vocabulary without requiring broader files" {
    const validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 1024 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "\"gap_packet\":");
    try expectContains(validator, gap_packet_marker);

    const required_files = try requiredFilesBlock(validator);
    inline for (gap_paths) |path| {
        try expectAbsent(required_files, path);
    }

    try expectContains(required_files, "PHASE1_CLOSURE_REL");
    try expectContains(required_files, "DOCS_ROOT_REL");
    try expectContains(required_files, "TESTS_README_REL");
    try expectContains(required_files, "MANIFEST_REL");
}
