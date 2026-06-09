const std = @import("std");
const source_path = @import("source_path").path;

const structure_markers = [_][]const u8{
    "\"\"\"Guard the Phase 1 string helper review packet against helper, manifest, fixture, and lane-note drift.\"\"\"",
    "STRING_HELPER_REL = Path(\"tools/lib/string.zig\")",
    "STRING_MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")",
    "STRING_FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")",
    "STRING_LANE_NOTE_REL = Path(\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\")",
    "class DuplicateTrackingDict(dict[str, object]):",
    "EXPECTED_STRING_SOURCE_SYMBOLS = [",
    "EXPECTED_HELPER_TEST_ANCHORS = [",
    "EXPECTED_HELPER_SOURCE_EQUIVALENT_ANCHORS = {",
    "EXPECTED_HELPER_LOCAL_ONLY_ANCHORS = [",
    "EXPECTED_STRING_PACKET = {",
    "EXPECTED_STRING_FIXTURE_VALUES = {",
    "EXPECTED_STRING_LANE_MARKERS = [",
    "def collect_failures(root: Path) -> list[str]:",
    "def run_self_test() -> int:",
};

const packet_markers = [_][]const u8{
    "\"memparse_review_anchors\": [",
    "\"strlcat_review_anchors\": [",
    "\"copy_fill_review_anchors\": [",
    "\"memtostr_review_anchors\": [",
    "\"prefix_suffix_review_anchors\": [",
    "\"lookup_review_anchors\": [",
    "\"sysfs_review_anchors\": [",
    "\"strscpy_review_anchors\": [",
    "\"strcmp_review_anchors\": [",
    "\"casecmp_review_anchors\": [",
    "\"substring_search_review_anchors\": [",
    "\"search_length_review_anchors\": [",
    "\"counted_search_review_anchors\": [",
    "\"replace_char_cstr_bytes\": [97, 95, 0, 45, 122],",
    "\"lane_direct_owner\",",
    "\"lane_next_safe_step\",",
};

const validation_markers = [_][]const u8{
    "duplicate_manifest_paths = collect_duplicate_json_key_paths(manifest)",
    "duplicate_fixture_paths = collect_duplicate_json_key_paths(fixture)",
    "for symbol in EXPECTED_STRING_SOURCE_SYMBOLS:",
    "for anchor in EXPECTED_HELPER_TEST_ANCHORS:",
    "for anchor in EXPECTED_HELPER_LOCAL_ONLY_ANCHORS:",
    "for key, expected in EXPECTED_STRING_PACKET.items():",
    "for key, expected in EXPECTED_STRING_FIXTURE_VALUES.items():",
    "PHASE1_STRING_REVIEW_PACKET_SELF_TEST=pass",
    "PHASE1_STRING_REVIEW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}",
    "phase1-string-review-packet:ok",
};

const self_test_markers = [_][]const u8{
    "\"missing_file:tools/lib/string.zig\"",
    "phase1-string-review:self-test:strlcat_anchor",
    "phase1-string-review:self-test:strlcat_source_alias",
    "phase1-string-review:self-test:casecmp_anchor",
    "phase1-string-review:self-test:strchrnul_anchor",
    "phase1-string-review:self-test:memchr_fast_path_anchor",
    "phase1-string-review:self-test:lane_next_safe_step",
    "phase1-string-review:self-test:manifest_duplicate_json_key",
    "phase1-string-review:self-test:fixture_duplicate_json_key",
    "phase1-string-review:self-test:memchr_unaligned_prefix_anchor",
    "phase1-string-review:self-test:memchr_aligned_word_hit_anchor",
};

fn readSource(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, source_path, allocator, .limited(1024 * 1024));
}

fn requireOnce(text: []const u8, marker: []const u8) !void {
    const count = std.mem.count(u8, text, marker);
    if (count != 1) {
        std.debug.print("expected marker once, found {d}: {s}\n", .{ count, marker });
        return error.MarkerCountMismatch;
    }
}

fn requirePresent(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) == null) {
        std.debug.print("missing marker: {s}\n", .{marker});
        return error.MarkerMissing;
    }
}

test "string review checker keeps source structure and rosters" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (structure_markers) |marker| try requireOnce(source, marker);
}

test "string review checker keeps packet families and validation outputs" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (packet_markers) |marker| try requirePresent(source, marker);
    for (validation_markers) |marker| try requirePresent(source, marker);
}

test "string review checker keeps negative self-test coverage" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (self_test_markers) |marker| try requireOnce(source, marker);
}
