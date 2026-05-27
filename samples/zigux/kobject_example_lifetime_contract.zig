const std = @import("std");

pub const linux_anchor = "samples/kobject/kobject-example.c";
pub const directory_name = "kobject_example";

pub const SampleStage = enum {
    cold,
    initialized,
    registered,
    exited,
};

pub const ExitDisposition = enum {
    abandoned_before_registration,
    tore_down_registered_attributes,
};

pub const CounterSnapshot = struct {
    init_runs: usize,
    register_runs: usize,
    exit_runs: usize,
};

pub const LifecycleSnapshot = struct {
    stage: SampleStage,
    active_attr_count: usize,
    replay_ready: bool,
    counters: CounterSnapshot,
};

pub const LifetimeContract = struct {
    anchor: []const u8,
    directory: []const u8,
    stage_sequence: [4]LifecycleSnapshot,
    initialized_exit_disposition: ExitDisposition,
    registered_exit_disposition: ExitDisposition,
    initialized_exit_cleared_attr_count: usize,
    registered_exit_cleared_attr_count: usize,
    values_reset_on_exit: bool,
    counters_progress_monotonic: bool,
};

pub fn referencePattern() LifetimeContract {
    const stages = [_]LifecycleSnapshot{
        .{
            .stage = .cold,
            .active_attr_count = 0,
            .replay_ready = false,
            .counters = .{ .init_runs = 0, .register_runs = 0, .exit_runs = 0 },
        },
        .{
            .stage = .initialized,
            .active_attr_count = 0,
            .replay_ready = true,
            .counters = .{ .init_runs = 1, .register_runs = 0, .exit_runs = 0 },
        },
        .{
            .stage = .registered,
            .active_attr_count = 3,
            .replay_ready = false,
            .counters = .{ .init_runs = 1, .register_runs = 1, .exit_runs = 0 },
        },
        .{
            .stage = .exited,
            .active_attr_count = 0,
            .replay_ready = false,
            .counters = .{ .init_runs = 1, .register_runs = 1, .exit_runs = 1 },
        },
    };

    return .{
        .anchor = linux_anchor,
        .directory = directory_name,
        .stage_sequence = stages,
        .initialized_exit_disposition = .abandoned_before_registration,
        .registered_exit_disposition = .tore_down_registered_attributes,
        .initialized_exit_cleared_attr_count = 0,
        .registered_exit_cleared_attr_count = 3,
        .values_reset_on_exit = true,
        .counters_progress_monotonic = countersProgressMonotonic(stages),
    };
}

fn countersProgressMonotonic(stages: [4]LifecycleSnapshot) bool {
    return countersDoNotRegress(stages[0].counters, stages[1].counters) and
        countersDoNotRegress(stages[1].counters, stages[2].counters) and
        countersDoNotRegress(stages[2].counters, stages[3].counters);
}

fn countersDoNotRegress(previous: CounterSnapshot, next: CounterSnapshot) bool {
    return next.init_runs >= previous.init_runs and
        next.register_runs >= previous.register_runs and
        next.exit_runs >= previous.exit_runs;
}

test "kobject lifetime companion keeps the ownership stage sequence explicit" {
    const contract = referencePattern();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", contract.anchor);
    try std.testing.expectEqualStrings("kobject_example", contract.directory);
    try std.testing.expectEqual(SampleStage.cold, contract.stage_sequence[0].stage);
    try std.testing.expectEqual(SampleStage.initialized, contract.stage_sequence[1].stage);
    try std.testing.expectEqual(SampleStage.registered, contract.stage_sequence[2].stage);
    try std.testing.expectEqual(SampleStage.exited, contract.stage_sequence[3].stage);
    try std.testing.expectEqual(@as(usize, 0), contract.stage_sequence[0].active_attr_count);
    try std.testing.expectEqual(@as(usize, 0), contract.stage_sequence[1].active_attr_count);
    try std.testing.expectEqual(@as(usize, 3), contract.stage_sequence[2].active_attr_count);
    try std.testing.expectEqual(@as(usize, 0), contract.stage_sequence[3].active_attr_count);
    try std.testing.expect(!contract.stage_sequence[0].replay_ready);
    try std.testing.expect(contract.stage_sequence[1].replay_ready);
    try std.testing.expect(!contract.stage_sequence[2].replay_ready);
    try std.testing.expect(!contract.stage_sequence[3].replay_ready);
}

test "kobject lifetime companion keeps the exit split and counter progression explicit" {
    const contract = referencePattern();

    try std.testing.expectEqual(ExitDisposition.abandoned_before_registration, contract.initialized_exit_disposition);
    try std.testing.expectEqual(ExitDisposition.tore_down_registered_attributes, contract.registered_exit_disposition);
    try std.testing.expectEqual(@as(usize, 0), contract.initialized_exit_cleared_attr_count);
    try std.testing.expectEqual(@as(usize, 3), contract.registered_exit_cleared_attr_count);
    try std.testing.expect(contract.values_reset_on_exit);
    try std.testing.expect(contract.counters_progress_monotonic);
    try std.testing.expectEqual(@as(usize, 1), contract.stage_sequence[1].counters.init_runs);
    try std.testing.expectEqual(@as(usize, 1), contract.stage_sequence[2].counters.register_runs);
    try std.testing.expectEqual(@as(usize, 1), contract.stage_sequence[3].counters.exit_runs);
}
