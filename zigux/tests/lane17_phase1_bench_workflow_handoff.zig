const std = @import("std");

const bench_self_test_step = "      - name: Self-test current Phase 1 bench checker\n        run: python3 scripts/zigux/check-phase1-bench.py --self-test";
const bench_live_check_step = "      - name: Check current Phase 1 bench packet\n        run: python3 scripts/zigux/check-phase1-bench.py";
const find_bit_bench_self_test_step = "      - name: Self-test current Phase 1 find-bit bench anchor checker\n        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test";
const find_bit_bench_live_check_step = "      - name: Check current Phase 1 find-bit bench anchor packet\n        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py";

fn requireIndex(source: []const u8, marker: []const u8) !usize {
    return std.mem.indexOf(u8, source, marker) orelse error.MissingWorkflowMarker;
}

fn requireSingleMarker(source: []const u8, marker: []const u8) !usize {
    const first = try requireIndex(source, marker);
    if (std.mem.indexOfPos(u8, source, first + marker.len, marker) != null) {
        return error.DuplicateWorkflowMarker;
    }
    return first;
}

fn requireBefore(earlier_index: usize, later_index: usize) !void {
    if (earlier_index >= later_index) {
        return error.WorkflowMarkerOutOfOrder;
    }
}

fn requirePhase1BenchHandoff(workflow: []const u8) !void {
    const bench_self_test = try requireSingleMarker(workflow, bench_self_test_step);
    const bench_live_check = try requireSingleMarker(workflow, bench_live_check_step);
    const find_bit_bench_self_test = try requireSingleMarker(workflow, find_bit_bench_self_test_step);
    const find_bit_bench_live_check = try requireSingleMarker(workflow, find_bit_bench_live_check_step);

    try requireBefore(bench_self_test, bench_live_check);
    try requireBefore(bench_live_check, find_bit_bench_self_test);
    try requireBefore(find_bit_bench_self_test, find_bit_bench_live_check);
}

const expected_phase1_bench_handoff =
    bench_self_test_step ++
    "\n\n" ++
    bench_live_check_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

const missing_live_bench_check_handoff =
    bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

const duplicate_live_bench_check_handoff =
    bench_self_test_step ++
    "\n\n" ++
    bench_live_check_step ++
    "\n\n" ++
    bench_live_check_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

const reordered_live_bench_check_handoff =
    bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    bench_live_check_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

test "lane17 phase1 bench workflow contract accepts expected handoff" {
    try requirePhase1BenchHandoff(expected_phase1_bench_handoff);
}

test "lane17 phase1 bench workflow contract rejects missing live bench check" {
    try std.testing.expectError(
        error.MissingWorkflowMarker,
        requirePhase1BenchHandoff(missing_live_bench_check_handoff),
    );
}

test "lane17 phase1 bench workflow contract rejects duplicate live bench checks" {
    try std.testing.expectError(
        error.DuplicateWorkflowMarker,
        requirePhase1BenchHandoff(duplicate_live_bench_check_handoff),
    );
}

test "lane17 phase1 bench workflow contract rejects reordered live bench check" {
    try std.testing.expectError(
        error.WorkflowMarkerOutOfOrder,
        requirePhase1BenchHandoff(reordered_live_bench_check_handoff),
    );
}
