const std = @import("std");
const testing = std.testing;

const closure_sysfs_marker =
    "`PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`";

const manifest_sysfs_packet = .{
    .anchors = [_][]const u8{
        "test \\\"sysfsStreq treats trailing newline and NUL as equivalent\\\"",
        "test \\\"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\\\"",
        "test \\\"sysfsMatchString finds newline-aware matches and preserves first-match order\\\"",
        "test \\\"sysfs_match_string mirrors sysfsMatchString for empty and matched lists\\\"",
    },
    .summary = "helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface",
};

const lane_sysfs_markers = .{
    .direct_owner = "`PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
    .next_safe_step = "`PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
};

const checker_sysfs_markers = .{
    .source_symbols = [_][]const u8{
        "\"pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {\"",
        "\"pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {\"",
        "\"pub fn __sysfs_match_string(haystack: []const []const u8, count: usize, needle: []const u8) ?usize {\"",
        "\"pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {\"",
        "\"pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {\"",
    },
    .packet_key = "\"sysfs_review_anchors\": [",
    .summary_key = "\"sysfs_review_summary\":",
    .fixture_gap = "shared Phase 1 replay still carries no dedicated sysfs fixture keys",
};

const helper_sysfs_symbols = [_][]const u8{
    "pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn __sysfs_match_string(haystack: []const []const u8, count: usize, needle: []const u8) ?usize {",
    "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
};

const helper_sysfs_test_anchors = [_][]const u8{
    "test \"sysfsStreq treats trailing newline and NUL as equivalent\"",
    "test \"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\"",
    "test \"sysfsMatchString finds newline-aware matches and preserves first-match order\"",
    "test \"sysfs_match_string mirrors sysfsMatchString for empty and matched lists\"",
};

const stale_sysfs_interpretations = [_][]const u8{
    "shared fixture owns sysfs",
    "validator-owned sysfs requirement",
    "PHASE1_STRING_SYSFS_REVIEW=missing_current_master",
    "dedicated shared sysfs fixture keys land",
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

test "closure note keeps string sysfs review helper-local" {
    const closure_note = try readRepoFile(
        testing.allocator,
        "Documentation/zigux/phase1-closure.md",
    );
    defer testing.allocator.free(closure_note);

    try expectOnce(closure_note, closure_sysfs_marker);
    try expectOnce(closure_sysfs_marker, "helper-local string sysfs newline-aware equality");
    try expectOnce(closure_sysfs_marker, "lookup-order anchors");
    try expectOnce(closure_sysfs_marker, "direct string tests");
    try expectOnce(closure_sysfs_marker, "Phase 1 helper manifest");
    try expectOnce(closure_sysfs_marker, "no dedicated sysfs fixture keys");
}

test "helper manifest carries the exact sysfs anchor packet" {
    const helper_manifest = try readRepoFile(
        testing.allocator,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
    );
    defer testing.allocator.free(helper_manifest);

    try testing.expectEqual(@as(usize, 4), manifest_sysfs_packet.anchors.len);
    for (manifest_sysfs_packet.anchors) |anchor| {
        try expectContains(helper_manifest, anchor);
        try expectOnce(anchor, "test \\\"");
    }
    try expectOnce(helper_manifest, manifest_sysfs_packet.summary);
    try expectOnce(manifest_sysfs_packet.summary, "sysfsStreq");
    try expectOnce(manifest_sysfs_packet.summary, "sysfs_streq");
    try expectOnce(manifest_sysfs_packet.summary, "sysfsMatchString");
    try expectOnce(manifest_sysfs_packet.summary, "sysfs_match_string");
}

test "string review checker owns the sysfs marker packet" {
    const checker = try readRepoFile(
        testing.allocator,
        "scripts/zigux/check-phase1-string-review-packet.py",
    );
    defer testing.allocator.free(checker);

    try expectOnce(checker, checker_sysfs_markers.packet_key);
    try expectOnce(checker, checker_sysfs_markers.summary_key);
    try expectOnce(checker, manifest_sysfs_packet.summary);
    try expectOnce(checker, checker_sysfs_markers.fixture_gap);
    for (checker_sysfs_markers.source_symbols) |symbol| {
        try expectOnce(checker, symbol);
    }
    for (helper_sysfs_test_anchors) |anchor| {
        try expectContains(checker, anchor);
    }
}

test "string helper exposes the sysfs functions guarded by the packet" {
    const string_helper = try readRepoFile(
        testing.allocator,
        "tools/lib/string.zig",
    );
    defer testing.allocator.free(string_helper);

    for (helper_sysfs_symbols) |symbol| {
        try expectOnce(string_helper, symbol);
    }
    for (helper_sysfs_test_anchors) |anchor| {
        try expectContains(string_helper, anchor);
    }
    try expectOnce(string_helper, "return __sysfs_match_string(haystack, haystack.len, needle);");
    try expectOnce(string_helper, "return sysfsMatchString(haystack, needle);");
}

test "lane sequencing keeps sysfs inside the string-only owner map" {
    const lane_note = try readRepoFile(
        testing.allocator,
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    );
    defer testing.allocator.free(lane_note);

    try expectOnce(lane_note, lane_sysfs_markers.direct_owner);
    try expectOnce(lane_note, lane_sysfs_markers.next_safe_step);
    try expectOnce(lane_sysfs_markers.direct_owner, "sysfs newline-aware equality and lookup order");
    try expectOnce(lane_sysfs_markers.next_safe_step, "keep the helper-local sysfs review anchors aligned");
    try expectOnce(lane_sysfs_markers.next_safe_step, "unless dedicated shared sysfs fixture keys land");
    try expectOnce(lane_sysfs_markers.next_safe_step, "do not reopen missing closure-side validator names by default");
}

test "stale shared-fixture or validator ownership stays outside sysfs review" {
    for (stale_sysfs_interpretations) |marker| {
        try expectAbsent(closure_sysfs_marker, marker);
        try expectAbsent(manifest_sysfs_packet.summary, marker);
        try expectAbsent(lane_sysfs_markers.direct_owner, marker);
    }
    try testing.expect(std.mem.indexOf(u8, lane_sysfs_markers.next_safe_step, "dedicated shared sysfs fixture keys land") != null);
    try testing.expect(std.mem.indexOf(u8, closure_sysfs_marker, "validator-owned") == null);
    try testing.expect(std.mem.indexOf(u8, manifest_sysfs_packet.summary, "shared fixture owns") == null);
}
