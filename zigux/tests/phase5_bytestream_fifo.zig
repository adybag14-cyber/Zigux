const std = @import("std");
const sample = @import("bytestream_fifo_sample");

test "phase 5 bytestream fifo sample stays in the reference-sample lane" {
    const descriptor = sample.BytestreamFifoSample.descriptor();
    const contract = sample.BytestreamFifoSample.reviewContract();
    const expected_focus = [_]sample.SampleFocus{
        .bounded_fifo_order,
        .wraparound_requeue,
        .peek_and_skip,
        .non_destructive_snapshot,
        .preview_truncation,
        .remaining_capacity,
        .queue_shape_boundaries,
        .helper_boundaries,
        .reset_and_replay,
        .ownership_and_lifetime,
    };
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
    try std.testing.expectEqual(@as(usize, expected_focus.len), contract.focus.len);
    for (expected_focus, contract.focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
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
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), replay.preview_total_visible);
    try std.testing.expect(replay.preview_truncated);
    try std.testing.expectEqualSlices(u8, sample.expected_anchor_result[0..8], replay.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), replay.snapshot_len);
    try std.testing.expectEqualSlices(u8, sample.expected_anchor_result[0..], replay.snapshot_before_final_drain[0..]);
    try std.testing.expectEqual(@as(u8, 20), replay.fill_start);
    try std.testing.expectEqual(@as(u8, 42), replay.fill_end);
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
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().second_window_len);
    try std.testing.expect(!module.usesWrappedStorageWindow());

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.available());
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().second_window_len);
    try std.testing.expect(!module.usesWrappedStorageWindow());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());
}

test "phase 5 bytestream fifo sample keeps helper, occupancy, and queue-shape behavior explicit" {
    var module = sample.BytestreamFifoSample{};

    try std.testing.expectEqual(@as(?u8, null), module.peekByte());
    try std.testing.expectEqual(@as(?u8, null), module.skipByte());
    try std.testing.expectEqual(@as(usize, 0), module.enqueueSlice(&.{}));

    var preview_buf: [4]u8 = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const empty_preview = module.previewInto(preview_buf[0..]);
    try std.testing.expectEqual(@as(usize, 0), empty_preview.copied);
    try std.testing.expectEqual(@as(usize, 0), empty_preview.total_visible);
    try std.testing.expect(!empty_preview.truncated);
    try std.testing.expectEqualSlices(u8, &.{ 0xaa, 0xaa, 0xaa, 0xaa }, preview_buf[0..]);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.available());
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().second_window_len);
    try std.testing.expect(!module.usesWrappedStorageWindow());
    const empty_occupancy = module.occupancySummary();
    try std.testing.expectEqual(@as(usize, 0), empty_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 0), empty_occupancy.used);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), empty_occupancy.available);
    try std.testing.expect(empty_occupancy.empty);
    try std.testing.expect(!empty_occupancy.full);
    try std.testing.expect(!empty_occupancy.wrapped);
    try std.testing.expect(!empty_occupancy.wrapped_window);

    try module.init();
    try std.testing.expect(module.pushByte(7));
    try std.testing.expectEqual(@as(usize, 1), module.count());
    module.reset();
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 0), module.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), module.count());

    try std.testing.expectEqual(@as(usize, 5), module.enqueueSlice("hello"));
    try std.testing.expectEqual(@as(usize, 27), module.available());
    try std.testing.expectEqual(@as(usize, 5), module.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().second_window_len);
    try std.testing.expect(!module.usesWrappedStorageWindow());

    var value: u8 = 0;
    while (value < 10) : (value += 1) {
        try std.testing.expect(module.pushByte(value));
    }
    var discard: [7]u8 = undefined;
    try std.testing.expectEqual(@as(usize, discard.len), module.dequeueSlice(discard[0..]));
    try std.testing.expectEqual(@as(usize, 2), module.enqueueSlice(&.{ 0, 1 }));

    var wraparound_preview: [8]u8 = [_]u8{0} ** 8;
    const wrap_preview = module.previewInto(wraparound_preview[0..]);
    try std.testing.expectEqual(@as(usize, wraparound_preview.len), wrap_preview.copied);
    try std.testing.expectEqual(@as(usize, 10), wrap_preview.total_visible);
    try std.testing.expect(wrap_preview.truncated);
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5, 6, 7, 8, 9 }, wraparound_preview[0..]);
    try std.testing.expectEqual(@as(usize, 10), module.count());
    try std.testing.expectEqual(@as(usize, 22), module.available());
    try std.testing.expectEqual(@as(usize, 10), module.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().second_window_len);
    try std.testing.expect(!module.usesWrappedStorageWindow());

    module.reset();
    var fill: u8 = 0;
    while (fill < sample.fifo_capacity) : (fill += 1) {
        try std.testing.expect(module.pushByte(fill));
    }
    try std.testing.expect(!module.pushByte(255));
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), module.count());
    try std.testing.expectEqual(@as(usize, 0), module.available());
    try std.testing.expectEqual(@as(?u8, 0), module.peekByte());
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), module.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().second_window_len);
    try std.testing.expect(!module.usesWrappedStorageWindow());
    const full_occupancy = module.occupancySummary();
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), full_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), full_occupancy.used);
    try std.testing.expectEqual(@as(usize, 0), full_occupancy.available);
    try std.testing.expect(!full_occupancy.empty);
    try std.testing.expect(full_occupancy.full);
    try std.testing.expect(!full_occupancy.wrapped);
    try std.testing.expect(!full_occupancy.wrapped_window);

    var full_preview: [sample.fifo_capacity]u8 = [_]u8{0} ** sample.fifo_capacity;
    const full_preview_result = module.previewInto(full_preview[0..]);
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), full_preview_result.copied);
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), full_preview_result.total_visible);
    try std.testing.expect(!full_preview_result.truncated);

    try std.testing.expectEqual(@as(?u8, 0), module.skipByte());
    try std.testing.expectEqual(@as(usize, 1), module.available());
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity - 1), module.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().second_window_len);
    try std.testing.expect(!module.usesWrappedStorageWindow());
    try std.testing.expect(module.pushByte(200));
    try std.testing.expectEqual(@as(usize, 0), module.available());
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity - 1), module.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 1), module.visibleSpanSummary().second_window_len);
    try std.testing.expect(module.usesWrappedStorageWindow());
    const wrapped_full_occupancy = module.occupancySummary();
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), wrapped_full_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), wrapped_full_occupancy.used);
    try std.testing.expectEqual(@as(usize, 0), wrapped_full_occupancy.available);
    try std.testing.expect(!wrapped_full_occupancy.empty);
    try std.testing.expect(wrapped_full_occupancy.full);
    try std.testing.expect(wrapped_full_occupancy.wrapped);
    try std.testing.expect(wrapped_full_occupancy.wrapped_window);

    module.reset();
    try std.testing.expectEqual(@as(usize, 5), module.enqueueSlice("hello"));
    var short_drain: [3]u8 = undefined;
    try std.testing.expectEqual(@as(usize, short_drain.len), module.drain(short_drain[0..]));
    try std.testing.expectEqualSlices(u8, "hel", short_drain[0..]);
    try std.testing.expectEqual(@as(usize, 2), module.count());
    try std.testing.expectEqual(@as(?u8, 'l'), module.peekByte());

    var remainder: [2]u8 = undefined;
    try std.testing.expectEqual(@as(usize, remainder.len), module.dequeueSlice(remainder[0..]));
    try std.testing.expectEqualSlices(u8, "lo", remainder[0..]);
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(@as(usize, 0), module.drain(short_drain[0..]));

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    const exited_occupancy = module.occupancySummary();
    try std.testing.expectEqual(@as(usize, 0), exited_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 0), exited_occupancy.used);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), exited_occupancy.available);
    try std.testing.expect(exited_occupancy.empty);
    try std.testing.expect(!exited_occupancy.full);
    try std.testing.expect(!exited_occupancy.wrapped);
    try std.testing.expect(!exited_occupancy.wrapped_window);
}

test "phase 5 bytestream fifo sample keeps preview and lifecycle boundaries explicit" {
    var module = sample.BytestreamFifoSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runPreviewBoundaryReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runWrappedPreviewReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());

    try module.init();
    const preview_replay = try module.runPreviewBoundaryReplay();
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5 }, preview_replay.snapshot_prefix[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5, 6, 7, 8, 9 }, preview_replay.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, 10), preview_replay.preview_total_visible);
    try std.testing.expectEqual(@as(usize, 10), preview_replay.queue_len_after_preview);
    try std.testing.expectEqual(@as(usize, 22), preview_replay.available_after_preview);
    try std.testing.expectEqual(@as(usize, 7), preview_replay.visible_span_after_preview.head_index);
    try std.testing.expectEqual(@as(usize, 17), preview_replay.visible_span_after_preview.tail_index);
    try std.testing.expectEqual(@as(usize, 10), preview_replay.visible_span_after_preview.total_visible);
    try std.testing.expectEqual(@as(usize, 10), preview_replay.visible_span_after_preview.first_window_len);
    try std.testing.expectEqual(@as(usize, 0), preview_replay.visible_span_after_preview.second_window_len);
    try std.testing.expect(!preview_replay.visible_span_after_preview.wraps);
    const preview_occupancy = module.occupancySummary();
    try std.testing.expectEqual(@as(usize, 10), preview_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 10), preview_occupancy.used);
    try std.testing.expectEqual(@as(usize, 22), preview_occupancy.available);
    try std.testing.expect(!preview_occupancy.empty);
    try std.testing.expect(!preview_occupancy.full);
    try std.testing.expect(!preview_occupancy.wrapped);
    try std.testing.expect(!preview_occupancy.wrapped_window);
    const preview_writable = module.writableSpanSummary();
    try std.testing.expectEqual(@as(usize, 17), preview_writable.tail_index);
    try std.testing.expectEqual(@as(usize, 22), preview_writable.writable_count);
    try std.testing.expectEqual(@as(usize, 15), preview_writable.first_window_len);
    try std.testing.expectEqual(@as(usize, 7), preview_writable.second_window_len);
    try std.testing.expect(preview_writable.wraps);
    try std.testing.expectEqual(@as(usize, 22), module.available());
    try std.testing.expectEqual(@as(usize, 10), module.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().second_window_len);
    try std.testing.expect(!module.usesWrappedStorageWindow());

    const wrapped_preview = try module.runWrappedPreviewReplay();
    try std.testing.expectEqualSlices(u8, "hell", wrapped_preview.drained_prefix[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 200, 201, 202, 203 }, wrapped_preview.refill_values[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 'o', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 }, wrapped_preview.snapshot_prefix[0..]);
    try std.testing.expectEqualSlices(u8, &.{ 'o', 0, 1, 2, 3, 4, 5, 6 }, wrapped_preview.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), wrapped_preview.preview_total_visible);
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), wrapped_preview.queue_len_after_preview);
    try std.testing.expectEqual(@as(usize, 0), wrapped_preview.available_after_preview);
    try std.testing.expectEqual(@as(usize, 4), wrapped_preview.visible_span_after_preview.head_index);
    try std.testing.expectEqual(@as(usize, 4), wrapped_preview.visible_span_after_preview.tail_index);
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), wrapped_preview.visible_span_after_preview.total_visible);
    try std.testing.expectEqual(@as(usize, 28), wrapped_preview.visible_span_after_preview.first_window_len);
    try std.testing.expectEqual(@as(usize, 4), wrapped_preview.visible_span_after_preview.second_window_len);
    try std.testing.expect(wrapped_preview.visible_span_after_preview.wraps);
    const wrapped_occupancy = module.occupancySummary();
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), wrapped_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), wrapped_occupancy.used);
    try std.testing.expectEqual(@as(usize, 0), wrapped_occupancy.available);
    try std.testing.expect(!wrapped_occupancy.empty);
    try std.testing.expect(wrapped_occupancy.full);
    try std.testing.expect(wrapped_occupancy.wrapped);
    try std.testing.expect(wrapped_occupancy.wrapped_window);
    const wrapped_writable = module.writableSpanSummary();
    try std.testing.expectEqual(@as(usize, 4), wrapped_writable.tail_index);
    try std.testing.expectEqual(@as(usize, 0), wrapped_writable.writable_count);
    try std.testing.expectEqual(@as(usize, 0), wrapped_writable.first_window_len);
    try std.testing.expectEqual(@as(usize, 0), wrapped_writable.second_window_len);
    try std.testing.expect(!wrapped_writable.wraps);
    try std.testing.expect(module.usesWrappedStorageWindow());

    const remaining_capacity = try module.runRemainingCapacityReplay();
    try std.testing.expectEqualSlices(u8, &.{ 'e', 'l', 'l', 'o', 0, 1, 2, 3 }, remaining_capacity.drained_prefix[0..]);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), remaining_capacity.available_after_init);
    try std.testing.expectEqual(@as(usize, 27), remaining_capacity.available_after_hello);
    try std.testing.expectEqual(@as(usize, 0), remaining_capacity.available_when_full);
    try std.testing.expectEqual(@as(usize, 1), remaining_capacity.available_after_skip);
    try std.testing.expectEqual(@as(usize, 0), remaining_capacity.available_after_wrap_refill);
    try std.testing.expectEqual(@as(usize, 8), remaining_capacity.available_after_partial_drain);
    try std.testing.expectEqual(@as(usize, 24), remaining_capacity.queue_len_after_partial_drain);
    try std.testing.expectEqual(@as(usize, 9), remaining_capacity.visible_span_after_partial_drain.head_index);
    try std.testing.expectEqual(@as(usize, 1), remaining_capacity.visible_span_after_partial_drain.tail_index);
    try std.testing.expectEqual(@as(usize, 24), remaining_capacity.visible_span_after_partial_drain.total_visible);
    try std.testing.expectEqual(@as(usize, 23), remaining_capacity.visible_span_after_partial_drain.first_window_len);
    try std.testing.expectEqual(@as(usize, 1), remaining_capacity.visible_span_after_partial_drain.second_window_len);
    try std.testing.expect(remaining_capacity.visible_span_after_partial_drain.wraps);
    try std.testing.expect(!remaining_capacity.wrapped_when_full);
    try std.testing.expect(remaining_capacity.wrapped_after_wrap_refill);
    const partial_drain_occupancy = module.occupancySummary();
    try std.testing.expectEqual(@as(usize, 24), partial_drain_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 24), partial_drain_occupancy.used);
    try std.testing.expectEqual(@as(usize, 8), partial_drain_occupancy.available);
    try std.testing.expect(!partial_drain_occupancy.empty);
    try std.testing.expect(!partial_drain_occupancy.full);
    try std.testing.expect(partial_drain_occupancy.wrapped);
    try std.testing.expect(partial_drain_occupancy.wrapped_window);
    const partial_drain_writable = module.writableSpanSummary();
    try std.testing.expectEqual(@as(usize, 1), partial_drain_writable.tail_index);
    try std.testing.expectEqual(@as(usize, 8), partial_drain_writable.writable_count);
    try std.testing.expectEqual(@as(usize, 8), partial_drain_writable.first_window_len);
    try std.testing.expectEqual(@as(usize, 0), partial_drain_writable.second_window_len);
    try std.testing.expect(!partial_drain_writable.wraps);
    try std.testing.expect(module.usesWrappedStorageWindow());

    _ = try module.runAnchorReplay();
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());
    const replay_lifecycle = module.lifecycleSummary();
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), replay_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay_lifecycle.queue_len);
    try std.testing.expectEqual(sample.StorageBacking.embedded_fixed_buffer, replay_lifecycle.storage_backing);
    const replay_complete_occupancy = module.occupancySummary();
    try std.testing.expectEqual(@as(usize, 0), replay_complete_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 0), replay_complete_occupancy.used);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), replay_complete_occupancy.available);
    try std.testing.expect(replay_complete_occupancy.empty);
    try std.testing.expect(!replay_complete_occupancy.full);
    try std.testing.expect(!replay_complete_occupancy.wrapped);
    try std.testing.expect(!replay_complete_occupancy.wrapped_window);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.available());
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().second_window_len);
    try std.testing.expect(!module.usesWrappedStorageWindow());

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.available());
    const exited_occupancy = module.occupancySummary();
    try std.testing.expectEqual(@as(usize, 0), exited_occupancy.queue_len);
    try std.testing.expectEqual(@as(usize, 0), exited_occupancy.used);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), exited_occupancy.available);
    try std.testing.expect(exited_occupancy.empty);
    try std.testing.expect(!exited_occupancy.full);
    try std.testing.expect(!exited_occupancy.wrapped);
    try std.testing.expect(!exited_occupancy.wrapped_window);
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().first_window_len);
    try std.testing.expectEqual(@as(usize, 0), module.visibleSpanSummary().second_window_len);
    try std.testing.expect(!module.usesWrappedStorageWindow());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runPreviewBoundaryReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runWrappedPreviewReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}
