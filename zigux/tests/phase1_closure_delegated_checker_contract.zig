const std = @import("std");

const Checker = struct {
    rel_var: []const u8,
    label: []const u8,
    missing_case: ?[]const u8 = null,
    failing_case: ?[]const u8 = null,
};

const delegated_checkers = [_]Checker{
    .{
        .rel_var = "STRING_REVIEW_CHECKER_REL",
        .label = "phase1-string-review-packet",
        .missing_case = "missing_string_checker",
        .failing_case = "failing_string_checker",
    },
    .{
        .rel_var = "FIND_BIT_REVIEW_CHECKER_REL",
        .label = "phase1-find-bit-review-packet",
        .missing_case = "missing_find_bit_review_checker",
        .failing_case = "failing_find_bit_review_checker",
    },
    .{
        .rel_var = "RBTREE_REVIEW_CHECKER_REL",
        .label = "phase1-rbtree-review-packet",
        .missing_case = "missing_rbtree_review_checker",
        .failing_case = "failing_rbtree_review_checker",
    },
    .{
        .rel_var = "DIRECT_OWNER_CHECKER_REL",
        .label = "phase1-direct-owner-markers",
        .failing_case = "failing_direct_owner_checker",
    },
    .{
        .rel_var = "DIRECT_ANCHOR_MANIFEST_GATE_REL",
        .label = "phase1-direct-anchor-manifest-gate",
        .missing_case = "missing_direct_anchor_manifest_gate_checker",
        .failing_case = "failing_direct_anchor_manifest_gate_checker",
    },
    .{
        .rel_var = "ROUTE_SUMMARY_CHECKER_REL",
        .label = "phase1-route-summary-counts",
    },
    .{
        .rel_var = "FIND_BIT_BENCH_ANCHOR_CHECKER_REL",
        .label = "phase1-find-bit-bench-anchors",
        .missing_case = "missing_find_bit_bench_anchor_checker",
        .failing_case = "failing_find_bit_bench_anchor_checker",
    },
    .{
        .rel_var = "BITMAP_DIRECT_ANCHOR_CHECKER_REL",
        .label = "phase1-bitmap-direct-anchors",
        .missing_case = "missing_bitmap_direct_anchor_checker",
        .failing_case = "failing_bitmap_direct_anchor_checker",
    },
    .{
        .rel_var = "SHARED_REMINDER_CHECKER_REL",
        .label = "phase1-shared-reminder-packet",
    },
};

fn readValidator(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "scripts/zigux/validate-phase1-closure.py",
        allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn expectOnce(text: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, text, needle));
}

test "phase1 closure validator delegates to the expected checker roster" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try expectOnce(validator, "DELEGATED_CHECKERS = (");
    try expectOnce(validator, "for script_rel, label in DELEGATED_CHECKERS:");
    try expectOnce(validator, "failures.extend(run_checker(root, script_rel, label))");
    try expectOnce(validator, "return [f\"delegated:{label}:{line}\" for line in output]");

    for (delegated_checkers) |checker| {
        try expectContains(validator, checker.rel_var);
        try expectContains(validator, checker.label);
        try expectContains(validator, "DELEGATED_CHECKERS");
        try expectContains(validator, "run_checker(root, script_rel, label)");
    }
}

test "phase1 closure self-test covers delegated checker disappearance and failure" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try expectOnce(validator, "def run_self_test() -> int:");
    try expectOnce(validator, "PHASE1_CLOSURE_SELF_TEST=pass");
    try expectOnce(validator, "PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}");
    try expectOnce(validator, "make_checker_stub(root / checker_rel)");

    for (delegated_checkers) |checker| {
        if (checker.missing_case) |case_name| {
            try expectOnce(validator, case_name);
        }
        if (checker.failing_case) |case_name| {
            try expectOnce(validator, case_name);
        }
    }

    try expectContains(validator, "missing_direct_anchor_manifest_gate_checker");
    try expectContains(validator, "failing_direct_anchor_manifest_gate_checker");
    try expectContains(validator, "failing_direct_owner_checker");
}

test "phase1 closure validator keeps public success markers distinct from self-test markers" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "PHASE1_CLOSURE_VALIDATION=pass");
    try expectContains(validator, "PHASE1_CLOSURE_MODE=current-master-safe");
    try expectContains(validator, "if args.self_test:");
    try expectContains(validator, "def main() -> int:");
}
