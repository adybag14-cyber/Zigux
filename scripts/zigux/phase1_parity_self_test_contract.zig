const std = @import("std");

const checker_source = @embedFile("check-phase1-parity.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn markerIndex(needle: []const u8) !usize {
    return std.mem.indexOf(u8, checker_source, needle) orelse error.MarkerMissing;
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    try std.testing.expect((try markerIndex(first)) < (try markerIndex(second)));
}

fn countOccurrences(needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (start <= checker_source.len) {
        const found = std.mem.indexOf(u8, checker_source[start..], needle) orelse break;
        count += 1;
        start += found + needle.len;
    }
    return count;
}

test "phase1 parity checker self-test remains a CLI branch before root validation" {
    try expectContains("parser.add_argument(\"--self-test\", action=\"store_true\", help=\"run focused parity checker self-test\")");
    try expectContains("if args.self_test:\n        return run_self_test()");
    try expectContains("return run_check(Path(args.root).resolve())");
    try expectBefore("if args.self_test:\n        return run_self_test()", "return run_check(Path(args.root).resolve())");
}

test "phase1 parity checker self-test keeps the public summary stable" {
    try expectContains("def run_self_test() -> int:");
    try expectContains("case_count = 0");
    try std.testing.expectEqual(@as(usize, 3), countOccurrences("case_count += 1"));
    try expectContains("print(\"PHASE1_PARITY_SELF_TEST=pass\")");
    try expectContains("print(f\"PHASE1_PARITY_SELF_TEST_CASE_COUNT={case_count}\")");
}

test "phase1 parity checker self-test exercises review-anchor mutation failures" {
    try expectContains("build_sample_review_anchor_payloads()");
    try expectContains("ensure(collect_issues(root) == [], \"self_test:baseline\", [])");
    try expectContains("bitmap_payload.pop(\"shared_range_fixture_keys\")");
    try expectContains("\"manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:not_list\"");
    try expectContains("bitmap_payload[\"shared_range_fixture_keys\"] = [\"range_after_set\", \"range_after_clear\", \"full_after_fill\"]");
    try expectContains("issue.startswith(\"manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:\")");
    try expectBefore("bitmap_payload.pop(\"shared_range_fixture_keys\")", "bitmap_payload[\"shared_range_fixture_keys\"] = [\"range_after_set\", \"range_after_clear\", \"full_after_fill\"]");
}
