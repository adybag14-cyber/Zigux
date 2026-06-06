const std = @import("std");
const testing = std.testing;

const closure_string_review_carrier =
    "`PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py exact-checks helper-local string anchors plus the committed replaceChar and current string fixture packet across the helper, closure note, lane note, manifest, and fixture`";

const checker_strlcat_packet = .{
    .packet_key = "\"strlcat_review_anchors\": [",
    .summary_key = "\"strlcat_review_summary\":",
    .anchors = [_][]const u8{
        "test \"strlcat appends within the destination size and reports the attempted length\"",
        "test \"strlcat truncates with a terminator and keeps the full attempted length\"",
        "test \"strlcat treats an unterminated destination as full\"",
        "test \"strlcat handles a zero-length destination buffer\"",
    },
    .source_equivalent = "test \"strlcat appends only the C-string prefix from embedded-NUL sources\"",
    .summary = "helper-local strlcat truncation and destination-boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strlcat() fixture keys, so append length reporting, truncation with a preserved terminator slot, unterminated-destination handling, and zero-length destination behavior remain review-visible at the helper surface",
};

const helper_strlcat_symbols = .{
    .entry = "pub fn strlcat(dest: []u8, src: []const u8) usize {",
    .source_len = "const src_len = cStringLen(src);",
    .dest_len = "const dest_len = strnlen(dest, dest.len);",
    .full_dest = "return dest.len + src_len;",
    .attempted_len = "return dest_len + src_len;",
};

const lane_strlcat_marker =
    "current `master` keeps string parked on helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review-anchor alignment across the live string review packet and this lane note";

const manifest_strlcat_summary =
    "\"strlcat_review_summary\": \"helper-local strlcat truncation and destination-boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strlcat() fixture keys, so append length reporting, truncation with a preserved terminator slot, unterminated-destination handling, and zero-length destination behavior remain review-visible at the helper surface\"";

const manifest_strlcat_anchors = [_][]const u8{
    "test \\\"strlcat appends within the destination size and reports the attempted length\\\"",
    "test \\\"strlcat truncates with a terminator and keeps the full attempted length\\\"",
    "test \\\"strlcat treats an unterminated destination as full\\\"",
    "test \\\"strlcat handles a zero-length destination buffer\\\"",
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

fn expectAtLeastOnce(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(countNeedle(haystack, needle) >= 1);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expectEqual(@as(usize, 0), countNeedle(haystack, needle));
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(768 * 1024));
}

test "closure note carries string review guard for strlcat packet" {
    const closure_note = try readRepoFile(
        testing.allocator,
        "Documentation/zigux/phase1-closure.md",
    );
    defer testing.allocator.free(closure_note);

    try expectOnce(closure_note, closure_string_review_carrier);
    try expectOnce(closure_string_review_carrier, "check-phase1-string-review-packet.py");
    try expectOnce(closure_string_review_carrier, "helper-local string anchors");
    try expectOnce(closure_string_review_carrier, "manifest");
    try expectAbsent(closure_string_review_carrier, "validator-owned strlcat");
    try expectAbsent(closure_string_review_carrier, "shared strlcat fixture keys landed");
}

test "string review checker keeps exact strlcat packet" {
    const checker = try readRepoFile(
        testing.allocator,
        "scripts/zigux/check-phase1-string-review-packet.py",
    );
    defer testing.allocator.free(checker);

    try expectOnce(checker, checker_strlcat_packet.packet_key);
    try expectOnce(checker, checker_strlcat_packet.summary_key);
    for (checker_strlcat_packet.anchors) |anchor| {
        try expectAtLeastOnce(checker, anchor);
    }
    try expectOnce(checker, checker_strlcat_packet.summary);
    try expectOnce(checker, "EXPECTED_HELPER_SOURCE_EQUIVALENT_ANCHORS");
    try expectOnce(checker, checker_strlcat_packet.source_equivalent);
}

test "helper manifest keeps strlcat helper-local review anchors" {
    const helper_manifest = try readRepoFile(
        testing.allocator,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
    );
    defer testing.allocator.free(helper_manifest);

    try expectOnce(helper_manifest, "\"strlcat_review_anchors\": [");
    for (manifest_strlcat_anchors) |anchor| {
        try expectOnce(helper_manifest, anchor);
    }
    try expectOnce(helper_manifest, manifest_strlcat_summary);
    try expectOnce(helper_manifest, "strlcat() fixture keys");
}

test "string helper exposes direct strlcat behavior anchors" {
    const string_helper = try readRepoFile(testing.allocator, "tools/lib/string.zig");
    defer testing.allocator.free(string_helper);

    try expectOnce(string_helper, helper_strlcat_symbols.entry);
    try expectOnce(string_helper, helper_strlcat_symbols.source_len);
    try expectOnce(string_helper, helper_strlcat_symbols.dest_len);
    try expectOnce(string_helper, helper_strlcat_symbols.full_dest);
    try expectOnce(string_helper, helper_strlcat_symbols.attempted_len);
    for (checker_strlcat_packet.anchors) |anchor| {
        try expectOnce(string_helper, anchor);
    }
    try expectOnce(string_helper, checker_strlcat_packet.source_equivalent);
}

test "lane note leaves strlcat parked until shared fixture keys land" {
    const lane_note = try readRepoFile(
        testing.allocator,
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    );
    defer testing.allocator.free(lane_note);

    try expectOnce(lane_note, lane_strlcat_marker);
    try expectOnce(lane_note, "helper-local strlcat");
    try expectOnce(lane_note, "live string review packet");
    try expectOnce(lane_note, "dedicated shared fixture keys land");
    try expectAbsent(lane_strlcat_marker, "missing closure-side validator names");
}
