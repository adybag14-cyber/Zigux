const std = @import("std");

const bench_self_test = "Self-test current Phase 1 bench checker";
const bench_live_check = "Check current Phase 1 bench packet";
const find_bit_bench_self_test = "Self-test current Phase 1 find-bit bench anchor checker";
const find_bit_bench_live_check = "Check current Phase 1 find-bit bench anchor packet";

const WorkflowGapError = error{
    MissingBenchSelfTest,
    MissingBenchLiveCheck,
    MissingFindBitBenchSelfTest,
    MissingFindBitBenchLiveCheck,
    DuplicateBenchLiveCheck,
    BenchLiveCheckBeforeSelfTest,
    BenchLiveCheckAfterFindBitSelfTest,
    FindBitLiveCheckBeforeFindBitSelfTest,
};

fn requireOnce(haystack: []const u8, needle: []const u8, missing: WorkflowGapError) WorkflowGapError!usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return missing;
    const next_start = first + needle.len;
    if (std.mem.indexOf(u8, haystack[next_start..], needle) != null) return error.DuplicateBenchLiveCheck;
    return first;
}

fn requirePhase1BenchWindow(workflow: []const u8) WorkflowGapError!void {
    const bench_self = try requireOnce(workflow, bench_self_test, error.MissingBenchSelfTest);
    const bench_live = try requireOnce(workflow, bench_live_check, error.MissingBenchLiveCheck);
    const find_bit_self = try requireOnce(workflow, find_bit_bench_self_test, error.MissingFindBitBenchSelfTest);
    const find_bit_live = try requireOnce(workflow, find_bit_bench_live_check, error.MissingFindBitBenchLiveCheck);

    if (bench_live < bench_self) return error.BenchLiveCheckBeforeSelfTest;
    if (find_bit_self < bench_live) return error.BenchLiveCheckAfterFindBitSelfTest;
    if (find_bit_live < find_bit_self) return error.FindBitLiveCheckBeforeFindBitSelfTest;
}

test "current master bench gap is rejected until the live packet check exists" {
    const current_gap =
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
        \\
        \\      - name: Check current Phase 1 find-bit bench anchor packet
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
    ;

    try std.testing.expectError(error.MissingBenchLiveCheck, requirePhase1BenchWindow(current_gap));
}

test "intended live bench packet window is accepted" {
    const intended_window =
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
        \\
        \\      - name: Check current Phase 1 find-bit bench anchor packet
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
    ;

    try requirePhase1BenchWindow(intended_window);
}

test "bench live check must stay before find-bit bench anchors" {
    const misplaced_live_check =
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
        \\
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
        \\
        \\      - name: Check current Phase 1 find-bit bench anchor packet
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
    ;

    try std.testing.expectError(error.BenchLiveCheckAfterFindBitSelfTest, requirePhase1BenchWindow(misplaced_live_check));
}

test "bench live check must not be duplicated" {
    const duplicated_live_check =
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
        \\
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
        \\
        \\      - name: Check current Phase 1 find-bit bench anchor packet
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
    ;

    try std.testing.expectError(error.DuplicateBenchLiveCheck, requirePhase1BenchWindow(duplicated_live_check));
}
