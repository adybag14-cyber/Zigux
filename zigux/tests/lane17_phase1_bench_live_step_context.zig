const std = @import("std");

const Step = struct {
    name: []const u8,
    run: []const u8,
};

const BenchContextError = error{
    MissingRequiredStep,
    DuplicateLiveBenchStep,
    UnexpectedCommand,
    WrongStepOrder,
};

const route_summary_name = "Check current Phase 1 route summary packet";
const bench_self_name = "Self-test current Phase 1 bench checker";
const bench_live_name = "Check current Phase 1 bench packet";
const find_bit_self_name = "Self-test current Phase 1 find-bit bench anchor checker";
const find_bit_live_name = "Check current Phase 1 find-bit bench anchor packet";
const shared_reminder_name = "Self-test current Phase 1 shared reminder checker";

const route_summary_run = "python3 scripts/zigux/check-phase1-route-summary-counts.py";
const bench_self_run = "python3 scripts/zigux/check-phase1-bench.py --self-test";
const bench_live_run = "python3 scripts/zigux/check-phase1-bench.py";
const find_bit_self_run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test";
const find_bit_live_run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py";
const shared_reminder_run = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test";

fn findStep(steps: []const Step, name: []const u8) ?usize {
    for (steps, 0..) |step, index| {
        if (std.mem.eql(u8, step.name, name)) return index;
    }
    return null;
}

fn countSteps(steps: []const Step, name: []const u8) usize {
    var count: usize = 0;
    for (steps) |step| {
        if (std.mem.eql(u8, step.name, name)) count += 1;
    }
    return count;
}

fn requireStep(steps: []const Step, name: []const u8, run: []const u8) BenchContextError!usize {
    const index = findStep(steps, name) orelse return BenchContextError.MissingRequiredStep;
    if (!std.mem.eql(u8, steps[index].run, run)) return BenchContextError.UnexpectedCommand;
    return index;
}

fn expectIncreasing(indices: []const usize) BenchContextError!void {
    for (indices[1..], 1..) |index, offset| {
        if (indices[offset - 1] >= index) return BenchContextError.WrongStepOrder;
    }
}

fn expectBenchLiveStepContext(steps: []const Step) BenchContextError!void {
    if (countSteps(steps, bench_live_name) > 1) return BenchContextError.DuplicateLiveBenchStep;

    const route_summary = try requireStep(steps, route_summary_name, route_summary_run);
    const bench_self = try requireStep(steps, bench_self_name, bench_self_run);
    const bench_live = try requireStep(steps, bench_live_name, bench_live_run);
    const find_bit_self = try requireStep(steps, find_bit_self_name, find_bit_self_run);
    const find_bit_live = try requireStep(steps, find_bit_live_name, find_bit_live_run);
    const shared_reminder = try requireStep(steps, shared_reminder_name, shared_reminder_run);

    try expectIncreasing(&.{
        route_summary,
        bench_self,
        bench_live,
        find_bit_self,
        find_bit_live,
        shared_reminder,
    });
}

test "accepts the intended Phase 1 bench live-check workflow context" {
    const steps = [_]Step{
        .{ .name = route_summary_name, .run = route_summary_run },
        .{ .name = bench_self_name, .run = bench_self_run },
        .{ .name = bench_live_name, .run = bench_live_run },
        .{ .name = find_bit_self_name, .run = find_bit_self_run },
        .{ .name = find_bit_live_name, .run = find_bit_live_run },
        .{ .name = shared_reminder_name, .run = shared_reminder_run },
    };

    try expectBenchLiveStepContext(&steps);
}

test "rejects the current missing Phase 1 bench live-check slot" {
    const steps = [_]Step{
        .{ .name = route_summary_name, .run = route_summary_run },
        .{ .name = bench_self_name, .run = bench_self_run },
        .{ .name = find_bit_self_name, .run = find_bit_self_run },
        .{ .name = find_bit_live_name, .run = find_bit_live_run },
        .{ .name = shared_reminder_name, .run = shared_reminder_run },
    };

    try std.testing.expectError(BenchContextError.MissingRequiredStep, expectBenchLiveStepContext(&steps));
}

test "rejects a Phase 1 bench live check before its self-test" {
    const steps = [_]Step{
        .{ .name = route_summary_name, .run = route_summary_run },
        .{ .name = bench_live_name, .run = bench_live_run },
        .{ .name = bench_self_name, .run = bench_self_run },
        .{ .name = find_bit_self_name, .run = find_bit_self_run },
        .{ .name = find_bit_live_name, .run = find_bit_live_run },
        .{ .name = shared_reminder_name, .run = shared_reminder_run },
    };

    try std.testing.expectError(BenchContextError.WrongStepOrder, expectBenchLiveStepContext(&steps));
}

test "rejects duplicate Phase 1 bench live checks" {
    const steps = [_]Step{
        .{ .name = route_summary_name, .run = route_summary_run },
        .{ .name = bench_self_name, .run = bench_self_run },
        .{ .name = bench_live_name, .run = bench_live_run },
        .{ .name = bench_live_name, .run = bench_live_run },
        .{ .name = find_bit_self_name, .run = find_bit_self_run },
        .{ .name = find_bit_live_name, .run = find_bit_live_run },
        .{ .name = shared_reminder_name, .run = shared_reminder_run },
    };

    try std.testing.expectError(BenchContextError.DuplicateLiveBenchStep, expectBenchLiveStepContext(&steps));
}

test "rejects a live Phase 1 bench step wired to the self-test command" {
    const steps = [_]Step{
        .{ .name = route_summary_name, .run = route_summary_run },
        .{ .name = bench_self_name, .run = bench_self_run },
        .{ .name = bench_live_name, .run = bench_self_run },
        .{ .name = find_bit_self_name, .run = find_bit_self_run },
        .{ .name = find_bit_live_name, .run = find_bit_live_run },
        .{ .name = shared_reminder_name, .run = shared_reminder_run },
    };

    try std.testing.expectError(BenchContextError.UnexpectedCommand, expectBenchLiveStepContext(&steps));
}

test "rejects a mutated find-bit bench handoff after the live bench check" {
    const steps = [_]Step{
        .{ .name = route_summary_name, .run = route_summary_run },
        .{ .name = bench_self_name, .run = bench_self_run },
        .{ .name = bench_live_name, .run = bench_live_run },
        .{ .name = find_bit_self_name, .run = find_bit_self_run },
        .{ .name = find_bit_live_name, .run = find_bit_self_run },
        .{ .name = shared_reminder_name, .run = shared_reminder_run },
    };

    try std.testing.expectError(BenchContextError.UnexpectedCommand, expectBenchLiveStepContext(&steps));
}
