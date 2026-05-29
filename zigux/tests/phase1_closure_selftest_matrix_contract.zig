const std = @import("std");

const MatrixCase = struct {
    name: []const u8,
    marker: []const u8,
};

const closure_selftest_core_cases = [_]MatrixCase{
    .{ .name = "baseline", .marker = "(\"baseline\", None)," },
    .{ .name = "bad_helper_count", .marker = "(\"bad_helper_count\", lambda root:" },
    .{ .name = "duplicate_manifest_helper_count", .marker = "(\"duplicate_manifest_helper_count\", lambda root: insert_duplicate_manifest_line(root," },
    .{ .name = "duplicate_manifest_lane_rule_summary", .marker = "(\"duplicate_manifest_lane_rule_summary\", lambda root: insert_duplicate_manifest_line(root," },
};

const helper_review_mutation_cases = [_]MatrixCase{
    .{ .name = "missing_find_bit_andnot_contract", .marker = "(\"missing_find_bit_andnot_contract\", lambda root: mutate_remove_review_key(root, \"tools/lib/find_bit.zig\", \"andnot_scan_entrypoint_contract\"))," },
    .{ .name = "stale_find_bit_review_summary", .marker = "(\"stale_find_bit_review_summary\", lambda root: mutate_bad_review_value(root, \"tools/lib/find_bit.zig\", \"review_packet_summary\"))," },
    .{ .name = "missing_rbtree_cached_root_alias_anchor", .marker = "(\"missing_rbtree_cached_root_alias_anchor\", lambda root: mutate_remove_review_key(root, \"tools/lib/rbtree.zig\", \"cached_root_alias_anchor\"))," },
    .{ .name = "stale_rbtree_cached_root_direct_review_summary", .marker = "(\"stale_rbtree_cached_root_direct_review_summary\", lambda root: mutate_bad_review_value(root, \"tools/lib/rbtree.zig\", \"cached_root_direct_review_summary\"))," },
    .{ .name = "missing_bitmap_or_window_anchor", .marker = "(\"missing_bitmap_or_window_anchor\", lambda root: mutate_remove_review_key(root, \"tools/lib/bitmap.zig\", \"or_window_anchor\"))," },
    .{ .name = "missing_bitmap_linux_alias_anchor", .marker = "(\"missing_bitmap_linux_alias_anchor\", lambda root: mutate_remove_review_key(root, \"tools/lib/bitmap.zig\", \"linux_alias_anchor\"))," },
    .{ .name = "stale_string_sysfs_review_summary", .marker = "(\"stale_string_sysfs_review_summary\", lambda root: mutate_bad_review_value(root, \"tools/lib/string.zig\", \"sysfs_review_summary\"))," },
    .{ .name = "stale_string_next_safe_step_note", .marker = "(\"stale_string_next_safe_step_note\", lambda root: mutate_bad_review_value(root, \"tools/lib/string.zig\", \"next_safe_step_note\"))," },
};

const delegated_checker_cases = [_]MatrixCase{
    .{ .name = "missing_string_checker", .marker = "(\"missing_string_checker\", lambda root: (root / STRING_REVIEW_CHECKER_REL).unlink())," },
    .{ .name = "failing_string_checker", .marker = "(\"failing_string_checker\", lambda root: make_checker_stub(root / STRING_REVIEW_CHECKER_REL, ok=False))," },
    .{ .name = "missing_find_bit_review_checker", .marker = "(\"missing_find_bit_review_checker\", lambda root: (root / FIND_BIT_REVIEW_CHECKER_REL).unlink())," },
    .{ .name = "failing_find_bit_review_checker", .marker = "(\"failing_find_bit_review_checker\", lambda root: make_checker_stub(root / FIND_BIT_REVIEW_CHECKER_REL, ok=False))," },
    .{ .name = "missing_rbtree_review_checker", .marker = "(\"missing_rbtree_review_checker\", lambda root: (root / RBTREE_REVIEW_CHECKER_REL).unlink())," },
    .{ .name = "failing_rbtree_review_checker", .marker = "(\"failing_rbtree_review_checker\", lambda root: make_checker_stub(root / RBTREE_REVIEW_CHECKER_REL, ok=False))," },
    .{ .name = "missing_direct_anchor_manifest_gate_checker", .marker = "(\"missing_direct_anchor_manifest_gate_checker\", lambda root: (root / DIRECT_ANCHOR_MANIFEST_GATE_REL).unlink())," },
    .{ .name = "failing_direct_anchor_manifest_gate_checker", .marker = "(\"failing_direct_anchor_manifest_gate_checker\", lambda root: make_checker_stub(root / DIRECT_ANCHOR_MANIFEST_GATE_REL, ok=False))," },
};

const makefile_boundary_cases = [_]MatrixCase{
    .{ .name = "missing_makefile_marker", .marker = "(\"missing_makefile_marker\", lambda root: write_text(root / ZIGUX_MAKEFILE_REL," },
    .{ .name = "missing_phase8_exec_cmd_route", .marker = "(\"missing_phase8_exec_cmd_route\", lambda root: write_text(root / ZIGUX_MAKEFILE_REL," },
    .{ .name = "forbidden_phase1_makefile_route", .marker = "(\"forbidden_phase1_makefile_route\", lambda root: write_text(root / ZIGUX_MAKEFILE_REL," },
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(512 * 1024),
    );
}

fn expectMatrixCases(validator: []const u8, comptime cases: []const MatrixCase) !void {
    inline for (cases) |case| {
        try expectContains(validator, case.marker);
    }
}

test "phase1 closure validator self-test keeps baseline and manifest drift cases explicit" {
    const validator = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "def run_self_test() -> int:");
    try expectContains(validator, "cases: list[tuple[str, object | None]] = [");
    try expectMatrixCases(validator, closure_selftest_core_cases[0..]);
}

test "phase1 closure validator self-test protects helper-local review mutations" {
    const validator = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    try expectMatrixCases(validator, helper_review_mutation_cases[0..]);
    try expectBefore(validator, "missing_find_bit_andnot_contract", "missing_rbtree_cached_root_alias_anchor");
    try expectBefore(validator, "missing_rbtree_cached_root_alias_anchor", "missing_bitmap_or_window_anchor");
    try expectBefore(validator, "missing_bitmap_or_window_anchor", "stale_string_sysfs_review_summary");
}

test "phase1 closure validator self-test exercises delegated checker loss and failure" {
    const validator = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    try expectMatrixCases(validator, delegated_checker_cases[0..]);
    try expectBefore(validator, "missing_string_checker", "failing_string_checker");
    try expectBefore(validator, "missing_find_bit_review_checker", "failing_find_bit_review_checker");
    try expectBefore(validator, "missing_direct_anchor_manifest_gate_checker", "failing_direct_anchor_manifest_gate_checker");
}

test "phase1 closure validator self-test keeps Makefile closure boundary cases" {
    const validator = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    try expectMatrixCases(validator, makefile_boundary_cases[0..]);
    try expectBefore(validator, "missing_makefile_marker", "missing_phase8_exec_cmd_route");
    try expectBefore(validator, "missing_phase8_exec_cmd_route", "forbidden_phase1_makefile_route");
}

test "phase1 closure validator self-test remains wired to the CLI contract" {
    const validator = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "parser.add_argument(\"--self-test\", action=\"store_true\", help=\"run validator self-tests\")");
    try expectContains(validator, "if args.self_test:");
    try expectContains(validator, "return run_self_test()");
    try expectContains(validator, "print(\"PHASE1_CLOSURE_SELF_TEST=pass\")");
    try expectContains(validator, "print(f\"PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}\")");
}
