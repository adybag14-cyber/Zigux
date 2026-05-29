const std = @import("std");

const bench_self_test_step =
    \\      - name: Self-test current Phase 1 bench checker
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
;

const bench_live_check_step =
    \\      - name: Check current Phase 1 bench packet
    \\        run: python3 scripts/zigux/check-phase1-bench.py
;

const find_bit_bench_self_test_step =
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
;

const find_bit_bench_live_check_step =
    \\      - name: Check current Phase 1 find-bit bench anchor packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
;

const current_master_gap_window =
    bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

const intended_live_check_window =
    bench_self_test_step ++
    "\n\n" ++
    bench_live_check_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

const WorkflowWindowStatus = enum {
    valid,
    missing_bench_live_check,
};

fn markerPosition(workflow_window: []const u8, marker: []const u8) ?usize {
    const first = std.mem.indexOf(u8, workflow_window, marker) orelse return null;
    const after_first = first + marker.len;
    if (std.mem.indexOf(u8, workflow_window[after_first..], marker) != null) return null;
    return first;
}

fn requireSingleMarker(workflow_window: []const u8, marker: []const u8) !usize {
    return markerPosition(workflow_window, marker) orelse {
        if (std.mem.indexOf(u8, workflow_window, marker) == null) return error.MissingWorkflowMarker;
        return error.DuplicateWorkflowMarker;
    };
}

fn optionalSingleMarker(workflow_window: []const u8, marker: []const u8) !?usize {
    const first = std.mem.indexOf(u8, workflow_window, marker) orelse return null;
    const after_first = first + marker.len;
    if (std.mem.indexOf(u8, workflow_window[after_first..], marker) != null) return error.DuplicateWorkflowMarker;
    return first;
}

fn requireBefore(earlier: usize, later: usize) !void {
    if (earlier >= later) return error.WorkflowMarkerOutOfOrder;
}

fn classifyPhase1BenchWorkflowWindow(workflow_window: []const u8) !WorkflowWindowStatus {
    const bench_self_test = try requireSingleMarker(workflow_window, bench_self_test_step);
    const find_bit_self_test = try requireSingleMarker(workflow_window, find_bit_bench_self_test_step);
    const find_bit_live_check = try requireSingleMarker(workflow_window, find_bit_bench_live_check_step);
    try requireBefore(bench_self_test, find_bit_self_test);
    try requireBefore(find_bit_self_test, find_bit_live_check);

    const bench_live_check = (try optionalSingleMarker(workflow_window, bench_live_check_step)) orelse return .missing_bench_live_check;
    try requireBefore(bench_self_test, bench_live_check);
    try requireBefore(bench_live_check, find_bit_self_test);

    return .valid;
}

test "lane17 bench workflow live-check window identifies current master gap" {
    try std.testing.expectEqual(
        WorkflowWindowStatus.missing_bench_live_check,
        try classifyPhase1BenchWorkflowWindow(current_master_gap_window),
    );
}

test "lane17 bench workflow live-check window accepts intended insertion" {
    try std.testing.expectEqual(
        WorkflowWindowStatus.valid,
        try classifyPhase1BenchWorkflowWindow(intended_live_check_window),
    );
}

test "lane17 bench workflow live-check window rejects duplicate live bench check" {
    const duplicate_live_check_window =
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

    try std.testing.expectError(
        error.DuplicateWorkflowMarker,
        classifyPhase1BenchWorkflowWindow(duplicate_live_check_window),
    );
}

test "lane17 bench workflow live-check window rejects late live bench check" {
    const late_live_check_window =
        bench_self_test_step ++
        "\n\n" ++
        find_bit_bench_self_test_step ++
        "\n\n" ++
        bench_live_check_step ++
        "\n\n" ++
        find_bit_bench_live_check_step ++
        "\n";

    try std.testing.expectError(
        error.WorkflowMarkerOutOfOrder,
        classifyPhase1BenchWorkflowWindow(late_live_check_window),
    );
}
