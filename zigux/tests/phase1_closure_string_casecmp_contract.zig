const std = @import("std");
const testing = std.testing;

const casecmp_packet = .{
    .source_symbols = [_][]const u8{
        "pub fn strcasecmp(lhs: []const u8, rhs: []const u8) i32 {",
        "pub fn strncasecmp(lhs: []const u8, rhs: []const u8, count: usize) i32 {",
    },
    .source_test_anchors = [_][]const u8{
        "test \"strcasecmp ignores ASCII case and preserves lexical ordering\"",
        "test \"strcasecmp stops at embedded NULs and length mismatches\"",
        "test \"strncasecmp honors the count limit before later mismatches\"",
        "test \"strncasecmp stops at embedded NULs and shorter prefixes\"",
    },
    .manifest_test_anchors = [_][]const u8{
        "test \\\"strcasecmp ignores ASCII case and preserves lexical ordering\\\"",
        "test \\\"strcasecmp stops at embedded NULs and length mismatches\\\"",
        "test \\\"strncasecmp honors the count limit before later mismatches\\\"",
        "test \\\"strncasecmp stops at embedded NULs and shorter prefixes\\\"",
    },
    .manifest_key = "\"casecmp_review_anchors\"",
    .manifest_summary_key = "\"casecmp_review_summary\"",
    .summary = "helper-local ASCII case-folded compare anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strcasecmp() or strncasecmp() fixture keys, so case-insensitive lexical ordering, embedded-NUL boundaries, and counted-prefix behavior remain review-visible at the helper surface",
};

const closure_review_guard =
    "`PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py exact-checks helper-local string anchors plus the committed replaceChar and current string fixture packet across the helper, closure note, lane note, manifest, and fixture`";

const lane_casecmp_marker =
    "keep the helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review anchors aligned across the string review packet and this lane note unless dedicated shared fixture keys land";

const stale_casecmp_owners = [_][]const u8{
    "shared fixture owns strcasecmp",
    "shared fixture owns strncasecmp",
    "validator-owned case-insensitive compare",
    "PHASE1_STRING_CASECMP_REVIEW=missing_current_master",
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

test "closure note keeps string review guard as the casecmp carrier" {
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

test "manifest carries the exact case-insensitive compare review packet" {
    const helper_manifest = try readRepoFile(
        testing.allocator,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
    );
    defer testing.allocator.free(helper_manifest);

    try expectOnce(helper_manifest, casecmp_packet.manifest_key);
    try expectOnce(helper_manifest, casecmp_packet.manifest_summary_key);
    for (casecmp_packet.manifest_test_anchors) |anchor| {
        try expectContains(helper_manifest, anchor);
        try expectOnce(anchor, "test \\\"");
    }
    try expectOnce(helper_manifest, casecmp_packet.summary);
    try expectOnce(casecmp_packet.summary, "strcasecmp()");
    try expectOnce(casecmp_packet.summary, "strncasecmp()");
    try expectOnce(casecmp_packet.summary, "case-insensitive lexical ordering");
    try expectOnce(casecmp_packet.summary, "counted-prefix behavior");
}

test "string checker and helper source keep casecmp exact-checkable" {
    const checker = try readRepoFile(
        testing.allocator,
        "scripts/zigux/check-phase1-string-review-packet.py",
    );
    defer testing.allocator.free(checker);
    const helper = try readRepoFile(testing.allocator, "tools/lib/string.zig");
    defer testing.allocator.free(helper);

    try expectOnce(checker, casecmp_packet.manifest_key);
    try expectOnce(checker, casecmp_packet.manifest_summary_key);
    try expectOnce(checker, casecmp_packet.summary);
    for (casecmp_packet.source_symbols) |symbol| {
        try expectOnce(checker, symbol);
        try expectOnce(helper, symbol);
    }
    for (casecmp_packet.source_test_anchors) |anchor| {
        try expectOnce(checker, anchor);
        try expectOnce(helper, anchor);
    }
}

test "lane note keeps casecmp in the string-only next-safe-step packet" {
    const lane_note = try readRepoFile(
        testing.allocator,
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    );
    defer testing.allocator.free(lane_note);

    try expectOnce(lane_note, lane_casecmp_marker);
    try expectOnce(lane_casecmp_marker, "case-insensitive compare");
    try expectOnce(lane_casecmp_marker, "string review packet");
    try expectOnce(lane_casecmp_marker, "unless dedicated shared fixture keys land");
}

test "stale shared-fixture or validator ownership stays outside casecmp review" {
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
    const lane_note = try readRepoFile(
        testing.allocator,
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    );
    defer testing.allocator.free(lane_note);

    for (stale_casecmp_owners) |marker| {
        try expectAbsent(closure_note, marker);
        try expectAbsent(helper_manifest, marker);
        try expectAbsent(lane_note, marker);
        try expectAbsent(casecmp_packet.summary, marker);
    }
}
