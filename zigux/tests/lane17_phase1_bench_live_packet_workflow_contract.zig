const std = @import("std");

const bench_self_test_name = "Self-test current Phase 1 bench checker";
const bench_self_test_run = "python3 scripts/zigux/check-phase1-bench.py --self-test";
const bench_live_name = "Check current Phase 1 bench packet";
const bench_live_run = "python3 scripts/zigux/check-phase1-bench.py";
const find_bit_self_test_name = "Self-test current Phase 1 find-bit bench anchor checker";
const find_bit_self_test_run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test";

const WorkflowStep = struct {
    name: []const u8,
    run: []const u8,
};

const StepError = error{
    MissingBenchSelfTest,
    MissingBenchLivePacket,
    MissingFindBitBenchSelfTest,
    DuplicateBenchLivePacket,
    BenchLiveBeforeSelfTest,
    BenchLiveAfterFindBitBenchSelfTest,
    BenchLiveCommandDrift,
};

fn findStep(steps: []const WorkflowStep, name: []const u8) ?usize {
    for (steps, 0..) |step, index| {
        if (std.mem.eql(u8, step.name, name)) return index;
    }
    return null;
}

fn countStep(steps: []const WorkflowStep, name: []const u8) usize {
    var count: usize = 0;
    for (steps) |step| {
        if (std.mem.eql(u8, step.name, name)) count += 1;
    }
    return count;
}

fn requireBenchLivePacketWorkflow(steps: []const WorkflowStep) StepError!void {
    const self_index = findStep(steps, bench_self_test_name) orelse return StepError.MissingBenchSelfTest;
    const live_index = findStep(steps, bench_live_name) orelse return StepError.MissingBenchLivePacket;
    const find_bit_index = findStep(steps, find_bit_self_test_name) orelse return StepError.MissingFindBitBenchSelfTest;

    if (countStep(steps, bench_live_name) != 1) return StepError.DuplicateBenchLivePacket;
    if (live_index <= self_index) return StepError.BenchLiveBeforeSelfTest;
    if (find_bit_index <= live_index) return StepError.BenchLiveAfterFindBitBenchSelfTest;
    if (!std.mem.eql(u8, steps[live_index].run, bench_live_run)) return StepError.BenchLiveCommandDrift;
}

test "Lane 17 bench live packet is between bench self-test and find-bit bench" {
    const steps = [_]WorkflowStep{
        .{ .name = bench_self_test_name, .run = bench_self_test_run },
        .{ .name = bench_live_name, .run = bench_live_run },
        .{ .name = find_bit_self_test_name, .run = find_bit_self_test_run },
    };

    try requireBenchLivePacketWorkflow(&steps);
}

test "current missing live packet gap is rejected" {
    const steps = [_]WorkflowStep{
        .{ .name = bench_self_test_name, .run = bench_self_test_run },
        .{ .name = find_bit_self_test_name, .run = find_bit_self_test_run },
    };

    try std.testing.expectError(StepError.MissingBenchLivePacket, requireBenchLivePacketWorkflow(&steps));
}

test "bench live packet cannot reuse the self-test command" {
    const steps = [_]WorkflowStep{
        .{ .name = bench_self_test_name, .run = bench_self_test_run },
        .{ .name = bench_live_name, .run = bench_self_test_run },
        .{ .name = find_bit_self_test_name, .run = find_bit_self_test_run },
    };

    try std.testing.expectError(StepError.BenchLiveCommandDrift, requireBenchLivePacketWorkflow(&steps));
}

test "bench live packet cannot drift after the find-bit bench anchor" {
    const steps = [_]WorkflowStep{
        .{ .name = bench_self_test_name, .run = bench_self_test_run },
        .{ .name = find_bit_self_test_name, .run = find_bit_self_test_run },
        .{ .name = bench_live_name, .run = bench_live_run },
    };

    try std.testing.expectError(StepError.BenchLiveAfterFindBitBenchSelfTest, requireBenchLivePacketWorkflow(&steps));
}

test "duplicate bench live packet steps fail closed" {
    const steps = [_]WorkflowStep{
        .{ .name = bench_self_test_name, .run = bench_self_test_run },
        .{ .name = bench_live_name, .run = bench_live_run },
        .{ .name = bench_live_name, .run = bench_live_run },
        .{ .name = find_bit_self_test_name, .run = find_bit_self_test_run },
    };

    try std.testing.expectError(StepError.DuplicateBenchLivePacket, requireBenchLivePacketWorkflow(&steps));
}
