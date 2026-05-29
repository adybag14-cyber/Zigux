const std = @import("std");

const bench_self_test_step =
    "      - name: Self-test current Phase 1 bench checker\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench.py --self-test";

const bench_live_check_step =
    "      - name: Check current Phase 1 bench packet\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench.py";

const find_bit_bench_self_test_step =
    "      - name: Self-test current Phase 1 find-bit bench anchor checker\n" ++
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test";

const find_bit_bench_live_check_step =
    "      - name: Check current Phase 1 find-bit bench anchor packet\n" ++
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py";

const missing_bench_live_check =
    bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

const expected_bench_live_check_patch =
    bench_self_test_step ++
    "\n\n" ++
    bench_live_check_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

const duplicate_bench_live_check =
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

const reordered_bench_live_check =
    bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    bench_live_check_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

fn countMarkers(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

fn requireSingleMarker(haystack: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingWorkflowMarker;
    if (std.mem.indexOfPos(u8, haystack, first + needle.len, needle) != null) {
        return error.DuplicateWorkflowMarker;
    }
    return first;
}

fn requirePatchableBenchHandoff(workflow: []const u8) !void {
    const bench_self_test = try requireSingleMarker(workflow, bench_self_test_step);
    if (countMarkers(workflow, bench_live_check_step) != 0) {
        return error.LiveBenchCheckAlreadyPresent;
    }
    const find_bit_bench_self_test = try requireSingleMarker(workflow, find_bit_bench_self_test_step);
    if (bench_self_test >= find_bit_bench_self_test) {
        return error.WorkflowMarkerOutOfOrder;
    }
}

fn requirePatchedBenchHandoff(workflow: []const u8) !void {
    const bench_self_test = try requireSingleMarker(workflow, bench_self_test_step);
    const bench_live_check = try requireSingleMarker(workflow, bench_live_check_step);
    const find_bit_bench_self_test = try requireSingleMarker(workflow, find_bit_bench_self_test_step);
    const find_bit_bench_live_check = try requireSingleMarker(workflow, find_bit_bench_live_check_step);

    if (bench_self_test >= bench_live_check) return error.WorkflowMarkerOutOfOrder;
    if (bench_live_check >= find_bit_bench_self_test) return error.WorkflowMarkerOutOfOrder;
    if (find_bit_bench_self_test >= find_bit_bench_live_check) return error.WorkflowMarkerOutOfOrder;
}

test "lane17 bench live step patch accepts current missing-live-check shape" {
    try requirePatchableBenchHandoff(missing_bench_live_check);
}

test "lane17 bench live step patch accepts exact expected patched handoff" {
    try requirePatchedBenchHandoff(expected_bench_live_check_patch);
}

test "lane17 bench live step patch rejects duplicate insertion" {
    try std.testing.expectError(
        error.LiveBenchCheckAlreadyPresent,
        requirePatchableBenchHandoff(expected_bench_live_check_patch),
    );
    try std.testing.expectError(
        error.DuplicateWorkflowMarker,
        requirePatchedBenchHandoff(duplicate_bench_live_check),
    );
}

test "lane17 bench live step patch rejects reordered insertion" {
    try std.testing.expectError(
        error.WorkflowMarkerOutOfOrder,
        requirePatchedBenchHandoff(reordered_bench_live_check),
    );
}
