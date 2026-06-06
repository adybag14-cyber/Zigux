const std = @import("std");

const checker_source = @embedFile("check-phase1-parity.py");

fn expectContains(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, marker) != null);
}

fn expectOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, checker_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, checker_source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn expectExactCount(marker: []const u8, expected: usize) !void {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, checker_source[cursor..], marker)) |relative_index| {
        count += 1;
        cursor += relative_index + marker.len;
    }
    try std.testing.expectEqual(expected, count);
}

test "sample root writes every phase1 parity scaffold artifact" {
    try expectContains("def build_sample_root(root)");
    try expectContains("artifact_diff_text =");
    try expectContains("fixture_payload = {name: {} for name in EXPECTED_SECTIONS}");
    try expectContains("manifest_payload = {");
    try expectContains("blockers_payload = {");
    try expectContains("replay_text = \"\\n\".join(EXPECTED_REPLAY_MARKERS) + \"\\n\"");
    try expectContains("replay_build_text = \"\\n\".join(EXPECTED_REPLAY_BUILD_MARKERS) + \"\\n\"");
    try expectContains("write_text(root / ARTIFACT_DIFF_REL, artifact_diff_text)");
    try expectContains("write_text(root / REPLAY_REL, replay_text)");
    try expectContains("write_text(root / REPLAY_BUILD_REL, replay_build_text)");
    try expectContains("write_text(root / FIXTURE_REL, json.dumps(fixture_payload, indent=2) + \"\\n\")");
    try expectContains("write_text(root / MANIFEST_REL, json.dumps(manifest_payload, indent=2) + \"\\n\")");
    try expectContains("write_text(root / BLOCKERS_REL, json.dumps(blockers_payload, indent=2) + \"\\n\")");

    try expectOrdered("artifact_diff_text =", "write_text(root / ARTIFACT_DIFF_REL, artifact_diff_text)");
    try expectOrdered("manifest_payload = {", "write_text(root / MANIFEST_REL, json.dumps(manifest_payload, indent=2) + \"\\n\")");
    try expectOrdered("blockers_payload = {", "write_text(root / BLOCKERS_REL, json.dumps(blockers_payload, indent=2) + \"\\n\")");
}

test "sample root mirrors closed manifest and parked blocker state" {
    try expectContains("\"phase\": \"Phase 1\"");
    try expectContains("\"status\": \"closed\"");
    try expectContains("\"helper_count\": len(EXPECTED_HELPERS)");
    try expectContains("\"helpers\": list(EXPECTED_HELPERS)");
    try expectContains("\"shared_replay_parked_helpers\": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS)");
    try expectContains("\"direct_anchor_followup_helpers\": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)");
    try expectContains("\"review_anchors\": build_sample_review_anchor_payloads()");
    try expectContains("\"state\": \"blocked\"");
    try expectContains("\"id\": EXPECTED_REPLAY_BLOCKER_IDS[0]");
    try expectContains("\"field\": \"slab.zero_after_kmalloc\"");
    try expectContains("\"expected\": True");
    try expectContains("\"actual\": False");
    try expectContains("\"blocker_id\": EXPECTED_REPLAY_BLOCKER_IDS[1]");
}

test "self-test mutates sample root through exact review-anchor negatives" {
    try expectContains("def run_self_test()");
    try expectContains("build_sample_root(root)");
    try expectContains("ensure(collect_issues(root) == [], \"self_test:baseline\", [])");
    try expectContains("bitmap_payload.pop(\"shared_range_fixture_keys\")");
    try expectContains("manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:not_list");
    try expectContains("bitmap_payload[\"shared_range_fixture_keys\"] = [\"range_after_set\", \"range_after_clear\", \"full_after_fill\"]");
    try expectContains("issue.startswith(\"manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:\")");
    try expectContains("PHASE1_PARITY_SELF_TEST=pass");
    try expectContains("PHASE1_PARITY_SELF_TEST_CASE_COUNT={case_count}");
    try expectExactCount("case_count += 1", 3);
    try expectOrdered("ensure(collect_issues(root) == [], \"self_test:baseline\", [])", "bitmap_payload.pop(\"shared_range_fixture_keys\")");
    try expectOrdered("bitmap_payload.pop(\"shared_range_fixture_keys\")", "bitmap_payload[\"shared_range_fixture_keys\"] = [\"range_after_set\", \"range_after_clear\", \"full_after_fill\"]");
}
