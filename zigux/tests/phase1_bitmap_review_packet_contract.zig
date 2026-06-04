const std = @import("std");
const options = @import("phase1_bitmap_review_packet_contract_options");

const checker_source = options.checker_source;

const required_paths = [_][]const u8{
    "tools/lib/bitmap.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers.json",
    "Documentation/zigux/phase1-closure.md",
};

const required_output_markers = [_][]const u8{
    "PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=pass",
    "PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST_CASE_COUNT=",
    "PHASE1_BITMAP_REVIEW_PACKET=fail",
    "PHASE1_BITMAP_REVIEW_PACKET=pass",
};

const required_helper_anchors = [_][]const u8{
    "bitmap range helpers preserve edges across whole-word spans",
    "bitmap copy alias preserves raw source words without tail clearing",
    "bitmap copy aliases preserve tail clearing and extension semantics",
    "bitmap zero-bit logical helpers stay explicit",
    "bitmap equal fast path ignores storage beyond an exact word boundary",
    "bitmap tail-masked helpers ignore out-of-range differences",
    "bitmap xor across a multiword tail still lets callers clamp the last word",
    "bitmap or across a multiword tail still lets callers clamp the last word",
    "bitmap complement clamps partial tails and leaves zero-sized caller views untouched",
    "bitmap scnprintf keeps contiguous ranges merged across word boundaries",
    "bitmap Linux-style aliases mirror copy logical range and format helpers",
    "bitmap allocation helpers size zero fill and reset optionals",
};

const required_fixture_keys = [_][]const u8{
    "partial_xor_nbits",
    "partial_xor_masked_values",
    "copy_clear_tail_values",
    "copy_and_extend_values",
    "terminator_only_scnprintf_len",
    "zero_length_scnprintf_len",
    "range_after_set",
    "range_after_clear",
};

const required_closure_markers = [_][]const u8{
    "PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit",
    "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit",
    "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit",
};

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
    }
}

test "bitmap review checker keeps current packet input paths explicit" {
    try expectContainsAll(checker_source, &required_paths);
}

test "bitmap review checker keeps output and self-test markers stable" {
    try expectContainsAll(checker_source, &required_output_markers);
    try std.testing.expect(std.mem.indexOf(u8, checker_source, "--self-test") != null);
}

test "bitmap review checker guards helper anchors and fixture keys" {
    try expectContainsAll(checker_source, &required_helper_anchors);
    try expectContainsAll(checker_source, &required_fixture_keys);
}

test "bitmap review checker guards closure marker contract" {
    try expectContainsAll(checker_source, &required_closure_markers);
}
