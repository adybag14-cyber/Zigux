const std = @import("std");

const WorkflowPatch = struct {
    changed_files: []const []const u8,
    additions: usize,
    deletions: usize,
    inserted_step: []const u8,
    inserted_command: []const u8,
    workflow_after_restack: []const u8,
    ahead_by: usize,
    behind_by: usize,
    status: []const u8,
};

const expected_step_name =
    \\- name: Check current Phase 1 bench packet
;

const expected_step_command =
    \\run: zig run scripts/zigux/check_phase1_bench.zig
;

const good_workflow =
    \\      - name: Self-test current Phase 1 route summary checker
    \\        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --self-test
    \\
    \\      - name: Check current Phase 1 route summary packet
    \\        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig
    \\
    \\      - name: Self-test current Phase 1 bench checker
    \\        run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test
    \\
    \\      - name: Check current Phase 1 bench packet
    \\        run: zig run scripts/zigux/check_phase1_bench.zig
    \\
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --self-test
    \\
    \\      - name: Check current Phase 1 find-bit bench anchor packet
    \\        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig
;

fn requireBenchWorkflowRestackReady(patch: WorkflowPatch) !void {
    try std.testing.expectEqual(@as(usize, 1), patch.changed_files.len);
    try std.testing.expectEqualStrings(".github/workflows/zigux-bootstrap.yml", patch.changed_files[0]);
    try std.testing.expectEqual(@as(usize, 3), patch.additions);
    try std.testing.expectEqual(@as(usize, 0), patch.deletions);
    try std.testing.expectEqualStrings("Check current Phase 1 bench packet", patch.inserted_step);
    try std.testing.expectEqualStrings("zig run scripts/zigux/check_phase1_bench.zig", patch.inserted_command);
    try std.testing.expectEqual(@as(usize, 0), patch.behind_by);
    try std.testing.expectEqualStrings("ahead", patch.status);

    const bench_selftest = "Self-test current Phase 1 bench checker";
    const live_bench = "Check current Phase 1 bench packet";
    const find_bit_selftest = "Self-test current Phase 1 find-bit bench anchor checker";

    const bench_selftest_at = std.mem.indexOf(u8, patch.workflow_after_restack, bench_selftest) orelse return error.MissingBenchSelfTest;
    const live_bench_at = std.mem.indexOf(u8, patch.workflow_after_restack, live_bench) orelse return error.MissingLiveBenchCheck;
    const find_bit_selftest_at = std.mem.indexOf(u8, patch.workflow_after_restack, find_bit_selftest) orelse return error.MissingFindBitBenchSelfTest;

    try std.testing.expect(bench_selftest_at < live_bench_at);
    try std.testing.expect(live_bench_at < find_bit_selftest_at);
    try std.testing.expectEqual(live_bench_at, std.mem.lastIndexOf(u8, patch.workflow_after_restack, live_bench).?);
    const live_bench_line_start = std.mem.lastIndexOfScalar(u8, patch.workflow_after_restack[0..live_bench_at], '\n') orelse 0;
    const live_bench_step = patch.workflow_after_restack[live_bench_line_start..find_bit_selftest_at];
    try std.testing.expect(std.mem.indexOf(u8, live_bench_step, expected_step_name) != null);
    try std.testing.expect(std.mem.indexOf(u8, live_bench_step, expected_step_command) != null);
}

test "bench workflow PR is ready only after current-master restack" {
    try requireBenchWorkflowRestackReady(.{
        .changed_files = &.{".github/workflows/zigux-bootstrap.yml"},
        .additions = 3,
        .deletions = 0,
        .inserted_step = "Check current Phase 1 bench packet",
        .inserted_command = "zig run scripts/zigux/check_phase1_bench.zig",
        .workflow_after_restack = good_workflow,
        .ahead_by = 1,
        .behind_by = 0,
        .status = "ahead",
    });
}

test "stale branch state is rejected even with the right workflow edit" {
    try std.testing.expectError(error.TestExpectedEqual, requireBenchWorkflowRestackReady(.{
        .changed_files = &.{".github/workflows/zigux-bootstrap.yml"},
        .additions = 3,
        .deletions = 0,
        .inserted_step = "Check current Phase 1 bench packet",
        .inserted_command = "zig run scripts/zigux/check_phase1_bench.zig",
        .workflow_after_restack = good_workflow,
        .ahead_by = 2,
        .behind_by = 290,
        .status = "diverged",
    }));
}

test "duplicate or misplaced live bench checks fail the contract" {
    const duplicated =
        good_workflow ++
        \\
        \\      - name: Check current Phase 1 bench packet
        \\        run: zig run scripts/zigux/check_phase1_bench.zig
        ;
    try std.testing.expectError(error.TestExpectedEqual, requireBenchWorkflowRestackReady(.{
        .changed_files = &.{".github/workflows/zigux-bootstrap.yml"},
        .additions = 3,
        .deletions = 0,
        .inserted_step = "Check current Phase 1 bench packet",
        .inserted_command = "zig run scripts/zigux/check_phase1_bench.zig",
        .workflow_after_restack = duplicated,
        .ahead_by = 1,
        .behind_by = 0,
        .status = "ahead",
    }));

    const misplaced =
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --self-test
        \\
        \\      - name: Check current Phase 1 bench packet
        \\        run: zig run scripts/zigux/check_phase1_bench.zig
    ;
    try std.testing.expectError(error.TestUnexpectedResult, requireBenchWorkflowRestackReady(.{
        .changed_files = &.{".github/workflows/zigux-bootstrap.yml"},
        .additions = 3,
        .deletions = 0,
        .inserted_step = "Check current Phase 1 bench packet",
        .inserted_command = "zig run scripts/zigux/check_phase1_bench.zig",
        .workflow_after_restack = misplaced,
        .ahead_by = 1,
        .behind_by = 0,
        .status = "ahead",
    }));
}

test "non-workflow or widened edits stay out of the bench insertion PR" {
    try std.testing.expectError(error.TestExpectedEqual, requireBenchWorkflowRestackReady(.{
        .changed_files = &.{ ".github/workflows/zigux-bootstrap.yml", "zigux/tests/build.zig" },
        .additions = 4,
        .deletions = 0,
        .inserted_step = "Check current Phase 1 bench packet",
        .inserted_command = "zig run scripts/zigux/check_phase1_bench.zig",
        .workflow_after_restack = good_workflow,
        .ahead_by = 1,
        .behind_by = 0,
        .status = "ahead",
    }));
}
