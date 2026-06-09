const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-parity.py";
const read_limit = 256 * 1024;

fn readCheckerSource(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, checker_path, allocator, .limited(read_limit));
}

fn requireCurrentReviewAnchorSurface(source: []const u8) !void {
    if (std.mem.indexOf(u8, source, "EXPECTED_DIRECT_REVIEW_ANCHOR_EXACT_FIELDS: dict[str, dict[str, object]]") == null) {
        return error.SkipZigTest;
    }
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOf(u8, haystack[index..], needle)) |offset| {
        count += 1;
        index += offset + needle.len;
    }
    return count;
}

fn expectContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn expectExactOccurrence(source: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(source, marker));
}

fn expectBefore(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.TestUnexpectedResult;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.TestUnexpectedResult;
    try std.testing.expect(first_index < second_index);
}

test "parity checker validates review-anchor exact fields through helper-aware issue keys" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);
    try requireCurrentReviewAnchorSurface(source);

    try expectExactOccurrence(source, "def ensure_review_anchor_exact_fields(helper: str, helper_payload: dict[str, object], issues: list[str]) -> None:");
    try expectContains(source, "for key, expected_value in EXPECTED_DIRECT_REVIEW_ANCHOR_EXACT_FIELDS.get(helper, {}).items():");
    try expectContains(source, "actual_value = helper_payload.get(key)");
    try expectContains(source, "issue_prefix = f\"manifest:review_anchors:{helper}:{key}\"");
    try expectContains(source, "if isinstance(expected_value, tuple):");
    try expectContains(source, "ensure(isinstance(actual_value, list), f\"{issue_prefix}:not_list\", issues)");
    try expectContains(source, "ensure(tuple(actual_value) == expected_value, f\"{issue_prefix}:{actual_value!r}!={expected_value!r}\", issues)");
    try expectContains(source, "ensure(actual_value == expected_value, f\"{issue_prefix}:{actual_value!r}!={expected_value!r}\", issues)");
    try expectBefore(source, "actual_value = helper_payload.get(key)", "if isinstance(expected_value, tuple):");
    try expectBefore(source, "if isinstance(expected_value, tuple):", "ensure(actual_value == expected_value");
}

test "parity checker validates review-anchor subset fields as membership requirements" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);
    try requireCurrentReviewAnchorSurface(source);

    try expectExactOccurrence(source, "def ensure_review_anchor_subset_fields(helper: str, helper_payload: dict[str, object], issues: list[str]) -> None:");
    try expectContains(source, "for key, expected_values in EXPECTED_DIRECT_REVIEW_ANCHOR_SUBSET_FIELDS.get(helper, {}).items():");
    try expectContains(source, "ensure(isinstance(actual_value, list), f\"{issue_prefix}:not_list\", issues)");
    try expectContains(source, "for expected_value in expected_values:");
    try expectContains(source, "ensure(expected_value in actual_value, f\"{issue_prefix}:missing:{expected_value}\", issues)");
    try expectBefore(source, "for key, expected_values in EXPECTED_DIRECT_REVIEW_ANCHOR_SUBSET_FIELDS.get(helper, {}).items():", "for expected_value in expected_values:");
    try expectBefore(source, "for expected_value in expected_values:", "ensure(expected_value in actual_value");
}

test "parity checker calls exact and subset validators from manifest review-anchor collection" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);
    try requireCurrentReviewAnchorSurface(source);

    try expectContains(source, "for helper in EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS:");
    try expectContains(source, "ensure(helper in review_anchors, f\"manifest:review_anchors:{helper}:missing\", issues)");
    try expectContains(source, "ensure_review_anchor_exact_fields(helper, helper_payload, issues)");
    try expectContains(source, "ensure_review_anchor_subset_fields(helper, helper_payload, issues)");
    try expectContains(source, "bitmap_payload.pop(\"shared_range_fixture_keys\")");
    try expectContains(source, "assert \"manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:not_list\" in issues");
    try expectContains(source, "bitmap_payload[\"shared_range_fixture_keys\"] = [\"range_after_set\", \"range_after_clear\", \"full_after_fill\"]");
    try expectContains(source, "issue.startswith(\"manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:\")");
    try expectBefore(source, "ensure_review_anchor_exact_fields(helper, helper_payload, issues)", "ensure_review_anchor_subset_fields(helper, helper_payload, issues)");
}
