const std = @import("std");

const SourceFile = struct {
    contents: []u8,
};

const validator_path = "scripts/zigux/validate-phase1-closure.py";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const selftest_case_names = [_][]const u8{
    "\"baseline\"",
    "\"missing_restore_state\"",
    "\"old_next_step_marker\"",
    "\"forbidden_old_marker\"",
    "\"missing_find_bit_bench_guard\"",
    "\"missing_rbtree_bench_guard\"",
    "\"missing_find_bit_bench_anchor_guard\"",
    "\"missing_find_bit_review_guard\"",
    "\"stale_find_bit_review_guard\"",
    "\"missing_rbtree_review_guard\"",
    "\"stale_rbtree_review_guard\"",
    "\"missing_direct_anchor_manifest_gate_marker\"",
    "\"stale_direct_anchor_manifest_gate_marker\"",
    "\"missing_route_summary_guard\"",
    "\"missing_shared_tests_route\"",
    "\"missing_validator_state\"",
    "\"missing_bitmap_direct_review\"",
    "\"stale_bitmap_direct_review\"",
    "\"missing_bitmap_linux_alias_review\"",
    "\"stale_bitmap_linux_alias_review\"",
    "\"missing_string_review_guard\"",
    "\"stale_string_review_guard\"",
    "\"missing_string_memtostr_review\"",
    "\"stale_string_memtostr_review\"",
    "\"bad_helper_count\"",
    "\"stale_lane_rule_summary\"",
    "\"stale_anti_overlap_rule\"",
    "\"duplicate_manifest_helper_count\"",
    "\"duplicate_manifest_lane_rule_summary\"",
    "\"missing_find_bit_andnot_contract\"",
    "\"stale_find_bit_review_summary\"",
    "\"stale_find_bit_next_safe_step_note\"",
    "\"missing_rbtree_cached_root_alias_anchor\"",
    "\"stale_rbtree_shared_replay_summary\"",
    "\"stale_rbtree_cached_root_direct_review_summary\"",
    "\"missing_bitmap_or_window_anchor\"",
    "\"missing_bitmap_copy_raw_alias_anchor\"",
    "\"missing_bitmap_final_partial_word_anchor\"",
    "\"missing_bitmap_linux_alias_anchor\"",
    "\"stale_bitmap_empty_buffer_anchor\"",
    "\"stale_bitmap_next_safe_step_note\"",
    "\"stale_string_sysfs_review_summary\"",
    "\"stale_string_strcmp_review_anchors\"",
    "\"stale_string_strcmp_review_summary\"",
    "\"stale_string_search_length_review_anchors\"",
    "\"stale_string_search_length_review_summary\"",
    "\"stale_string_counted_search_review_anchors\"",
    "\"stale_string_strnchr_review_summary\"",
    "\"stale_string_next_safe_step_note\"",
    "\"missing_string_checker\"",
    "\"failing_string_checker\"",
    "\"missing_find_bit_review_checker\"",
    "\"missing_rbtree_review_checker\"",
    "\"missing_find_bit_bench_anchor_checker\"",
    "\"failing_find_bit_bench_anchor_checker\"",
    "\"missing_bitmap_direct_anchor_checker\"",
    "\"failing_bitmap_direct_anchor_checker\"",
    "\"missing_direct_anchor_manifest_gate_checker\"",
    "\"failing_direct_anchor_manifest_gate_checker\"",
    "\"failing_find_bit_review_checker\"",
    "\"failing_rbtree_review_checker\"",
    "\"failing_direct_owner_checker\"",
    "\"missing_makefile_marker\"",
    "\"missing_phase8_validate_route\"",
    "\"forbidden_phase1_makefile_route\"",
};

const delegated_checker_paths = [_][]const u8{
    "STRING_REVIEW_CHECKER_REL",
    "FIND_BIT_REVIEW_CHECKER_REL",
    "RBTREE_REVIEW_CHECKER_REL",
    "DIRECT_OWNER_CHECKER_REL",
    "DIRECT_ANCHOR_MANIFEST_GATE_REL",
    "ROUTE_SUMMARY_CHECKER_REL",
    "FIND_BIT_BENCH_ANCHOR_CHECKER_REL",
    "BITMAP_DIRECT_ANCHOR_CHECKER_REL",
    "SHARED_REMINDER_CHECKER_REL",
};

fn readFile(path: []const u8, limit: usize) !SourceFile {
    return .{
        .contents = try std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            path,
            std.testing.allocator,
            .limited(limit),
        ),
    };
}

fn unload(file: SourceFile) void {
    std.testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase1 closure validator self-test keeps public pass and count markers" {
    const validator = try readFile(validator_path, 512 * 1024);
    defer unload(validator);

    try expectContains(validator.contents, "def run_self_test() -> int:");
    try expectContains(validator.contents, "PHASE1_CLOSURE_SELF_TEST=pass");
    try expectContains(validator.contents, "PHASE1_CLOSURE_SELF_TEST_CASE_COUNT=");
    try expectContains(validator.contents, "len(cases)");
    try expectContains(validator.contents, "phase1-closure-self-test:{name}:unexpected=");
    try expectContains(validator.contents, "phase1-closure-self-test:{name}:expected_failure");
}

test "phase1 closure validator self-test pins the hardening case roster" {
    const validator = try readFile(validator_path, 512 * 1024);
    defer unload(validator);

    inline for (selftest_case_names) |case_name| {
        try expectContains(validator.contents, case_name);
    }

    try expectContains(validator.contents, "EXPECTED_CLOSURE_MARKERS");
    try expectContains(validator.contents, "EXPECTED_BITMAP_REVIEW_ANCHORS");
    try expectContains(validator.contents, "EXPECTED_FIND_BIT_REVIEW_ANCHORS");
    try expectContains(validator.contents, "EXPECTED_RBTREE_REVIEW_ANCHORS");
    try expectContains(validator.contents, "EXPECTED_STRING_REVIEW_ANCHORS");
}

test "phase1 closure validator self-test still exercises delegated checker failures" {
    const validator = try readFile(validator_path, 512 * 1024);
    defer unload(validator);

    try expectContains(validator.contents, "DELEGATED_CHECKERS");
    try expectContains(validator.contents, "delegated:{label}:");
    try expectContains(validator.contents, "make_checker_stub");
    try expectContains(validator.contents, "stub:failure");

    inline for (delegated_checker_paths) |checker| {
        try expectContains(validator.contents, checker);
    }
}

test "bootstrap workflow keeps phase1 closure validator self-test before live check" {
    const workflow = try readFile(workflow_path, 512 * 1024);
    defer unload(workflow);

    try expectOrdered(
        workflow.contents,
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "name: Check current Phase 1 closure packet",
    );
    try expectOrdered(
        workflow.contents,
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    );
    try expectOrdered(
        workflow.contents,
        "name: Check current Phase 1 closure packet",
        "python3 scripts/zigux/validate_phase3_selftest.py",
    );
}
