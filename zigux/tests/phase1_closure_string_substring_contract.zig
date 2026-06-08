const std = @import("std");
const testing = std.testing;

const substring_packet = .{
    .source_symbols = [_][]const u8{
        "pub fn strstr(buf: []const u8, needle: []const u8) ?usize {",
        "pub fn strnstr(buf: []const u8, needle: []const u8, count: usize) ?usize {",
    },
    .source_test_anchors = [_][]const u8{
        "test \"strstr mirrors full-length C-string substring searches\"",
        "test \"strnstr honors count and C-string boundaries\"",
    },
    .manifest_test_anchors = [_][]const u8{
        "test \\\"strstr mirrors full-length C-string substring searches\\\"",
        "test \\\"strnstr honors count and C-string boundaries\\\"",
    },
    .manifest_key = "\"substring_search_review_anchors\"",
    .manifest_summary_key = "\"substring_search_review_summary\"",
    .summary = "helper-local substring-search anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strstr() or strnstr() fixture keys, so full-length and count-clamped substring boundaries remain review-visible at the helper surface",
};

const closure_review_guard =
    "`PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py exact-checks helper-local string anchors plus the committed replaceChar and current string fixture packet across the helper, closure note, lane note, manifest, and fixture`";

const stale_substring_owners = [_][]const u8{
    "shared fixture owns strstr",
    "shared fixture owns strnstr",
    "validator-owned substring search",
    "PHASE1_STRING_SUBSTRING_REVIEW=missing_current_master",
};

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    try testing.expectEqual(@as(usize, 1), countNeedle(haystack, needle));
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expectEqual(@as(usize, 0), countNeedle(haystack, needle));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

test "closure note keeps string review guard as the substring carrier" {
    const closure_note = try readRepoFile(
        testing.allocator,
        "Documentation/zigux/phase1-closure.md",
    );
    defer testing.allocator.free(closure_note);

    try expectOnce(closure_note, closure_review_guard);
    try expectOnce(closure_review_guard, "check-phase1-string-review-packet.py");
    try expectOnce(closure_review_guard, "helper-local string anchors");
    try expectOnce(closure_review_guard, "manifest");
    try expectContains(closure_review_guard, "fixture");
}

test "manifest carries the exact substring-search review packet" {
    const helper_manifest = try readRepoFile(
        testing.allocator,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
    );
    defer testing.allocator.free(helper_manifest);

    try expectOnce(helper_manifest, substring_packet.manifest_key);
    try expectOnce(helper_manifest, substring_packet.manifest_summary_key);
    for (substring_packet.manifest_test_anchors) |anchor| {
        try expectContains(helper_manifest, anchor);
    }
    try expectOnce(helper_manifest, substring_packet.summary);
    try expectOnce(substring_packet.summary, "strstr()");
    try expectOnce(substring_packet.summary, "strnstr()");
    try expectOnce(substring_packet.summary, "full-length");
    try expectOnce(substring_packet.summary, "count-clamped substring boundaries");
}

test "string checker and helper source keep substring search exact-checkable" {
    const checker = try readRepoFile(
        testing.allocator,
        "scripts/zigux/check-phase1-string-review-packet.py",
    );
    defer testing.allocator.free(checker);
    const helper = try readRepoFile(testing.allocator, "tools/lib/string.zig");
    defer testing.allocator.free(helper);

    try expectOnce(checker, substring_packet.manifest_key);
    try expectOnce(checker, substring_packet.manifest_summary_key);
    try expectOnce(checker, substring_packet.summary);
    for (substring_packet.source_symbols) |symbol| {
        try expectOnce(checker, symbol);
        try expectOnce(helper, symbol);
    }
    for (substring_packet.source_test_anchors) |anchor| {
        try expectOnce(checker, anchor);
        try expectOnce(helper, anchor);
    }
}

test "substring search remains helper-local rather than shared-fixture owned" {
    const closure_note = try readRepoFile(
        testing.allocator,
        "Documentation/zigux/phase1-closure.md",
    );
    defer testing.allocator.free(closure_note);
    const helper_manifest = try readRepoFile(
        testing.allocator,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
    );
    defer testing.allocator.free(helper_manifest);
    const checker = try readRepoFile(
        testing.allocator,
        "scripts/zigux/check-phase1-string-review-packet.py",
    );
    defer testing.allocator.free(checker);

    for (stale_substring_owners) |marker| {
        try expectAbsent(closure_note, marker);
        try expectAbsent(helper_manifest, marker);
        try expectAbsent(checker, marker);
        try expectAbsent(substring_packet.summary, marker);
    }
}
