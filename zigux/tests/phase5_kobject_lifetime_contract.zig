const std = @import("std");
const companion = @import("kobject_lifetime_contract");

test "phase 5 kobject lifetime companion keeps the anchor-local lifecycle packet reviewable through a focused test surface" {
    const contract = companion.referencePattern();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", contract.anchor);
    try std.testing.expectEqualStrings("kobject_example", contract.directory);
    try std.testing.expectEqual(companion.SampleStage.cold, contract.stage_sequence[0].stage);
    try std.testing.expectEqual(companion.SampleStage.initialized, contract.stage_sequence[1].stage);
    try std.testing.expectEqual(companion.SampleStage.registered, contract.stage_sequence[2].stage);
    try std.testing.expectEqual(companion.SampleStage.exited, contract.stage_sequence[3].stage);
    try std.testing.expectEqual(@as(usize, 0), contract.stage_sequence[0].active_attr_count);
    try std.testing.expectEqual(@as(usize, 0), contract.stage_sequence[1].active_attr_count);
    try std.testing.expectEqual(@as(usize, 3), contract.stage_sequence[2].active_attr_count);
    try std.testing.expectEqual(@as(usize, 0), contract.stage_sequence[3].active_attr_count);
}

test "phase 5 kobject lifetime companion keeps replay readiness, exit split, and counters explicit" {
    const contract = companion.referencePattern();
    const expected_replay_ready = [_]bool{ false, true, false, false };
    const expected_counts = [_]usize{ 0, 0, 3, 0 };

    inline for (expected_replay_ready, expected_counts, 0..) |replay_ready, active_attr_count, idx| {
        try std.testing.expectEqual(replay_ready, contract.stage_sequence[idx].replay_ready);
        try std.testing.expectEqual(active_attr_count, contract.stage_sequence[idx].active_attr_count);
    }

    try std.testing.expectEqual(companion.ExitDisposition.abandoned_before_registration, contract.initialized_exit_disposition);
    try std.testing.expectEqual(companion.ExitDisposition.tore_down_registered_attributes, contract.registered_exit_disposition);
    try std.testing.expectEqual(@as(usize, 0), contract.initialized_exit_cleared_attr_count);
    try std.testing.expectEqual(@as(usize, 3), contract.registered_exit_cleared_attr_count);
    try std.testing.expect(contract.values_reset_on_exit);
    try std.testing.expect(contract.counters_progress_monotonic);
    try std.testing.expectEqual(@as(usize, 1), contract.stage_sequence[1].counters.init_runs);
    try std.testing.expectEqual(@as(usize, 1), contract.stage_sequence[2].counters.register_runs);
    try std.testing.expectEqual(@as(usize, 1), contract.stage_sequence[3].counters.exit_runs);
}
