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
    try std.testing.expectEqual(@as(usize, 10), contract.focus.len);
    try std.testing.expectEqual(sample.SampleFocus.bounded_fifo_order, contract.focus[0]);
    try std.testing.expectEqual(sample.SampleFocus.wraparound_requeue, contract.focus[1]);
    try std.testing.expectEqual(sample.SampleFocus.peek_and_skip, contract.focus[2]);
    try std.testing.expectEqual(sample.SampleFocus.non_destructive_snapshot, contract.focus[3]);
    try std.testing.expectEqual(sample.SampleFocus.preview_truncation, contract.focus[4]);
    try std.testing.expectEqual(sample.SampleFocus.remaining_capacity, contract.focus[5]);
    try std.testing.expectEqual(sample.SampleFocus.queue_shape_boundaries, contract.focus[6]);
    try std.testing.expectEqual(sample.SampleFocus.helper_boundaries, contract.focus[7]);
    try std.testing.expectEqual(sample.SampleFocus.reset_and_replay, contract.focus[8]);
    try std.testing.expectEqual(sample.SampleFocus.ownership_and_lifetime, contract.focus[9]);
    try std.testing.expectEqual(@as(usize, expected_non_goals.len), contract.non_goals.len);
    for (expected_non_goals, contract.non_goals) |expected, actual| {
        try std.testing.expectEqualStrings(expected, actual);
    }
}

test "phase 5 bytestream fifo sample replays exact queue behavior from the Linux anchor" {
    const descriptor = sample.BytestreamFifoSample.descriptor();
    const contract = sample.BytestreamFifoSample.reviewContract();

    var module = sample.BytestreamFifoSample{};
    try module.init();
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqualStrings(descriptor.anchor, replay.anchor);
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
    try std.testing.expectEqual(@as(usize, contract.focus.len), replay.checked_focus.len);
    for (contract.focus, replay.checked_focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
    try std.testing.expectEqualSlices(u8, sample.expected_anchor_result[0..], replay.final_sequence[0..]);
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.available());
    try std.testing.expect(!module.usesWrappedStorageWindow());

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.available());
    try std.testing.expect(!module.usesWrappedStorageWindow());
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
    try std.testing.expectEqual(@as(usize, 1), helper_replay.checked_focus.len);
    try std.testing.expectEqual(sample.SampleFocus.helper_boundaries, helper_replay.checked_focus[0]);

    const short_drain = module.runShortDrainReplay();
    try std.testing.expectEqual(@as(usize, 5), short_drain.initial_copy_count);
    try std.testing.expectEqual(@as(usize, 3), short_drain.first_drain_count);
    try std.testing.expectEqualSlices(u8, "hel", short_drain.first_drain[0..]);
    try std.testing.expectEqual(@as(usize, 2), short_drain.remaining_snapshot_len);
    try std.testing.expectEqualSlices(u8, "lo", short_drain.remaining_snapshot[0..]);
    try std.testing.expectEqual(@as(usize, 2), short_drain.remaining_drain_count);
    try std.testing.expectEqualSlices(u8, "lo", short_drain.remaining_drain[0..]);
    try std.testing.expectEqual(@as(usize, 0), short_drain.empty_follow_up_drain_count);
    try std.testing.expectEqual(@as(usize, 1), short_drain.checked_focus.len);
    try std.testing.expectEqual(sample.SampleFocus.helper_boundaries, short_drain.checked_focus[0]);
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(sample.SampleStage.cold, module.stage());
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.available());
    try std.testing.expect(!module.usesWrappedStorageWindow());
}

test "phase 5 bytestream fifo sample keeps queue-shape boundaries explicit" {
    var module = sample.BytestreamFifoSample{};
    const queue_shape = try module.runQueueShapeReplay();

    try std.testing.expectEqual(sample.SampleStage.cold, queue_shape.stage_before_replay);

    try std.testing.expectEqual(sample.SampleStage.cold, queue_shape.cold.stage);
    try std.testing.expect(queue_shape.cold.is_empty);
    try std.testing.expect(!queue_shape.cold.is_full);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.cold.count);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), queue_shape.cold.available);
    try std.testing.expect(!queue_shape.cold.wrapped_window);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.cold.spans.first_span_len);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.cold.spans.second_span_len);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.cold.spans.total_visible);
    try std.testing.expect(!queue_shape.cold.spans.wrapped);

    try std.testing.expectEqual(sample.SampleStage.initialized, queue_shape.after_init.stage);
    try std.testing.expect(queue_shape.after_init.is_empty);
    try std.testing.expect(!queue_shape.after_init.is_full);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_init.count);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), queue_shape.after_init.available);
    try std.testing.expect(!queue_shape.after_init.wrapped_window);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_init.spans.first_span_len);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_init.spans.second_span_len);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_init.spans.total_visible);
    try std.testing.expect(!queue_shape.after_init.spans.wrapped);

    try std.testing.expectEqual(@as(usize, 5), queue_shape.hello_copy_count);
    try std.testing.expectEqual(sample.SampleStage.initialized, queue_shape.after_hello.stage);
    try std.testing.expect(!queue_shape.after_hello.is_empty);
    try std.testing.expect(!queue_shape.after_hello.is_full);
    try std.testing.expectEqual(@as(usize, 5), queue_shape.after_hello.count);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 5), queue_shape.after_hello.available);
    try std.testing.expect(!queue_shape.after_hello.wrapped_window);
    try std.testing.expectEqual(@as(usize, 5), queue_shape.after_hello.spans.first_span_len);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_hello.spans.second_span_len);
    try std.testing.expectEqual(@as(usize, 5), queue_shape.after_hello.spans.total_visible);
    try std.testing.expect(!queue_shape.after_hello.spans.wrapped);

    try std.testing.expectEqual(sample.SampleStage.initialized, queue_shape.at_capacity.stage);
    try std.testing.expect(!queue_shape.at_capacity.is_empty);
    try std.testing.expect(queue_shape.at_capacity.is_full);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), queue_shape.at_capacity.count);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.at_capacity.available);
    try std.testing.expect(!queue_shape.at_capacity.wrapped_window);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), queue_shape.at_capacity.spans.first_span_len);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.at_capacity.spans.second_span_len);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), queue_shape.at_capacity.spans.total_visible);
    try std.testing.expect(!queue_shape.at_capacity.spans.wrapped);
    try std.testing.expect(queue_shape.overflow_rejected);

    try std.testing.expectEqual(@as(u8, 'h'), queue_shape.skipped_at_capacity);
    try std.testing.expectEqual(sample.SampleStage.initialized, queue_shape.post_skip.stage);
    try std.testing.expect(!queue_shape.post_skip.is_empty);
    try std.testing.expect(!queue_shape.post_skip.is_full);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 1), queue_shape.post_skip.count);
    try std.testing.expectEqual(@as(usize, 1), queue_shape.post_skip.available);
    try std.testing.expect(!queue_shape.post_skip.wrapped_window);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 1), queue_shape.post_skip.spans.first_span_len);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.post_skip.spans.second_span_len);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 1), queue_shape.post_skip.spans.total_visible);
    try std.testing.expect(!queue_shape.post_skip.spans.wrapped);

    try std.testing.expectEqual(@as(u8, 255), queue_shape.refill_value);
    try std.testing.expectEqual(sample.SampleStage.initialized, queue_shape.wrapped_refill.stage);
    try std.testing.expect(!queue_shape.wrapped_refill.is_empty);
    try std.testing.expect(queue_shape.wrapped_refill.is_full);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), queue_shape.wrapped_refill.count);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.wrapped_refill.available);
    try std.testing.expect(queue_shape.wrapped_refill.wrapped_window);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 1), queue_shape.wrapped_refill.spans.first_span_len);
    try std.testing.expectEqual(@as(usize, 1), queue_shape.wrapped_refill.spans.second_span_len);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), queue_shape.wrapped_refill.spans.total_visible);
    try std.testing.expect(queue_shape.wrapped_refill.spans.wrapped);

    try std.testing.expectEqual(sample.SampleStage.initialized, queue_shape.after_reset.stage);
    try std.testing.expect(queue_shape.after_reset.is_empty);
    try std.testing.expect(!queue_shape.after_reset.is_full);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_reset.count);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), queue_shape.after_reset.available);
    try std.testing.expect(!queue_shape.after_reset.wrapped_window);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_reset.spans.first_span_len);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_reset.spans.second_span_len);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_reset.spans.total_visible);
    try std.testing.expect(!queue_shape.after_reset.spans.wrapped);

    try std.testing.expectEqual(sample.SampleStage.exited, queue_shape.after_exit.stage);
    try std.testing.expect(queue_shape.after_exit.is_empty);
    try std.testing.expect(!queue_shape.after_exit.is_full);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_exit.count);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), queue_shape.after_exit.available);
    try std.testing.expect(!queue_shape.after_exit.wrapped_window);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_exit.spans.first_span_len);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_exit.spans.second_span_len);
    try std.testing.expectEqual(@as(usize, 0), queue_shape.after_exit.spans.total_visible);
    try std.testing.expect(!queue_shape.after_exit.spans.wrapped);

    try std.testing.expectEqual(@as(usize, 1), queue_shape.init_runs);
    try std.testing.expectEqual(@as(usize, 1), queue_shape.exit_runs);
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.available());
    try std.testing.expect(!module.usesWrappedStorageWindow());
}

test "phase 5 bytestream fifo sample makes preview truncation and lifetime boundaries explicit" {
    var module = sample.BytestreamFifoSample{};

    const cold_lifecycle = module.lifecycleSummary();
    try std.testing.expectEqual(sample.SampleStage.cold, cold_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 0), cold_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), cold_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), cold_lifecycle.queue_len);
    try std.testing.expectEqual(sample.StorageBacking.embedded_fixed_buffer, cold_lifecycle.storage_backing);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runPreviewBoundaryReplay());
    try module.init();

    const initialized_lifecycle = module.lifecycleSummary();
    try std.testing.expectEqual(sample.SampleStage.initialized, initialized_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), initialized_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), initialized_lifecycle.queue_len);
    try std.testing.expectEqual(sample.StorageBacking.embedded_fixed_buffer, initialized_lifecycle.storage_backing);

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
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 10), preview_replay.available_after_preview);
    try std.testing.expect(!preview_replay.wrapped_window_after_preview);
    try std.testing.expectEqual(@as(usize, 10), preview_replay.visible_spans_after_preview.first_span_len);
    try std.testing.expectEqual(@as(usize, 0), preview_replay.visible_spans_after_preview.second_span_len);
    try std.testing.expectEqual(@as(usize, 10), preview_replay.visible_spans_after_preview.total_visible);
    try std.testing.expect(!preview_replay.visible_spans_after_preview.wrapped);
    try std.testing.expectEqual(@as(usize, 2), preview_replay.checked_focus.len);
    try std.testing.expectEqual(sample.SampleFocus.non_destructive_snapshot, preview_replay.checked_focus[0]);
    try std.testing.expectEqual(sample.SampleFocus.preview_truncation, preview_replay.checked_focus[1]);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 10), module.available());
    try std.testing.expect(!module.usesWrappedStorageWindow());

    _ = try module.runAnchorReplay();
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());
    const replay_lifecycle = module.lifecycleSummary();
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), replay_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay_lifecycle.queue_len);
    try std.testing.expectEqual(sample.StorageBacking.embedded_fixed_buffer, replay_lifecycle.storage_backing);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.available());
    try std.testing.expect(!module.usesWrappedStorageWindow());

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    const exited_lifecycle = module.lifecycleSummary();
    try std.testing.expectEqual(sample.SampleStage.exited, exited_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 1), exited_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), exited_lifecycle.queue_len);
    try std.testing.expectEqual(sample.StorageBacking.embedded_fixed_buffer, exited_lifecycle.storage_backing);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.available());
    try std.testing.expect(!module.usesWrappedStorageWindow());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runPreviewBoundaryReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}

test "phase 5 bytestream fifo sample keeps wrapped preview truncation explicit" {
    var module = sample.BytestreamFifoSample{};
    const wrapped_expected_after_preview = [_]u8{
        'o', 0, 1, 2, 3, 4, 5, 6,
        7,   8, 9, 10, 11, 12, 13, 14,
        15,  16, 17, 18, 19, 20, 21, 22,
        23,  24, 25, 26, 200, 201, 202, 203,
    };

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runWrappedPreviewReplay());
    try module.init();

    const wrapped_preview = try module.runWrappedPreviewReplay();
    try std.testing.expectEqual(sample.SampleStage.initialized, wrapped_preview.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.initialized, wrapped_preview.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 4), wrapped_preview.drained_count);
    try std.testing.expectEqualSlices(u8, "hell", wrapped_preview.drained_prefix[0..]);
    try std.testing.expectEqual(@as(usize, 4), wrapped_preview.refill_count);
    try std.testing.expectEqualSlices(u8, &.{ 200, 201, 202, 203 }, wrapped_preview.refill_values[0..]);
    try std.testing.expectEqual(@as(usize, 12), wrapped_preview.snapshot_len);
    try std.testing.expectEqualSlices(u8, &.{ 'o', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 }, wrapped_preview.snapshot_prefix[0..]);
    try std.testing.expectEqual(@as(usize, 8), wrapped_preview.preview_len);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), wrapped_preview.preview_total_visible);
    try std.testing.expect(wrapped_preview.preview_truncated);
    try std.testing.expectEqualSlices(u8, &.{ 'o', 0, 1, 2, 3, 4, 5, 6 }, wrapped_preview.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), wrapped_preview.queue_len_after_preview);
    try std.testing.expectEqual(@as(usize, 0), wrapped_preview.available_after_preview);
    try std.testing.expect(wrapped_preview.wrapped_window_after_preview);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 4), wrapped_preview.visible_spans_after_preview.first_span_len);
    try std.testing.expectEqual(@as(usize, 4), wrapped_preview.visible_spans_after_preview.second_span_len);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), wrapped_preview.visible_spans_after_preview.total_visible);
    try std.testing.expect(wrapped_preview.visible_spans_after_preview.wrapped);
    try std.testing.expectEqual(@as(usize, 4), wrapped_preview.checked_focus.len);
    try std.testing.expectEqual(sample.SampleFocus.wraparound_requeue, wrapped_preview.checked_focus[0]);
    try std.testing.expectEqual(sample.SampleFocus.non_destructive_snapshot, wrapped_preview.checked_focus[1]);
    try std.testing.expectEqual(sample.SampleFocus.preview_truncation, wrapped_preview.checked_focus[2]);
    try std.testing.expectEqual(sample.SampleFocus.queue_shape_boundaries, wrapped_preview.checked_focus[3]);
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.count());
    try std.testing.expectEqual(@as(usize, 0), module.available());
    try std.testing.expect(module.usesWrappedStorageWindow());
    const wrapped_spans = module.visibleSpanSummary();
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 4), wrapped_spans.first_span_len);
    try std.testing.expectEqual(@as(usize, 4), wrapped_spans.second_span_len);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), wrapped_spans.total_visible);
    try std.testing.expect(wrapped_spans.wrapped);

    var drained_after_preview: [sample.BytestreamFifoSample.capacity]u8 = undefined;
    const drained_after_preview_count = module.drain(drained_after_preview[0..]);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), drained_after_preview_count);
    try std.testing.expectEqualSlices(u8, wrapped_expected_after_preview[0..], drained_after_preview[0..]);
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.available());
    try std.testing.expect(!module.usesWrappedStorageWindow());
}
