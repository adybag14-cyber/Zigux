const std = @import("std");

const ContractError = error{
    MissingBenchSelfTest,
    MissingBenchLiveCheck,
    MissingGuardSelfTest,
    MissingGuardLiveCheck,
    MissingFindBitBenchAnchor,
    DuplicateBenchLiveCheck,
    DuplicateGuardSelfTest,
    DuplicateGuardLiveCheck,
    BenchLiveCheckBeforeSelfTest,
    GuardSelfTestBeforeBenchLiveCheck,
    GuardLiveCheckBeforeGuardSelfTest,
    FindBitAnchorBeforeGuardLiveCheck,
    StepRunMismatch,
};

const bench_self_test_name = "      - name: Self-test current Phase 1 bench checker\n";
const bench_self_test_run = "        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n";
const bench_live_check_name = "      - name: Check current Phase 1 bench packet\n";
const bench_live_check_run = "        run: python3 scripts/zigux/check-phase1-bench.py\n";
const guard_self_test_name = "      - name: Self-test current Phase 1 bench live-check workflow guard\n";
const guard_self_test_run = "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test\n";
const guard_live_check_name = "      - name: Check current Phase 1 bench live-check workflow guard\n";
const guard_live_check_run = "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py\n";
const find_bit_anchor_name = "      - name: Self-test current Phase 1 find-bit bench anchor checker\n";

const intended_hook =
    bench_self_test_name ++
    bench_self_test_run ++
    "\n" ++
    bench_live_check_name ++
    bench_live_check_run ++
    "\n" ++
    guard_self_test_name ++
    guard_self_test_run ++
    "\n" ++
    guard_live_check_name ++
    guard_live_check_run ++
    "\n" ++
    find_bit_anchor_name ++
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\n";

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |idx| {
        count += 1;
        offset = idx + needle.len;
    }
    return count;
}

fn stepRunMatches(workflow: []const u8, step_name: []const u8, step_run: []const u8) bool {
    const step_index = std.mem.indexOf(u8, workflow, step_name) orelse return false;
    const after_step = workflow[step_index + step_name.len ..];
    const next_step_index = std.mem.indexOf(u8, after_step, "      - name: ") orelse after_step.len;
    const block = after_step[0..next_step_index];
    return std.mem.indexOf(u8, block, step_run) != null;
}

fn requireSingle(workflow: []const u8, needle: []const u8, missing: ContractError, duplicate: ?ContractError) ContractError!usize {
    const first = std.mem.indexOf(u8, workflow, needle) orelse return missing;
    const count = countNeedle(workflow, needle);
    if (count != 1) return duplicate orelse missing;
    return first;
}

fn validateBenchLiveGuardHook(workflow: []const u8) ContractError!void {
    const bench_self_test = std.mem.indexOf(u8, workflow, bench_self_test_name) orelse return ContractError.MissingBenchSelfTest;
    const bench_live_check = try requireSingle(workflow, bench_live_check_name, ContractError.MissingBenchLiveCheck, ContractError.DuplicateBenchLiveCheck);
    const guard_self_test = try requireSingle(workflow, guard_self_test_name, ContractError.MissingGuardSelfTest, ContractError.DuplicateGuardSelfTest);
    const guard_live_check = try requireSingle(workflow, guard_live_check_name, ContractError.MissingGuardLiveCheck, ContractError.DuplicateGuardLiveCheck);
    const find_bit_anchor = std.mem.indexOf(u8, workflow, find_bit_anchor_name) orelse return ContractError.MissingFindBitBenchAnchor;

    if (bench_live_check < bench_self_test) return ContractError.BenchLiveCheckBeforeSelfTest;
    if (guard_self_test < bench_live_check) return ContractError.GuardSelfTestBeforeBenchLiveCheck;
    if (guard_live_check < guard_self_test) return ContractError.GuardLiveCheckBeforeGuardSelfTest;
    if (find_bit_anchor < guard_live_check) return ContractError.FindBitAnchorBeforeGuardLiveCheck;

    if (!stepRunMatches(workflow, bench_self_test_name, bench_self_test_run)) return ContractError.StepRunMismatch;
    if (!stepRunMatches(workflow, bench_live_check_name, bench_live_check_run)) return ContractError.StepRunMismatch;
    if (!stepRunMatches(workflow, guard_self_test_name, guard_self_test_run)) return ContractError.StepRunMismatch;
    if (!stepRunMatches(workflow, guard_live_check_name, guard_live_check_run)) return ContractError.StepRunMismatch;
}

test "lane17 accepts intended Phase 1 bench live guard workflow hook" {
    try validateBenchLiveGuardHook(intended_hook);
}

test "lane17 rejects current missing live bench packet step" {
    const current_gap =
        bench_self_test_name ++
        bench_self_test_run ++
        "\n" ++
        find_bit_anchor_name ++
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\n";

    try std.testing.expectError(ContractError.MissingBenchLiveCheck, validateBenchLiveGuardHook(current_gap));
}

test "lane17 rejects duplicate live guard hook steps" {
    const duplicate_live_check = intended_hook ++ "\n" ++ bench_live_check_name ++ bench_live_check_run;
    try std.testing.expectError(ContractError.DuplicateBenchLiveCheck, validateBenchLiveGuardHook(duplicate_live_check));

    const duplicate_guard = intended_hook ++ "\n" ++ guard_live_check_name ++ guard_live_check_run;
    try std.testing.expectError(ContractError.DuplicateGuardLiveCheck, validateBenchLiveGuardHook(duplicate_guard));
}

test "lane17 rejects reordered guard handoff" {
    const reordered =
        bench_self_test_name ++
        bench_self_test_run ++
        "\n" ++
        guard_self_test_name ++
        guard_self_test_run ++
        "\n" ++
        bench_live_check_name ++
        bench_live_check_run ++
        "\n" ++
        guard_live_check_name ++
        guard_live_check_run ++
        "\n" ++
        find_bit_anchor_name ++
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\n";

    try std.testing.expectError(ContractError.GuardSelfTestBeforeBenchLiveCheck, validateBenchLiveGuardHook(reordered));
}

test "lane17 rejects command drift inside named hook blocks" {
    const drifted_run = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        intended_hook,
        guard_live_check_run,
        "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test\n",
    ) catch unreachable;
    defer std.testing.allocator.free(drifted_run);

    try std.testing.expectError(ContractError.StepRunMismatch, validateBenchLiveGuardHook(drifted_run));
}
