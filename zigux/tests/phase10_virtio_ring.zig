const std = @import("std");
const virtio_ring = @import("virtio_ring");

test "phase10 virtio ring queue registration replay keeps active queue count and definition discipline explicit" {
    var ring = virtio_ring.VirtioRingLab{};
    try std.testing.expectEqual(@as(usize, 0), ring.registeredQueueCount());

    try std.testing.expectError(error.QueueNotDefined, ring.queueRegistrationSummary(0));
    try std.testing.expectError(error.EmptyDescriptorCount, ring.defineQueue(0, 0, .split, true, false));
    try std.testing.expectEqual(@as(usize, 0), ring.registeredQueueCount());
    try std.testing.expectError(
        error.DescriptorCountMustBePowerOfTwo,
        ring.defineQueue(0, 6, .split, true, false),
    );
    try std.testing.expectEqual(@as(usize, 0), ring.registeredQueueCount());
    try std.testing.expectError(
        error.QueueIndexOutOfRange,
        ring.defineQueue(virtio_ring.queue_capacity, 8, .split, true, false),
    );
    try std.testing.expectEqual(@as(usize, 0), ring.registeredQueueCount());

    try ring.defineQueue(0, 8, .split, true, false);
    var summary = try ring.queueRegistrationSummary(0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 8), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, summary.layout);
    try std.testing.expect(summary.uses_event_idx);
    try std.testing.expect(!summary.uses_indirect_descriptors);
    try std.testing.expectEqual(@as(usize, 1), summary.registered_queue_count);
    try std.testing.expectEqual(@as(usize, 1), ring.registeredQueueCount());

    try ring.defineQueue(2, 16, .packed_ring, false, true);
    summary = try ring.queueRegistrationSummary(2);
    try std.testing.expectEqual(@as(u16, 2), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 16), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, summary.layout);
    try std.testing.expect(!summary.uses_event_idx);
    try std.testing.expect(summary.uses_indirect_descriptors);
    try std.testing.expectEqual(@as(usize, 2), summary.registered_queue_count);
    try std.testing.expectEqual(@as(usize, 2), ring.registeredQueueCount());

    try std.testing.expectError(error.QueueAlreadyDefined, ring.defineQueue(2, 16, .packed_ring, false, true));
    try std.testing.expectEqual(@as(usize, 2), ring.registeredQueueCount());
    try std.testing.expectError(error.QueueNotDefined, ring.queueRegistrationSummary(1));
}

test "phase10 virtio ring broader replay keeps queue-local publish notification and reset flow aligned" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(1, 8, .packed_ring, true, true);

    const shape = try ring.queueShapeSummary(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", shape.anchor);
    try std.testing.expectEqual(@as(u16, 1), shape.queue_index);
    try std.testing.expectEqual(@as(u16, 8), shape.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, shape.layout);
    try std.testing.expect(shape.uses_event_idx);
    try std.testing.expect(shape.uses_indirect_descriptors);

    var publish = try ring.queuePublishReadinessSummary(1);
    try std.testing.expect(publish.publish_ready);
    try std.testing.expect(publish.blocker == null);
    try std.testing.expectEqual(@as(u16, 8), publish.available_descriptor_count);

    try ring.publishDescriptorChain(1);
    try ring.publishDescriptorChain(1);

    var notification_state = try ring.notificationSummary(1);
    try std.testing.expectEqual(@as(u16, 2), notification_state.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 2), notification_state.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 2), notification_state.num_added);
    try std.testing.expect(notification_state.needs_kick);

    const notification_data = try ring.notificationDataSummary(1);
    try std.testing.expectEqual(@as(u16, 2), notification_data.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 2), notification_data.next_avail_idx);
    try std.testing.expect(!notification_data.next_avail_wrap_counter);
    try std.testing.expectEqual(@as(u16, 2), notification_data.encoded_next);
    try std.testing.expectEqual(@as(u32, 0x0002_0001), notification_data.notification_data);

    const kick = try ring.prepareKick(1);
    try std.testing.expect(kick.needs_kick);
    try std.testing.expectEqual(@as(u16, 2), kick.num_added);
    try std.testing.expectEqual(@as(usize, 1), kick.notification_count);

    notification_state = try ring.notificationSummary(1);
    try std.testing.expectEqual(@as(u16, 0), notification_state.num_added);
    try std.testing.expectEqual(@as(usize, 1), notification_state.notification_count);
    try std.testing.expect(!notification_state.needs_kick);

    try ring.recordUsedChains(1, 2);

    publish = try ring.queuePublishReadinessSummary(1);
    try std.testing.expect(publish.publish_ready);
    try std.testing.expect(publish.blocker == null);
    try std.testing.expectEqual(@as(u16, 8), publish.available_descriptor_count);
    try std.testing.expectEqual(@as(u16, 0), publish.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), publish.outstanding_chain_count);

    var reset_readiness = try ring.queueResetReadinessSummary(1);
    try std.testing.expect(!reset_readiness.reset_ready);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(reset_readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 2), reset_readiness.pending_used_chain_count);

    const poll = try ring.pollUsedBuffers(1);
    try std.testing.expect(poll.has_newly_used_chains);
    try std.testing.expectEqual(@as(u16, 2), poll.newly_used_chain_count);

    reset_readiness = try ring.queueResetReadinessSummary(1);
    try std.testing.expect(reset_readiness.reset_ready);
    try std.testing.expect(reset_readiness.blocker == null);

    const reset = try ring.resetQueue(1);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, reset.layout);
    try std.testing.expect(reset.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), reset.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), reset.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset.pending_used_chain_count);
    try std.testing.expectEqual(@as(usize, 0), reset.notification_count);
}

test "phase10 virtio ring broader replay keeps broken queue debt explicit until clearBroken and queue-local drain" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 8, .split, true, false);

    try ring.publishDescriptorChain(3);

    const broken = try ring.markBroken(3);
    try std.testing.expect(broken.broken);
    try std.testing.expect(!broken.callback_enabled);
    try std.testing.expectEqual(@as(u16, 1), broken.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), broken.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), broken.pending_used_chain_count);

    const broken_summary = try ring.brokenQueueSummary(3);
    try std.testing.expect(broken_summary.broken);
    try std.testing.expectEqual(@as(u16, 1), broken_summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), broken_summary.outstanding_chain_count);

    const cleared = try ring.clearBroken(3);
    try std.testing.expect(!cleared.broken);
    try std.testing.expectEqual(@as(u16, 1), cleared.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), cleared.outstanding_chain_count);

    var reset_readiness = try ring.queueResetReadinessSummary(3);
    try std.testing.expect(!reset_readiness.reset_ready);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(reset_readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), reset_readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), reset_readiness.outstanding_chain_count);

    const kick = try ring.prepareKick(3);
    try std.testing.expect(kick.needs_kick);
    try std.testing.expectEqual(@as(u16, 1), kick.num_added);

    reset_readiness = try ring.queueResetReadinessSummary(3);
    try std.testing.expect(!reset_readiness.reset_ready);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(reset_readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 0), reset_readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 1), reset_readiness.outstanding_chain_count);

    try ring.recordUsedChains(3, 1);

    reset_readiness = try ring.queueResetReadinessSummary(3);
    try std.testing.expect(!reset_readiness.reset_ready);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(reset_readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 1), reset_readiness.pending_used_chain_count);

    const poll = try ring.pollUsedBuffers(3);
    try std.testing.expect(poll.has_newly_used_chains);
    try std.testing.expectEqual(@as(u16, 1), poll.newly_used_chain_count);

    reset_readiness = try ring.queueResetReadinessSummary(3);
    try std.testing.expect(reset_readiness.reset_ready);
    try std.testing.expect(reset_readiness.blocker == null);
}

test "phase10 virtio ring callback summaries keep rollover math explicit across used-index wraparound" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(0, virtio_ring.max_descriptor_count, .split, true, false);

    var rounds: usize = 0;
    while (rounds < 63) : (rounds += 1) {
        var descriptors: u16 = 0;
        while (descriptors < virtio_ring.max_descriptor_count) : (descriptors += 1) {
            try ring.publishDescriptorChain(0);
        }
        _ = try ring.prepareKick(0);
        try ring.recordUsedChains(0, virtio_ring.max_descriptor_count);
        _ = try ring.pollUsedBuffers(0);
    }

    var descriptors: u16 = 0;
    while (descriptors < virtio_ring.max_descriptor_count - 1) : (descriptors += 1) {
        try ring.publishDescriptorChain(0);
    }
    _ = try ring.prepareKick(0);
    try ring.recordUsedChains(0, virtio_ring.max_descriptor_count - 1);
    _ = try ring.pollUsedBuffers(0);

    try ring.publishDescriptorChain(0);
    _ = try ring.prepareKick(0);
    try ring.recordUsedChains(0, 1);
    try ring.disableCallback(0);

    var callback = try ring.enableCallback(0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", callback.anchor);
    try std.testing.expectEqual(@as(u16, 0), callback.queue_index);
    try std.testing.expect(callback.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), callback.last_used_idx);
    try std.testing.expectEqual(@as(u16, std.math.maxInt(u16)), callback.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), callback.pending_used_chain_count);
    try std.testing.expect(callback.should_poll);

    var delayed = try ring.enableCallbackDelayed(0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", delayed.anchor);
    try std.testing.expectEqual(@as(u16, 0), delayed.queue_index);
    try std.testing.expect(delayed.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), delayed.last_used_idx);
    try std.testing.expectEqual(@as(u16, std.math.maxInt(u16)), delayed.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), delayed.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), delayed.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 0), delayed.delayed_event_target_idx);
    try std.testing.expectEqual(@as(u16, 1), delayed.pending_used_chain_count);
    try std.testing.expect(delayed.should_poll);
    try std.testing.expect(!delayed.settled);

    const poll = try ring.pollUsedBuffers(0);
    try std.testing.expectEqual(@as(u16, 0), poll.last_used_idx);
    try std.testing.expectEqual(@as(u16, std.math.maxInt(u16)), poll.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), poll.newly_used_chain_count);
    try std.testing.expect(poll.has_newly_used_chains);

    callback = try ring.enableCallback(0);
    try std.testing.expect(callback.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), callback.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), callback.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), callback.pending_used_chain_count);
    try std.testing.expect(!callback.should_poll);

    delayed = try ring.enableCallbackDelayed(0);
    try std.testing.expect(delayed.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), delayed.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), delayed.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), delayed.pending_used_chain_count);
    try std.testing.expect(!delayed.should_poll);
    try std.testing.expect(delayed.settled);
}
