const std = @import("std");

const bench_self_test_step =
    "      - name: Self-test current Phase 1 bench checker\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench.py --self-test";

const bench_live_check_step =
    "      - name: Check current Phase 1 bench packet\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench.py";

const bench_guard_self_test_step =
    "      - name: Self-test current Phase 1 bench live-check workflow guard\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test";

const bench_guard_live_check_step =
    "      - name: Check current Phase 1 bench live-check workflow guard\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py";

const find_bit_bench_self_test_step =
    "      - name: Self-test current Phase 1 find-bit bench anchor checker\n" ++
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test";

const find_bit_bench_live_check_step =
    "      - name: Check current Phase 1 find-bit bench anchor packet\n" ++
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py";

const expected_guarded_cluster =
    bench_self_test_step ++
    "\n\n" ++
    bench_live_check_step ++
    "\n\n" ++
    bench_guard_self_test_step ++
    "\n\n" ++
    bench_guard_live_check_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

fn requireSingleMarker(source: []const u8, marker: []const u8) !usize {
    const first = std.mem.indexOf(u8, source, marker) orelse return error.MissingWorkflowMarker;
    if (std.mem.indexOfPos(u8, source, first + marker.len, marker) != null) {
        return error.DuplicateWorkflowMarker;
    }
    return first;
}

fn requireBefore(earlier: usize, later: usize) !void {
    if (earlier >= later) return error.WorkflowMarkerOutOfOrder;
}

fn requirePhase1BenchLiveGuardCluster(workflow: []const u8) !void {
    const bench_self_test = try requireSingleMarker(workflow, bench_self_test_step);
    const bench_live_check = try requireSingleMarker(workflow, bench_live_check_step);
    const bench_guard_self_test = try requireSingleMarker(workflow, bench_guard_self_test_step);
    const bench_guard_live_check = try requireSingleMarker(workflow, bench_guard_live_check_step);
    const find_bit_self_test = try requireSingleMarker(workflow, find_bit_bench_self_test_step);
    const find_bit_live_check = try requireSingleMarker(workflow, find_bit_bench_live_check_step);

    try requireBefore(bench_self_test, bench_live_check);
    try requireBefore(bench_live_check, bench_guard_self_test);
    try requireBefore(bench_guard_self_test, bench_guard_live_check);
    try requireBefore(bench_guard_live_check, find_bit_self_test);
    try requireBefore(find_bit_self_test, find_bit_live_check);
}

test "lane17 phase1 bench live guard workflow cluster accepts intended order" {
    try requirePhase1BenchLiveGuardCluster(expected_guarded_cluster);
}

test "lane17 phase1 bench live guard workflow cluster rejects missing guard self-test" {
    const missing_guard_self_test =
        bench_self_test_step ++
        "\n\n" ++
        bench_live_check_step ++
        "\n\n" ++
        bench_guard_live_check_step ++
        "\n\n" ++
        find_bit_bench_self_test_step ++
        "\n\n" ++
        find_bit_bench_live_check_step ++
        "\n";

    try std.testing.expectError(
        error.MissingWorkflowMarker,
        requirePhase1BenchLiveGuardCluster(missing_guard_self_test),
    );
}

test "lane17 phase1 bench live guard workflow cluster rejects guard before live bench check" {
    const guard_before_live_check =
        bench_self_test_step ++
        "\n\n" ++
        bench_guard_self_test_step ++
        "\n\n" ++
        bench_live_check_step ++
        "\n\n" ++
        bench_guard_live_check_step ++
        "\n\n" ++
        find_bit_bench_self_test_step ++
        "\n\n" ++
        find_bit_bench_live_check_step ++
        "\n";

    try std.testing.expectError(
        error.WorkflowMarkerOutOfOrder,
        requirePhase1BenchLiveGuardCluster(guard_before_live_check),
    );
}

test "lane17 phase1 bench live guard workflow cluster rejects duplicate live guard" {
    const duplicate_live_guard =
        bench_self_test_step ++
        "\n\n" ++
        bench_live_check_step ++
        "\n\n" ++
        bench_guard_self_test_step ++
        "\n\n" ++
        bench_guard_live_check_step ++
        "\n\n" ++
        bench_guard_live_check_step ++
        "\n\n" ++
        find_bit_bench_self_test_step ++
        "\n\n" ++
        find_bit_bench_live_check_step ++
        "\n";

    try std.testing.expectError(
        error.DuplicateWorkflowMarker,
        requirePhase1BenchLiveGuardCluster(duplicate_live_guard),
    );
}

test "lane17 phase1 bench live guard workflow cluster rejects find-bit before guard live check" {
    const find_bit_before_guard_live_check =
        bench_self_test_step ++
        "\n\n" ++
        bench_live_check_step ++
        "\n\n" ++
        bench_guard_self_test_step ++
        "\n\n" ++
        find_bit_bench_self_test_step ++
        "\n\n" ++
        bench_guard_live_check_step ++
        "\n\n" ++
        find_bit_bench_live_check_step ++
        "\n";

    try std.testing.expectError(
        error.WorkflowMarkerOutOfOrder,
        requirePhase1BenchLiveGuardCluster(find_bit_before_guard_live_check),
    );
}
