const std = @import("std");

const validator_path = "scripts/zigux/validate-phase1-closure.py";

const required_cases = [_][]const u8{
    "baseline",
    "missing_restore_state",
    "old_next_step_marker",
    "forbidden_old_marker",
    "missing_find_bit_bench_guard",
    "stale_find_bit_review_guard",
    "missing_rbtree_review_guard",
    "missing_direct_anchor_manifest_gate_marker",
    "missing_bitmap_direct_review",
    "missing_string_memtostr_review",
    "bad_helper_count",
    "stale_lane_rule_summary",
    "stale_anti_overlap_rule",
    "duplicate_manifest_helper_count",
    "duplicate_manifest_lane_rule_summary",
    "missing_find_bit_andnot_contract",
    "stale_find_bit_next_safe_step_note",
    "missing_rbtree_cached_root_alias_anchor",
    "stale_rbtree_cached_root_direct_review_summary",
    "missing_bitmap_or_window_anchor",
    "missing_bitmap_copy_raw_alias_anchor",
    "missing_bitmap_linux_alias_anchor",
    "stale_bitmap_next_safe_step_note",
    "stale_string_sysfs_review_summary",
    "stale_string_strcmp_review_anchors",
    "stale_string_search_length_review_summary",
    "stale_string_counted_search_review_anchors",
    "stale_string_strnchr_review_summary",
    "stale_string_next_safe_step_note",
    "missing_string_checker",
    "failing_string_checker",
    "missing_find_bit_review_checker",
    "missing_rbtree_review_checker",
    "missing_find_bit_bench_anchor_checker",
    "failing_find_bit_bench_anchor_checker",
    "missing_bitmap_direct_anchor_checker",
    "failing_bitmap_direct_anchor_checker",
    "missing_direct_anchor_manifest_gate_checker",
    "failing_direct_anchor_manifest_gate_checker",
    "failing_find_bit_review_checker",
    "failing_rbtree_review_checker",
    "failing_direct_owner_checker",
    "missing_makefile_marker",
    "missing_phase8_validate_route",
    "forbidden_phase1_makefile_route",
};

fn readValidator(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, validator_path, allocator, .limited(1024 * 1024));
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingNeedle;
    const rest = haystack[first + needle.len ..];
    try std.testing.expectEqual(@as(?usize, null), std.mem.indexOf(u8, rest, needle));
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeNeedle;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterNeedle;
    try std.testing.expect(before_index < after_index);
}

test "phase1 closure self-test keeps named drift cases in the inventory" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    for (required_cases) |case_name| {
        var marker_buffer: [96]u8 = undefined;
        const marker = try std.fmt.bufPrint(&marker_buffer, "(\"{s}\"", .{case_name});
        try expectContainsOnce(validator, marker);
    }
}

test "phase1 closure self-test preserves baseline and expected-failure branches" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try expectContainsOnce(validator,
        \\    for name, mutate in cases:
    );
    try expectContainsOnce(validator,
        \\        if name == "baseline":
    );
    try expectContainsOnce(validator,
        \\                print(f"phase1-closure-self-test:{name}:unexpected={failures}")
    );
    try expectContainsOnce(validator,
        \\        elif not failures:
    );
    try expectContainsOnce(validator,
        \\            print(f"phase1-closure-self-test:{name}:expected_failure")
    );
    try expectOrdered(validator,
        \\        if name == "baseline":
    ,
        \\        elif not failures:
    );
}

test "phase1 closure self-test count is derived from the inventory" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try expectContainsOnce(validator,
        \\    print("PHASE1_CLOSURE_SELF_TEST=pass")
    );
    try expectContainsOnce(validator,
        \\    print(f"PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}")
    );
    try expectOrdered(validator,
        \\    for name, mutate in cases:
    ,
        \\    print("PHASE1_CLOSURE_SELF_TEST=pass")
    );
    try std.testing.expect(required_cases.len >= 40);
}
