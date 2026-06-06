const std = @import("std");

const read_limit = 512 * 1024;
const validator_path = "scripts/zigux/validate-phase1-closure.py";

const core_selftest_markers = [_][]const u8{
    "def run_self_test() -> int:",
    "cases: list[tuple[str, object | None]] = [",
    "parser.add_argument(\"--self-test\", action=\"store_true\", help=\"run validator self-tests\")",
    "if args.self_test:",
    "return run_self_test()",
    "failures = collect_failures(repo_root(args.root))",
    "print(\"PHASE1_CLOSURE_SELF_TEST=pass\")",
    "print(f\"PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}\")",
};

const closure_marker_cases = [_][]const u8{
    "(\"baseline\", None)",
    "(\"missing_restore_state\"",
    "(\"old_next_step_marker\"",
    "(\"forbidden_old_marker\"",
    "(\"missing_find_bit_bench_guard\"",
    "(\"missing_rbtree_bench_guard\"",
    "(\"missing_find_bit_review_guard\"",
    "(\"stale_find_bit_review_guard\"",
    "(\"missing_rbtree_review_guard\"",
    "(\"stale_rbtree_review_guard\"",
    "(\"missing_direct_anchor_manifest_gate_marker\"",
    "(\"stale_direct_anchor_manifest_gate_marker\"",
    "(\"missing_bitmap_direct_review\"",
    "(\"stale_bitmap_direct_review\"",
    "(\"missing_string_review_guard\"",
    "(\"stale_string_review_guard\"",
    "(\"missing_string_memtostr_review\"",
    "(\"stale_string_memtostr_review\"",
};

const manifest_drift_cases = [_][]const u8{
    "(\"bad_helper_count\"",
    "(\"stale_lane_rule_summary\"",
    "(\"stale_anti_overlap_rule\"",
    "(\"duplicate_manifest_helper_count\"",
    "(\"duplicate_manifest_lane_rule_summary\"",
    "(\"missing_find_bit_andnot_contract\"",
    "(\"stale_find_bit_review_summary\"",
    "(\"missing_rbtree_cached_root_alias_anchor\"",
    "(\"stale_rbtree_shared_replay_summary\"",
    "(\"missing_bitmap_or_window_anchor\"",
    "(\"missing_bitmap_linux_alias_anchor\"",
    "(\"stale_bitmap_next_safe_step_note\"",
    "(\"stale_string_sysfs_review_summary\"",
    "(\"stale_string_strcmp_review_anchors\"",
    "(\"stale_string_counted_search_review_anchors\"",
    "(\"stale_string_next_safe_step_note\"",
};

const delegated_checker_cases = [_][]const u8{
    "(\"missing_string_checker\"",
    "(\"failing_string_checker\"",
    "(\"missing_find_bit_review_checker\"",
    "(\"failing_find_bit_review_checker\"",
    "(\"missing_rbtree_review_checker\"",
    "(\"failing_rbtree_review_checker\"",
    "(\"missing_find_bit_bench_anchor_checker\"",
    "(\"failing_find_bit_bench_anchor_checker\"",
    "(\"missing_bitmap_direct_anchor_checker\"",
    "(\"failing_bitmap_direct_anchor_checker\"",
    "(\"missing_direct_anchor_manifest_gate_checker\"",
    "(\"failing_direct_anchor_manifest_gate_checker\"",
    "(\"failing_direct_owner_checker\"",
};

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(read_limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

fn countCaseEntries(source: []const u8) !usize {
    const start_marker = "cases: list[tuple[str, object | None]] = [";
    const end_marker = "\n    ]\n\n    for name, mutate in cases:";
    const start = std.mem.indexOf(u8, source, start_marker) orelse return error.CasesStartMissing;
    const tail = source[start..];
    const end = std.mem.indexOf(u8, tail, end_marker) orelse return error.CasesEndMissing;
    const cases_block = tail[0..end];

    var count: usize = 0;
    var remaining = cases_block;
    while (std.mem.indexOf(u8, remaining, "\n        (\"")) |index| {
        count += 1;
        remaining = remaining[index + 1 ..];
    }
    return count;
}

test "phase1 closure validator self-test dispatch and output stay explicit" {
    const validator = try readFile(validator_path);
    defer std.testing.allocator.free(validator);

    inline for (core_selftest_markers) |marker| {
        try expectContains(validator, marker);
    }

    try expectOrdered(validator, "if args.self_test:", "failures = collect_failures(repo_root(args.root))");
    try expectOrdered(validator, "print(\"PHASE1_CLOSURE_SELF_TEST=pass\")", "print(f\"PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}\")");

    const case_count = try countCaseEntries(validator);
    try std.testing.expect(case_count >= 60);
}

test "phase1 closure validator self-test keeps closure marker drift cases" {
    const validator = try readFile(validator_path);
    defer std.testing.allocator.free(validator);

    inline for (closure_marker_cases) |case_marker| {
        try expectContains(validator, case_marker);
    }

    try expectOrdered(validator, "(\"missing_restore_state\"", "(\"old_next_step_marker\"");
    try expectOrdered(validator, "(\"missing_find_bit_review_guard\"", "(\"stale_find_bit_review_guard\"");
    try expectOrdered(validator, "(\"missing_rbtree_review_guard\"", "(\"stale_rbtree_review_guard\"");
    try expectOrdered(validator, "(\"missing_string_review_guard\"", "(\"stale_string_review_guard\"");
}

test "phase1 closure validator self-test keeps manifest drift coverage" {
    const validator = try readFile(validator_path);
    defer std.testing.allocator.free(validator);

    inline for (manifest_drift_cases) |case_marker| {
        try expectContains(validator, case_marker);
    }

    try expectOrdered(validator, "(\"bad_helper_count\"", "(\"stale_lane_rule_summary\"");
    try expectOrdered(validator, "(\"duplicate_manifest_helper_count\"", "(\"duplicate_manifest_lane_rule_summary\"");
    try expectOrdered(validator, "(\"stale_find_bit_review_summary\"", "(\"stale_find_bit_next_safe_step_note\"");
    try expectOrdered(validator, "(\"stale_string_counted_search_review_anchors\"", "(\"stale_string_next_safe_step_note\"");
}

test "phase1 closure validator self-test keeps delegated checker and makefile boundary cases" {
    const validator = try readFile(validator_path);
    defer std.testing.allocator.free(validator);

    inline for (delegated_checker_cases) |case_marker| {
        try expectContains(validator, case_marker);
    }

    try expectContains(validator, "(\"missing_makefile_marker\"");
    try expectContains(validator, "(\"missing_phase8_validate_route\"");
    try expectContains(validator, "(\"forbidden_phase1_makefile_route\"");
    try expectOrdered(validator, "(\"missing_makefile_marker\"", "(\"forbidden_phase1_makefile_route\"");
}
