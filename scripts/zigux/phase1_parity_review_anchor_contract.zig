const std = @import("std");

const checker_source = @embedFile("check-phase1-parity.py");

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(contains(checker_source, needle));
}

fn expectBefore(left: []const u8, right: []const u8) !void {
    const left_index = std.mem.indexOf(u8, checker_source, left) orelse return error.MissingLeftMarker;
    const right_index = std.mem.indexOf(u8, checker_source, right) orelse return error.MissingRightMarker;
    try std.testing.expect(left_index < right_index);
}

fn requireLiveReviewAnchorSurface() !void {
    if (!contains(checker_source, "def ensure_review_anchor_exact_fields") or
        !contains(checker_source, "def ensure_review_anchor_subset_fields"))
    {
        return error.SkipZigTest;
    }
}

test "direct review anchor helper maps keep exact and subset field ownership explicit" {
    try requireLiveReviewAnchorSurface();

    try expectBefore(
        "EXPECTED_DIRECT_REVIEW_ANCHOR_EXACT_FIELDS: dict[str, dict[str, object]] = {",
        "EXPECTED_DIRECT_REVIEW_ANCHOR_SUBSET_FIELDS: dict[str, dict[str, tuple[str, ...]]] = {",
    );
    try expectContains("EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS = (");
    try expectContains("\"tools/lib/bitmap.zig\",");
    try expectContains("\"tools/lib/find_bit.zig\",");
    try expectContains("\"tools/lib/rbtree.zig\",");
    try expectContains("\"tools/lib/string.zig\",");

    try expectContains("\"shared_range_fixture_keys\": (");
    try expectContains("\"partial_xor_review_fields\": (");
    try expectContains("\"andnot_scan_entrypoints\": (");
    try expectContains("\"tail_inclusive_boundary_fixture_keys\": (");
    try expectContains("\"cached_leftmost_fixture_keys\": (");
    try expectContains("\"cached_root_transition_fixture_keys\": (");
    try expectContains("\"memparse_review_anchors\": (");
    try expectContains("\"sysfs_review_anchors\": (");
    try expectContains("\"helper_test_anchors\": (");
}

test "review anchor exact and subset validators emit stable fail closed issue keys" {
    try requireLiveReviewAnchorSurface();

    try expectContains("def ensure_review_anchor_exact_fields(helper: str, helper_payload: dict[str, object], issues: list[str]) -> None:");
    try expectContains("def ensure_review_anchor_subset_fields(helper: str, helper_payload: dict[str, object], issues: list[str]) -> None:");
    try expectContains("actual_value = helper_payload.get(key)");
    try expectContains("issue_prefix = f\"manifest:review_anchors:{helper}:{key}\"");
    try expectContains("ensure(isinstance(actual_value, list), f\"{issue_prefix}:not_list\", issues)");
    try expectContains("ensure(tuple(actual_value) == expected_value, f\"{issue_prefix}:{actual_value!r}!={expected_value!r}\", issues)");
    try expectContains("ensure(expected_value in actual_value, f\"{issue_prefix}:missing:{expected_value}\", issues)");
    try expectBefore(
        "ensure_review_anchor_exact_fields(helper, helper_payload, issues)",
        "ensure_review_anchor_subset_fields(helper, helper_payload, issues)",
    );
}

test "parity checker self test mutates review anchors to prove negative paths" {
    try requireLiveReviewAnchorSurface();

    try expectContains("def build_sample_review_anchor_payloads() -> dict[str, dict[str, object]]:");
    try expectContains("for helper in EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS:");
    try expectContains("payload[key] = list(value) if isinstance(value, tuple) else value");
    try expectContains("bitmap_payload.pop(\"shared_range_fixture_keys\")");
    try expectContains("\"manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:not_list\" in issues");
    try expectContains("bitmap_payload[\"shared_range_fixture_keys\"] = [\"range_after_set\", \"range_after_clear\", \"full_after_fill\"]");
    try expectContains("issue.startswith(\"manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:\")");
}
