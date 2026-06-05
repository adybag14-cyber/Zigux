const std = @import("std");

const closure_note_path = "Documentation/zigux/phase1-closure.md";
const helper_path = "tools/lib/find_bit.zig";
const manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative_index| {
        count += 1;
        cursor += relative_index + needle.len;
    }
    return count;
}

test "closure note keeps find_bit review guard and tie-breaker scoped" {
    const closure = try readRepoFile(closure_note_path, 128 * 1024);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`");
    try expectContains(closure, "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route");
    try expectContains(closure, "same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors");
    try expectContains(closure, "tail-clamped or tail-inclusive-boundary replay fields");
    try expectContains(closure, "clump8 past-end scans return without reading bitmap words");
    try expectContains(closure, "including andnot");
    try expectContains(closure, "single-word tail windows keep the last in-range next matches reachable from an inclusive start");

    try expectBefore(
        closure,
        "For `tools/lib/find_bit.zig`, current `master` still justifies a parked helper-local follow-up",
        "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route",
    );
}

test "find_bit helper exposes the direct anchors named by closure review" {
    const helper = try readRepoFile(helper_path, 192 * 1024);
    defer std.testing.allocator.free(helper);

    const expected_tests = [_][]const u8{
        "test \"find first and next set bits across words, with andnot gaps explicit\"",
        "test \"single-word next scans honor start masks\"",
        "test \"tail-word next set scans skip earlier in-range matches before clamping\"",
        "test \"tail-word next zero and shared scans skip earlier in-range matches before clamping\"",
        "test \"clump8 past-end scans return without reading bitmap words\"",
        "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
        "test \"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
        "test \"single-word tail windows keep the last in-range next matches reachable from an inclusive start\"",
        "test \"low-level underscore aliases mirror the primary find helpers, including andnot\"",
        "test \"Linux-style aliases mirror the primary find helpers, including andnot\"",
        "test \"Linux-style next-or aliases clamp tail words and past-end starts\"",
        "test \"Linux-style clump aliases mask tail bytes and preserve exhausted caller bytes\"",
    };

    for (expected_tests) |marker| {
        try expectContains(helper, marker);
    }

    const expected_entrypoints = [_][]const u8{
        "pub fn findFirstAndNotBit",
        "pub fn find_first_andnot_bit",
        "pub fn _find_first_andnot_bit",
        "pub fn findNextAndNotBit",
        "pub fn find_next_andnot_bit",
        "pub fn _find_next_andnot_bit",
    };

    for (expected_entrypoints) |entrypoint| {
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(helper, entrypoint));
    }
}

test "manifest keeps find_bit review anchors and next safe step precise" {
    const manifest = try readRepoFile(manifest_path, 256 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"tools/lib/find_bit.zig\"");
    try expectContains(manifest, "\"same_word_start_masks\": \"test \\\"single-word next scans honor start masks\\\"\"");
    try expectContains(manifest, "\"inclusive_boundary_start\": \"test \\\"head-word boundary scans keep the last in-range bit reachable from an inclusive start\\\"\"");
    try expectContains(manifest, "\"tail_word_inclusive_boundary_anchor\": \"test \\\"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\\\"\"");
    try expectContains(manifest, "\"single_word_tail_inclusive_boundary_anchor\": \"test \\\"single-word tail windows keep the last in-range next matches reachable from an inclusive start\\\"\"");
    try expectContains(manifest, "\"tail_word_set_skip_anchor\": \"test \\\"tail-word next set scans skip earlier in-range matches before clamping\\\"\"");
    try expectContains(manifest, "\"tail_word_skip_anchor\": \"test \\\"tail-word next zero and shared scans skip earlier in-range matches before clamping\\\"\"");
    try expectContains(manifest, "\"andnot_scan_entrypoint_contract\": \"The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.\"");
    try expectContains(manifest, "\"parity_fixture_keys\": [");
    try expectContains(manifest, "\"bits_per_long\"");
    try expectContains(manifest, "\"next_after_word\"");
    try expectContains(manifest, "\"next_and\"");
    try expectContains(manifest, "\"last\"");
    try expectContains(manifest, "keep find_bit parked unless a fresh reread finds drift in the manifest-backed same-word start-mask");
    try expectContains(manifest, "Linux-style alias coverage including the shipped andnot scan entry points");
}
