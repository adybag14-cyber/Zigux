const std = @import("std");

const bench_self_test_step =
    \\      - name: Self-test current Phase 1 bench checker
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
;

const bench_live_check_step =
    \\      - name: Check current Phase 1 bench packet
    \\        run: python3 scripts/zigux/check-phase1-bench.py
;

const find_bit_self_test_step =
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
;

const find_bit_live_check_step =
    \\      - name: Check current Phase 1 find-bit bench anchor packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
;

const intended_phase1_bench_workflow_slice =
    bench_self_test_step ++ "\n\n" ++
    bench_live_check_step ++ "\n\n" ++
    find_bit_self_test_step ++ "\n\n" ++
    find_bit_live_check_step;

const current_missing_live_check_slice =
    bench_self_test_step ++ "\n\n" ++
    find_bit_self_test_step ++ "\n\n" ++
    find_bit_live_check_step;

const duplicate_live_check_slice =
    bench_self_test_step ++ "\n\n" ++
    bench_live_check_step ++ "\n\n" ++
    bench_live_check_step ++ "\n\n" ++
    find_bit_self_test_step ++ "\n\n" ++
    find_bit_live_check_step;

const self_test_only_live_check_slice =
    bench_self_test_step ++ "\n\n" ++
    \\      - name: Check current Phase 1 bench packet
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
    ++ "\n\n" ++
    find_bit_self_test_step ++ "\n\n" ++
    find_bit_live_check_step;

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative_index| {
        count += 1;
        offset += relative_index + needle.len;
    }
    return count;
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingRequiredWorkflowStep;
}

fn hasAppliedBenchLiveWorkflowContract(workflow_slice: []const u8) bool {
    if (countOccurrences(workflow_slice, bench_live_check_step) != 1) return false;
    if (countOccurrences(workflow_slice, "run: python3 scripts/zigux/check-phase1-bench.py --self-test") != 1) return false;
    if (contains(workflow_slice, "Check current Phase 1 bench packet\n        run: python3 scripts/zigux/check-phase1-bench.py --self-test")) return false;

    const bench_self_test_index = indexOfRequired(workflow_slice, bench_self_test_step) catch return false;
    const bench_live_check_index = indexOfRequired(workflow_slice, bench_live_check_step) catch return false;
    const find_bit_self_test_index = indexOfRequired(workflow_slice, find_bit_self_test_step) catch return false;
    const find_bit_live_check_index = indexOfRequired(workflow_slice, find_bit_live_check_step) catch return false;

    return bench_self_test_index < bench_live_check_index and
        bench_live_check_index < find_bit_self_test_index and
        find_bit_self_test_index < find_bit_live_check_index;
}

test "lane17 applied bench workflow contract accepts the live check between both bench self-tests" {
    try std.testing.expect(hasAppliedBenchLiveWorkflowContract(intended_phase1_bench_workflow_slice));
}

test "lane17 applied bench workflow contract rejects current missing live check shape" {
    try std.testing.expect(!hasAppliedBenchLiveWorkflowContract(current_missing_live_check_slice));
}

test "lane17 applied bench workflow contract rejects duplicate live checks" {
    try std.testing.expect(!hasAppliedBenchLiveWorkflowContract(duplicate_live_check_slice));
}

test "lane17 applied bench workflow contract rejects a live step that only reruns the self-test" {
    try std.testing.expect(!hasAppliedBenchLiveWorkflowContract(self_test_only_live_check_slice));
}
