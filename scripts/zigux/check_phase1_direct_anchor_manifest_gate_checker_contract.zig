const std = @import("std");

const source_path = @import("contract_options").source_path;

fn readSource(allocator: std.mem.Allocator) ![]const u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        source_path,
        allocator,
        .limited(512 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn requireOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBefore;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfter;
    try std.testing.expect(before_index < after_index);
}

test "direct-anchor manifest checker pins the helper-family split" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "EXPECTED_HELPERS = [");
    try requireContains(source, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
    try requireContains(source, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
    try requireContains(source, "\"tools/lib/argv_split.zig\"");
    try requireContains(source, "\"tools/lib/bitmap.zig\"");
    try requireContains(source, "\"tools/lib/find_bit.zig\"");
    try requireContains(source, "\"tools/lib/rbtree.zig\"");
    try requireContains(source, "\"tools/lib/string.zig\"");
    try requireContains(source, "\"tools/lib/zalloc.zig\"");
    try requireContains(source, "helper_count\") != len(EXPECTED_HELPERS)");
    try requireContains(source, "manifest:helper_count=13");
    try requireContains(source, "manifest:lane_sequencing.shared_replay_parked_helpers");
    try requireContains(source, "manifest:lane_sequencing.direct_anchor_followup_helpers");
    try requireContains(source, "manifest:lane_sequencing.anti_overlap_rule");
    try requireContains(source, "Do not reopen Phase 1 by batching helpers across those two sets in one lane");

    try requireOrder(source, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [", "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
    try requireOrder(source, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [", "EXPECTED_REVIEW_FIELDS = {");
}

test "review-field source keeps each direct-anchor helper family guarded" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "\"tools/lib/bitmap.zig\": {");
    try requireContains(source, "\"copy_raw_alias_anchor\"");
    try requireContains(source, "\"or_multiword_tail_anchor\"");
    try requireContains(source, "\"weighted_tail_count_anchor\"");
    try requireContains(source, "\"partial_xor_review_fields\"");
    try requireContains(source, "\"tools/lib/find_bit.zig\": {");
    try requireContains(source, "\"andnot_scan_entrypoints\"");
    try requireContains(source, "\"same_word_start_masks\"");
    try requireContains(source, "\"Linux-style aliases mirror the primary find helpers, including andnot\"");
    try requireContains(source, "\"tools/lib/rbtree.zig\": {");
    try requireContains(source, "\"cached_root_followup_anchors\"");
    try requireContains(source, "\"cached_root_transition_fixture_keys\"");
    try requireContains(source, "\"cached_leftmost_return_serials\"");
    try requireContains(source, "\"tools/lib/string.zig\": {");
    try requireContains(source, "\"strcmp_review_anchors\"");
    try requireContains(source, "\"counted_search_review_anchors\"");
    try requireContains(source, "\"strnchr_review_summary\"");

    try requireContains(source, "manifest:review_anchor_value={helper}:{field}");
}

test "delegated checker handoff remains explicit and fail-closed" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bitmap-direct-anchors.py\")");
    try requireContains(source, "FIND_BIT_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-review-packet.py\")");
    try requireContains(source, "RBTREE_DIRECT_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-rbtree-direct-anchors.py\")");
    try requireContains(source, "RBTREE_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-rbtree-review-packet.py\")");
    try requireContains(source, "STRING_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-string-review-packet.py\")");
    try requireContains(source, "DELEGATED_CHECKERS = (");
    try requireContains(source, "PHASE1_BITMAP_DIRECT_ANCHORS=pass");
    try requireContains(source, "phase1-find-bit-review-packet:ok");
    try requireContains(source, "PHASE1_RBTREE_DIRECT_ANCHORS=pass");
    try requireContains(source, "phase1-rbtree-review-packet:ok");
    try requireContains(source, "phase1-string-review-packet:ok");
    try requireContains(source, "run_checker(root, script_rel, label, success_stdout)");
    try requireContains(source, "missing_success_stdout");
    try requireContains(source, ":exit=");

    try requireOrder(source, "DELEGATED_CHECKERS = (", "def run_checker(");
    try requireOrder(source, "def run_checker(", "if not issues:");
}

test "self-test and public output envelope stay review-visible" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "class DuplicateTrackingDict");
    try requireContains(source, "collect_duplicate_json_key_paths");
    try requireContains(source, "manifest:duplicate_json_key");
    try requireContains(source, "write_sample_root");
    try requireContains(source, "insert_duplicate_manifest_line");
    try requireContains(source, "write_zero_exit_wrong_output_checker");
    try requireContains(source, "write_failing_checker");
    try requireContains(source, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass");
    try requireContains(source, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST_CASE_COUNT={case_count}");
    try requireContains(source, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=fail");
    try requireContains(source, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_START");
    try requireContains(source, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass");
    try requireContains(source, "PHASE1_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}");
    try requireContains(source, "PHASE1_DIRECT_ANCHOR_REVIEW_FIELD_COUNT={sum(len(fields) for fields in EXPECTED_REVIEW_FIELDS.values())}");
    try requireContains(source, "PHASE1_DIRECT_ANCHOR_DELEGATED_CHECKER_COUNT={len(DELEGATED_CHECKERS)}");

    try requireOrder(source, "def collect_issues(", "def run_checker(");
    try requireOrder(source, "def run_checker(", "def run_self_test(");
    try requireOrder(source, "def run_self_test(", "def main()");
}
