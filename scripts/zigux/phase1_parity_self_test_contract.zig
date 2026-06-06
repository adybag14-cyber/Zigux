const std = @import("std");

const source = @embedFile("check-phase1-parity.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBefore;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfter;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

fn isLiveSelfTestPacket(text: []const u8) bool {
    return std.mem.indexOf(u8, text, "def build_sample_review_anchor_payloads()") != null;
}

test "phase1 parity self-test source owns the live review-anchor packet" {
    if (!isLiveSelfTestPacket(source)) return error.SkipZigTest;

    try expectContains(source, "def run_self_test() -> int:");
    try expectContains(source, "PHASE1_PARITY_SELF_TEST=pass");
    try expectContains(source, "PHASE1_PARITY_SELF_TEST_CASE_COUNT={case_count}");
    try expectContains(source, "case_count = 0");
    try expectContains(source, "build_sample_root(root)");
    try expectContains(source, "build_sample_review_anchor_payloads()");
    try expectContains(source, "EXPECTED_DIRECT_REVIEW_ANCHOR_EXACT_FIELDS");
    try expectContains(source, "EXPECTED_DIRECT_REVIEW_ANCHOR_SUBSET_FIELDS");
    try expectOrder(source, "build_sample_root(root)", "ensure(collect_issues(root) == []");
    try expectOrder(source, "ensure(collect_issues(root) == []", "case_count += 1");
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(source, "PHASE1_PARITY_SELF_TEST=pass"));
}

test "phase1 parity self-test keeps both manifest review-anchor drift cases" {
    if (!isLiveSelfTestPacket(source)) return error.SkipZigTest;

    try expectContains(source, "bitmap_payload.pop(\"shared_range_fixture_keys\")");
    try expectContains(source, "\"manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:not_list\" in issues");
    try expectContains(source, "bitmap_payload[\"shared_range_fixture_keys\"] = [\"range_after_set\", \"range_after_clear\", \"full_after_fill\"]");
    try expectContains(source, "issue.startswith(\"manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:\")");
    try expectOrder(
        source,
        "bitmap_payload.pop(\"shared_range_fixture_keys\")",
        "bitmap_payload[\"shared_range_fixture_keys\"] = [\"range_after_set\", \"range_after_clear\", \"full_after_fill\"]",
    );
    try std.testing.expectEqual(@as(usize, 3), countOccurrences(source, "case_count += 1"));
}

test "phase1 parity checker routes duplicate-aware JSON before self-test fixtures" {
    if (!isLiveSelfTestPacket(source)) return error.SkipZigTest;

    try expectContains(source, "class DuplicateTrackingDict(dict[str, object]):");
    try expectContains(source, "def load_json_with_duplicate_tracking(text: str) -> object:");
    try expectContains(source, "def collect_duplicate_json_key_paths(data: object");
    try expectContains(source, "def read_json(path: Path, label: str, issues: list[str]) -> object | None:");
    try expectContains(source, "issues.extend(f\"{label}:duplicate_json_key:{duplicate_path}\"");
    try expectOrder(source, "def read_json(path: Path", "def build_sample_review_anchor_payloads()");
    try expectOrder(source, "manifest_payload = read_json(root / MANIFEST_REL", "review_anchors = manifest_payload[\"review_anchors\"]");
}

test "phase1 parity self-test does not fall back to stale case-count literals" {
    if (!isLiveSelfTestPacket(source)) return error.SkipZigTest;

    try expectNotContains(source, "PHASE1_PARITY_SELF_TEST_CASE_COUNT=22");
    try expectNotContains(source, "print(\"PHASE1_PARITY_SELF_TEST_CASE_COUNT=3\")");
    try expectContains(source, "print(f\"PHASE1_PARITY_SELF_TEST_CASE_COUNT={case_count}\")");
}
