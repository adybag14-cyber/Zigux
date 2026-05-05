const std = @import("std");
const sample = @import("bytestream_fifo_sample");

test "phase 5 bytestream fifo sample stays in the reference-sample lane" {
    const descriptor = sample.BytestreamFifoSample.descriptor();

    try std.testing.expectEqualStrings("bytestream_fifo", descriptor.name);
    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
}

test "phase 5 bytestream fifo sample replays exact queue behavior from the Linux anchor" {
    var module = sample.BytestreamFifoSample{};
    try module.init();
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 15), replay.len_after_initial_fill);
    try std.testing.expectEqualStrings("hello", replay.first_out[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 0, 1 }, replay.second_out[0..]);
    try std.testing.expectEqual(@as(u8, 2), replay.skipped_byte);
    try std.testing.expectEqual(@as(u8, 3), replay.peek_value);
    try std.testing.expectEqual(@as(u8, 20), replay.fill_start);
    try std.testing.expectEqual(@as(u8, 42), replay.fill_end);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), replay.final_len);
    try std.testing.expectEqual(@as(usize, 5), replay.checked_focus.len);
    try std.testing.expectEqualSlices(u8, sample.expected_anchor_result[0..], replay.final_sequence[0..]);
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());
}

test "phase 5 bytestream fifo sample keeps bounded helper behavior explicit" {
    var module = sample.BytestreamFifoSample{};
    const helper_replay = module.runHelperBoundaryReplay();

    try std.testing.expectEqual(@as(?u8, null), helper_replay.peek_before_fill);
    try std.testing.expectEqual(@as(?u8, null), helper_replay.skip_before_fill);
    try std.testing.expectEqual(@as(usize, 0), helper_replay.empty_enqueue_len);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), helper_replay.count_at_capacity);
    try std.testing.expect(helper_replay.overflow_rejected);
    try std.testing.expectEqual(@as(u8, 0), helper_replay.peek_at_capacity);
    try std.testing.expectEqual(@as(u8, 0), helper_replay.skipped_at_capacity);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 1), helper_replay.count_after_skip);
    try std.testing.expectEqual(@as(usize, 0), helper_replay.count_after_reset);
    try std.testing.expectEqual(@as(?u8, null), helper_replay.pop_after_reset);
    try std.testing.expectEqual(@as(usize, 0), module.count());
}

test "phase 5 bytestream fifo sample makes ownership and lifetime boundaries explicit" {
    var module = sample.BytestreamFifoSample{};

    try std.testing.expectEqual(sample.SampleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());

    try module.init();
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());

    _ = try module.runAnchorReplay();
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}
