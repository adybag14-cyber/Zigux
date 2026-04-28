const std = @import("std");
const sample = @import("bytestream_fifo_sample");

test "phase 5 bytestream fifo sample stays in the reference-sample lane" {
    const descriptor = sample.BytestreamFifoSample.descriptor();

    try std.testing.expectEqualStrings("bytestream_fifo", descriptor.name);
    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
    try std.testing.expectEqual(sample.StorageBacking.embedded_fixed_buffer, descriptor.storage_backing);
}

test "phase 5 bytestream fifo sample replays exact queue behavior from the Linux anchor" {
    var module = sample.BytestreamFifoSample{};
    try module.init();
    const replay = try module.runAnchorReplay();
    const expected_focus = [_]sample.SampleFocus{
        .bounded_fifo_order,
        .wraparound_requeue,
        .peek_and_skip,
        .non_destructive_snapshot,
        .reset_and_replay,
        .ownership_and_lifetime,
    };

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
    try std.testing.expectEqualSlices(u8, sample.expected_anchor_result[0..8], replay.preview_prefix[0..]);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), replay.snapshot_len);
    try std.testing.expectEqual(@as(u8, 20), replay.fill_start);
    try std.testing.expectEqual(@as(u8, 42), replay.fill_end);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), replay.final_len);
    try std.testing.expectEqual(sample.StorageBacking.embedded_fixed_buffer, replay.storage_backing);
    try std.testing.expectEqual(expected_focus.len, replay.checked_focus.len);
    for (expected_focus, replay.checked_focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
    try std.testing.expectEqualSlices(u8, sample.expected_anchor_result[0..], replay.snapshot_before_final_drain[0..]);
    try std.testing.expectEqualSlices(u8, sample.expected_anchor_result[0..], replay.final_sequence[0..]);
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());
}

test "phase 5 bytestream fifo sample keeps bounded helper behavior explicit" {
    var module = sample.BytestreamFifoSample{};

    try std.testing.expectEqual(@as(?u8, null), module.peekByte());
    try std.testing.expectEqual(@as(?u8, null), module.skipByte());
    try std.testing.expectEqual(@as(usize, 0), module.enqueueSlice(&.{}));

    var preview: [4]u8 = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(usize, 0), module.snapshotInto(preview[0..]));
    try std.testing.expectEqual(@as(u8, 0xaa), preview[0]);

    var count: u8 = 0;
    while (count < sample.BytestreamFifoSample.capacity) : (count += 1) {
        try std.testing.expect(module.pushByte(count));
    }
    try std.testing.expect(!module.pushByte(255));
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.count());
    try std.testing.expectEqual(@as(?u8, 0), module.peekByte());

    var snapshot: [8]u8 = undefined;
    try std.testing.expectEqual(@as(usize, snapshot.len), module.snapshotInto(snapshot[0..]));
    try std.testing.expectEqualSlices(u8, &.{ 0, 1, 2, 3, 4, 5, 6, 7 }, snapshot[0..]);
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity), module.count());

    try std.testing.expectEqual(@as(?u8, 0), module.skipByte());
    try std.testing.expectEqual(@as(usize, sample.BytestreamFifoSample.capacity - 1), module.count());

    module.reset();
    try std.testing.expectEqual(@as(usize, 5), module.enqueueSlice("hello"));
    var value: u8 = 0;
    while (value < 10) : (value += 1) {
        try std.testing.expect(module.pushByte(value));
    }
    var discard: [7]u8 = undefined;
    try std.testing.expectEqual(@as(usize, discard.len), module.dequeueSlice(discard[0..]));
    try std.testing.expectEqual(@as(usize, 2), module.enqueueSlice(&.{ 0, 1 }));

    var wraparound_preview: [8]u8 = [_]u8{0} ** 8;
    try std.testing.expectEqual(@as(usize, wraparound_preview.len), module.snapshotInto(wraparound_preview[0..]));
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5, 6, 7, 8, 9 }, wraparound_preview[0..]);
    try std.testing.expectEqual(@as(usize, 10), module.count());

    module.reset();
    try std.testing.expectEqual(@as(usize, 0), module.count());
    try std.testing.expectEqual(@as(?u8, null), module.popByte());
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
