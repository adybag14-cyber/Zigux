const std = @import("std");
const options = @import("contract_options");

const source = @embedFile(options.source_path);

fn requireContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireCount(needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, source, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn requireOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "direct-owner checker keeps the live owner file roster explicit" {
    try requireContains("REQUIRED_FILES = (");
    try requireContains("LANE_NOTE_REL = Path(\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\")");
    try requireContains("DOCS_ROOT_REL = Path(\"Documentation/zigux/README.md\")");
    try requireContains("PHASE1_CLOSURE_REL = Path(\"Documentation/zigux/phase1-closure.md\")");
    try requireContains("REVIEW_CHECKLIST_REL = Path(\"Documentation/zigux/review-checklist.md\")");
    try requireContains("TESTS_README_REL = Path(\"zigux/tests/README.md\")");
    try requireContains("SCRIPTS_README_REL = Path(\"scripts/zigux/README.md\")");
    try requireContains("PHASE1_CLOSURE_VALIDATOR_REL = Path(\"scripts/zigux/validate-phase1-closure.py\")");
    try requireContains("SHARED_REMINDER_CHECKER_REL = Path(\"scripts/zigux/check-phase1-shared-reminder-packet.py\")");
    try requireContains("MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")");
    try requireContains("BITMAP_HELPER_REL = Path(\"tools/lib/bitmap.zig\")");
    try requireContains("FIND_BIT_HELPER_REL = Path(\"tools/lib/find_bit.zig\")");
    try requireContains("RBTREE_HELPER_REL = Path(\"tools/lib/rbtree.zig\")");
    try requireContains("STRING_HELPER_REL = Path(\"tools/lib/string.zig\")");
    try requireOrder("EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [", "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
    try requireContains("\"tools/lib/bitmap.zig\",");
    try requireContains("\"tools/lib/find_bit.zig\",");
    try requireContains("\"tools/lib/rbtree.zig\",");
    try requireContains("\"tools/lib/string.zig\",");
}

test "manifest expectations stay grouped by helper-family review anchors" {
    try requireContains("MANIFEST_EXPECTATIONS = {");
    try requireContains("(\"phase\",): \"Phase 1\"");
    try requireContains("(\"status\",): \"closed\"");
    try requireContains("(\"helper_count\",): len(EXPECTED_HELPERS)");
    try requireContains("(\"lane_sequencing\", \"shared_replay_parked_helpers\"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS");
    try requireContains("(\"lane_sequencing\", \"direct_anchor_followup_helpers\"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS");
    try requireContains("(\"review_anchors\", \"tools/lib/bitmap.zig\", \"review_packet_summary\"): EXPECTED_BITMAP_REVIEW_PACKET_SUMMARY");
    try requireContains("(\"review_anchors\", \"tools/lib/find_bit.zig\", \"andnot_scan_entrypoints\"): EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINTS");
    try requireContains("(\"review_anchors\", \"tools/lib/rbtree.zig\", \"cached_root_followup_anchors\"): EXPECTED_RBTREE_CACHED_ROOT_FOLLOWUP_ANCHORS");
    try requireContains("(\"review_anchors\", \"tools/lib/string.zig\", \"counted_search_review_anchors\"):");
    try requireOrder("MANIFEST_EXPECTATIONS = {", "def collect_failures(root: Path) -> list[str]:");
    try requireOrder("duplicate_manifest_paths = collect_duplicate_json_key_paths(manifest)", "for path, expected in MANIFEST_EXPECTATIONS.items():");
}

test "self-test and public result markers remain fail-closed" {
    try requireContains("def run_self_test() -> int:");
    try requireContains("(\"success\", None, None, \"\")");
    try requireContains("for relative_path in REQUIRED_FILES:");
    try requireContains("for relative_path, lines in REQUIRED_EXACT_LINES.items():");
    try requireContains("for path in MANIFEST_EXPECTATIONS:");
    try requireContains("(\"duplicate_manifest_key:review_anchors\", None, None, \"duplicate_manifest_key\")");
    try requireContains("PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST=pass");
    try requireContains("PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST_CASE_COUNT=");
    try requireContains("PHASE1_DIRECT_OWNER_MARKERS=fail");
    try requireContains("PHASE1_DIRECT_OWNER_MARKERS=pass");
    try requireContains("PHASE1_DIRECT_OWNER_MARKERS_REQUIRED_FILE_COUNT=");
    try requireContains("PHASE1_DIRECT_OWNER_MARKERS_REQUIRED_LINE_COUNT=");
    try requireContains("PHASE1_DIRECT_OWNER_MARKERS_REQUIRED_HELPER_COUNT=");
    try requireCount("PHASE1_DIRECT_OWNER_MARKERS=pass", 1);
}
