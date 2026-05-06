const std = @import("std");
const sample = @import("bytestream_fifo_sample");

test "phase 5 bytestream fifo sample stays in the reference-sample lane" {
    const descriptor = sample.BytestreamFifoSample.descriptor();
    const contract = sample.BytestreamFifoSample.reviewContract();
    const expected_non_goals = [_][]const u8{
        "procfs parity",
        "kfifo_from_user or kfifo_to_user parity",
        "loadable module registration",
        "locking or blocking semantics",
    };

    try std.testing.expectEqualStrings("bytestream_fifo", descriptor.name);
    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
    try std.testing.expectEqual(sample.StorageBacking.embedded_fixed_buffer, descriptor.storage_backing);
    try std.testing.expectEqual(@as(usize, 7), contract.focus.len);
    try std.testing.expectEqual(sample.SampleFocus.bounded_fifo_order, contract.focus[0]);
    try std.testing.expectEqual(sample.SampleFocus.wraparound_requeue, contract.focus[1]);
    try std.testing.expectEqual(sample.SampleFocus.peek_and_skip, contract.focus[2]);
    try std.testing.expectEqual(sample.SampleFocus.non_destructive_snapshot, contract.focus[3]);
    try std.testing.expectEqual(sample.SampleFocus.preview_truncation, contract.focus[4]);
    try std.testing.expectEqual(sample.SampleFocus.reset_and_replay, contract.focus[5]);
    try std.testing.expectEqual(sample.SampleFocus.ownership_and_lifetime, contract.focus[6]);
    try std.testing.expectEqual(@as(usize, expected_non_goals.len), contract.non_goals.len);
    for (expected_non_goals, contract.non_goals) |expected, actual| {
        try std.testing.expectEqualStrings(expected, actual);
    }
}

test "phase 5 bytestream fifo sample replays exact queue behavior from the Linux anchor" {
    var module = sample.BytestreamFifoSample{};
    try module.init();
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 5), replay.initial_string_copy_count);
    try std.testing.expectEqual(@as(usize, 15), replay.len_after_initial_fill);
    try std.testing.expectEqualStrings("hello", replay.first_out[0..]);
    try std.testing.expectEqual(@as(usize, 5), replay.first_drain_count);
    try std.testing.expectEqualSlices(u8, &.{ 0, 1 }, replay.second_out[0..]);
    try std.testing.expectEqual(@as(usize, 2), replay.second_drain_count);
    try std.testing.expectEqual(@as(usize, 2), replay.requeue_count);
    try std.testing.expectEqual(@as(u8, 2), replay.skipped_byte);
    try std.testing.expectEqual(@as(u8, 3), replay.peek_value);
    try std.testing.expectEqual(@as(usize, 8), replay.preview_len);
    try std.testing.expect(replay.preview_truncated);
    try std.testing.expectEqualSlices(u8, sample.expected_anchor_result[0..8], replay.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), replay.snapshot_len);
    try std.testing.expectEqualSlices(u8, sample.expected_anchor_result[0..], replay.snapshot_sequence[0..]);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), replay.final_len);
    try std.testing.expectEqual(sample.StorageBacking.embedded_fixed_buffer, replay.storage_backing);
    try std.testing.expectEqual(@as(usize, 7), replay.checked_focus.len);
    try std.testing.expectEqual(sample.SampleFocus.bounded_fifo_order, replay.checked_focus[0]);
    try std.testing.expectEqual(sample.SampleFocus.wraparound_requeue, replay.checked_focus[1]);
    try std.testing.expectEqual(sample.SampleFocus.peek_and_skip, replay.checked_focus[2]);
    try std.testing.expectEqual(sample.SampleFocus.non_destructive_snapshot, replay.checked_focus[3]);
    try std.testing.expectEqual(sample.SampleFocus.preview_truncation, replay.checked_focus[4]);
    try std.testing.expectEqual(sample.SampleFocus.reset_and_replay, replay.checked_focus[5]);
    try std.testing.expectEqual(sample.SampleFocus.ownership_and_lifetime, replay.checked_focus[6]);
    try std.testing.expectEqualSlices(u8, sample.expected_anchor_result[0..], replay.final_sequence[0..]);
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());
}

test "phase 5 bytestream fifo sample keeps bounded helper behavior explicit" {
    var module = sample.BytestreamFifoSample{};
    var preview_buf: [4]u8 = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const empty_preview = module.previewInto(preview_buf[0..]);

    try std.testing.expectEqual(@as(usize, 0), empty_preview.copied);
    try std.testing.expectEqual(@as(usize, 0), empty_preview.total_visible);
    try std.testing.expect(!empty_preview.truncated);
    try std.testing.expectEqualSlices(u8, &.{ 0xaa, 0xaa, 0xaa, 0xaa }, preview_buf[0..]);

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

    const short_drain = module.runShortDrainReplay();
    try std.testing.expectEqual(@as(usize, 5), short_drain.initial_copy_count);
    try std.testing.expectEqual(@as(usize, 3), short_drain.first_drain_count);
    try std.testing.expectEqualSlices(u8, "hel", short_drain.first_drain[0..]);
    try std.testing.expectEqual(@as(usize, 2), short_drain.remaining_snapshot_len);
    try std.testing.expectEqualSlices(u8, "lo", short_drain.remaining_snapshot[0..]);
    try std.testing.expectEqual(@as(usize, 2), short_drain.remaining_drain_count);
    try std.testing.expectEqualSlices(u8, "lo", short_drain.remaining_drain[0..]);
    try std.testing.expectEqual(@as(usize, 0), short_drain.empty_follow_up_drain_count);
    try std.testing.expectEqual(@as(usize, 0), module.count());
}

test "phase 5 bytestream fifo sample makes preview truncation and lifetime boundaries explicit" {
    var module = sample.BytestreamFifoSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runPreviewBoundaryReplay());
    try module.init();

    const preview_replay = try module.runPreviewBoundaryReplay();
    try std.testing.expectEqual(sample.SampleStage.initialized, preview_replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.initialized, preview_replay.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 4), preview_replay.snapshot_len);
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5 }, preview_replay.snapshot_prefix[0..]);
    try std.testing.expectEqual(@as(usize, 8), preview_replay.preview_len);
    try std.testing.expectEqual(@as(usize, 10), preview_replay.preview_total_visible);
    try std.testing.expect(preview_replay.preview_truncated);
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5, 6, 7, 8, 9 }, preview_replay.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, 10), preview_replay.queue_len_after_preview);
    try std.testing.expectEqual(@as(usize, 3), preview_replay.checked_focus.len);

    _ = try module.runAnchorReplay();
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());
    const replay_lifecycle = module.lifecycleSummary();
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), replay_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay_lifecycle.queue_len);
    try std.testing.expectEqual(sample.StorageBacking.embedded_fixed_buffer, replay_lifecycle.storage_backing);

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runPreviewBoundaryReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}
