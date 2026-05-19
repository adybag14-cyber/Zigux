const std = @import("std");
const virtio_ring = @import("virtio_ring");

pub const QueueShapeSummary = virtio_ring.QueueShapeSummary;
pub const QueueNotificationSummary = virtio_ring.QueueNotificationSummary;
pub const NotificationDataSummary = virtio_ring.NotificationDataSummary;
pub const UsedBufferPollSummary = virtio_ring.UsedBufferPollSummary;
pub const CallbackEnableSummary = virtio_ring.CallbackEnableSummary;
pub const DelayedCallbackSummary = virtio_ring.DelayedCallbackSummary;
pub const BrokenQueueSummary = virtio_ring.BrokenQueueSummary;
pub const QueueResetReadinessSummary = virtio_ring.QueueResetReadinessSummary;
pub const QueueResetSummary = virtio_ring.QueueResetSummary;

pub fn summarizeQueueShape(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !QueueShapeSummary {
    return ring.queueShapeSummary(queue_index);
}

pub fn summarizePrepareKick(
    ring: *virtio_ring.VirtioRingLab,
    queue_index: u16,
) !QueueNotificationSummary {
    return ring.prepareKick(queue_index);
}

pub fn summarizeNotificationData(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !NotificationDataSummary {
    return ring.notificationDataSummary(queue_index);
}

pub fn summarizeUsedBufferPoll(
    ring: *virtio_ring.VirtioRingLab,
    queue_index: u16,
) !UsedBufferPollSummary {
    return ring.pollUsedBuffers(queue_index);
}

pub fn summarizeEnableCallback(
    ring: *virtio_ring.VirtioRingLab,
    queue_index: u16,
) !CallbackEnableSummary {
    return ring.enableCallback(queue_index);
}

pub fn summarizeDelayedCallback(
    ring: *virtio_ring.VirtioRingLab,
    queue_index: u16,
) !DelayedCallbackSummary {
    return ring.enableCallbackDelayed(queue_index);
}

pub fn summarizeBrokenQueue(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !BrokenQueueSummary {
    return ring.brokenQueueSummary(queue_index);
}

pub fn summarizeResetReadiness(
    ring: *const virtio_ring.VirtioRingLab,
    queue_index: u16,
) !QueueResetReadinessSummary {
    return ring.queueResetReadinessSummary(queue_index);
}

pub fn summarizeResetQueue(
    ring: *virtio_ring.VirtioRingLab,
    queue_index: u16,
) !QueueResetSummary {
    return ring.resetQueue(queue_index);
}

pub fn queueNeedsResetPoll(summary: QueueResetReadinessSummary) bool {
    return summary.pending_used_chain_count != 0;
}

pub fn queueHasBrokenCallbackFence(summary: BrokenQueueSummary) bool {
    return summary.broken and !summary.callback_enabled;
}

pub fn callbackEnableNeedsPoll(summary: CallbackEnableSummary) bool {
    return summary.should_poll;
}

pub fn delayedCallbackBudgetExhausted(summary: DelayedCallbackSummary) bool {
    return summary.pending_used_chain_count > summary.delay_budget_count;
}

pub fn notificationDataUsesWrapBit(summary: NotificationDataSummary) bool {
    return (summary.encoded_next & virtio_ring.packed_notification_wrap_bit) != 0;
}

test "phase10 virtio ring verify keeps queue-shape wrapper explicit across split and packed queues" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(0, 8, .split, true, false);
    try ring.defineQueue(1, 16, .packed_ring, false, true);

    var summary = try summarizeQueueShape(&ring, 0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 8), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, summary.layout);
    try std.testing.expect(summary.uses_event_idx);
    try std.testing.expect(!summary.uses_indirect_descriptors);

    summary = try summarizeQueueShape(&ring, 1);
    try std.testing.expectEqual(@as(u16, 1), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 16), summary.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, summary.layout);
    try std.testing.expect(!summary.uses_event_idx);
    try std.testing.expect(summary.uses_indirect_descriptors);

    try std.testing.expectError(error.QueueNotDefined, summarizeQueueShape(&ring, 2));
}

test "phase10 virtio ring verify keeps prepare-kick wrapper idempotent and queue-local" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(7, 8, .split, true, false);

    try ring.publishDescriptorChain(7);
    try ring.publishDescriptorChain(7);

    var summary = try summarizePrepareKick(&ring, 7);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 7), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 2), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 2), summary.num_added);
    try std.testing.expectEqual(@as(usize, 1), summary.notification_count);
    try std.testing.expect(summary.needs_kick);

    summary = try summarizePrepareKick(&ring, 7);
    try std.testing.expectEqual(@as(u16, 2), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.num_added);
    try std.testing.expectEqual(@as(usize, 1), summary.notification_count);
    try std.testing.expect(!summary.needs_kick);

    try ring.publishDescriptorChain(7);
    summary = try summarizePrepareKick(&ring, 7);
    try std.testing.expectEqual(@as(u16, 3), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 3), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.num_added);
    try std.testing.expectEqual(@as(usize, 2), summary.notification_count);
    try std.testing.expect(summary.needs_kick);
}

test "phase10 virtio ring verify keeps notification-data next-avail state reviewable across split packed and reset replay" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(0, 8, .split, true, false);
    try ring.publishDescriptorChain(0);
    try ring.publishDescriptorChain(0);
    try ring.publishDescriptorChain(0);

    var summary = try summarizeNotificationData(&ring, 0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(virtio_ring.QueueLayout.split, summary.layout);
    try std.testing.expectEqual(@as(u16, 3), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 3), summary.next_avail_idx);
    try std.testing.expect(!summary.next_avail_wrap_counter);
    try std.testing.expect(!notificationDataUsesWrapBit(summary));
    try std.testing.expectEqual(@as(u32, 0x0003_0000), summary.notification_data);

    try ring.defineQueue(1, 8, .packed_ring, true, false);
    inline for (0..8) |_| {
        try ring.publishDescriptorChain(1);
    }
    _ = try ring.prepareKick(1);
    try ring.recordUsedChains(1, 8);
    _ = try ring.pollUsedBuffers(1);
    try ring.publishDescriptorChain(1);

    summary = try summarizeNotificationData(&ring, 1);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, summary.layout);
    try std.testing.expectEqual(@as(u16, 9), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), summary.next_avail_idx);
    try std.testing.expect(summary.next_avail_wrap_counter);
    try std.testing.expect(notificationDataUsesWrapBit(summary));
    try std.testing.expectEqual(
        @as(u16, virtio_ring.packed_notification_wrap_bit | 1),
        summary.encoded_next,
    );
    try std.testing.expectEqual(@as(u32, 0x8001_0001), summary.notification_data);

    _ = try ring.prepareKick(1);
    try ring.recordUsedChains(1, 1);
    _ = try ring.pollUsedBuffers(1);
    _ = try ring.resetQueue(1);

    summary = try summarizeNotificationData(&ring, 1);
    try std.testing.expectEqual(@as(u16, 0), summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), summary.next_avail_idx);
    try std.testing.expect(!summary.next_avail_wrap_counter);
    try std.testing.expect(!notificationDataUsesWrapBit(summary));
    try std.testing.expectEqual(@as(u16, 0), summary.encoded_next);
    try std.testing.expectEqual(@as(u32, 1), summary.notification_data);
}

test "phase10 virtio ring verify keeps used-buffer polling progress explicit after queue-local replay" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(3, 8, .split, true, false);

    try ring.publishDescriptorChain(3);
    try ring.publishDescriptorChain(3);
    _ = try ring.prepareKick(3);
    try ring.recordUsedChains(3, 1);

    var summary = try summarizeUsedBufferPoll(&ring, 3);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 3), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 1), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
    try std.testing.expect(summary.has_newly_used_chains);

    summary = try summarizeUsedBufferPoll(&ring, 3);
    try std.testing.expectEqual(@as(u16, 1), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 1), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
    try std.testing.expect(!summary.has_newly_used_chains);

    try ring.recordUsedChains(3, 1);
    summary = try summarizeUsedBufferPoll(&ring, 3);
    try std.testing.expectEqual(@as(u16, 2), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 1), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expect(summary.has_newly_used_chains);
}

test "phase10 virtio ring verify keeps callback-enable wrapper explicit about pending used work" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(4, 8, .split, true, false);

    try ring.publishDescriptorChain(4);
    try ring.publishDescriptorChain(4);
    _ = try ring.prepareKick(4);
    try ring.recordUsedChains(4, 2);
    try ring.disableCallback(4);

    var summary = try summarizeEnableCallback(&ring, 4);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 4), summary.queue_index);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.pending_used_chain_count);
    try std.testing.expect(summary.should_poll);
    try std.testing.expect(callbackEnableNeedsPoll(summary));

    const poll = try ring.pollUsedBuffers(4);
    try std.testing.expectEqual(@as(u16, 2), poll.newly_used_chain_count);

    summary = try summarizeEnableCallback(&ring, 4);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 2), summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!summary.should_poll);
    try std.testing.expect(!callbackEnableNeedsPoll(summary));
}

test "phase10 virtio ring verify rejects callback-enable replay on broken queues" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(6, 8, .packed_ring, true, true);
    _ = try ring.markBroken(6);
    try std.testing.expectError(error.QueueBroken, summarizeEnableCallback(&ring, 6));
}

test "phase10 virtio ring verify keeps delayed callback wrapper thresholds explicit" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(4, 8, .split, true, false);

    try ring.publishDescriptorChain(4);
    try ring.publishDescriptorChain(4);
    try ring.publishDescriptorChain(4);
    try ring.publishDescriptorChain(4);
    _ = try ring.prepareKick(4);

    try ring.recordUsedChains(4, 2);
    var summary = try summarizeDelayedCallback(&ring, 4);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 2), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);
    try std.testing.expectEqual(@as(u16, 2), summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 3), summary.delayed_event_target_idx);
    try std.testing.expect(summary.should_poll);
    try std.testing.expect(delayedCallbackBudgetExhausted(summary));

    const poll = try ring.pollUsedBuffers(4);
    try std.testing.expectEqual(@as(u16, 2), poll.newly_used_chain_count);

    summary = try summarizeDelayedCallback(&ring, 4);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expect(!summary.should_poll);
    try std.testing.expect(!delayedCallbackBudgetExhausted(summary));
}

test "phase10 virtio ring verify keeps broken queue fences visible until clear" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(5, 8, .packed_ring, false, true);

    try ring.publishDescriptorChain(5);
    try ring.publishDescriptorChain(5);
    _ = try ring.prepareKick(5);
    try ring.recordUsedChains(5, 1);

    _ = try ring.markBroken(5);
    var broken = try summarizeBrokenQueue(&ring, 5);
    try std.testing.expect(queueHasBrokenCallbackFence(broken));
    try std.testing.expectEqual(@as(u16, 1), broken.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), broken.pending_used_chain_count);
    try std.testing.expectError(error.QueueBroken, ring.pollUsedBuffers(5));

    _ = try ring.clearBroken(5);
    broken = try summarizeBrokenQueue(&ring, 5);
    try std.testing.expect(!broken.broken);
    try std.testing.expect(!queueHasBrokenCallbackFence(broken));
    try std.testing.expectEqual(@as(u16, 1), broken.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), broken.pending_used_chain_count);

    const poll = try ring.pollUsedBuffers(5);
    try std.testing.expectEqual(@as(u16, 1), poll.newly_used_chain_count);
}

test "phase10 virtio ring verify exposes reset-readiness blocker ordering after clearBroken releases queue debt" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .split, true, false);

    try ring.publishDescriptorChain(2);
    try ring.publishDescriptorChain(2);

    var readiness = try summarizeResetReadiness(&ring, 2);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 2), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), readiness.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.pending_used_chain_count);
    try std.testing.expect(!readiness.reset_ready);

    _ = try ring.markBroken(2);
    readiness = try summarizeResetReadiness(&ring, 2);
    try std.testing.expectEqualStrings("queue_broken", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 2), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), readiness.outstanding_chain_count);

    const cleared = try ring.clearBroken(2);
    try std.testing.expect(!cleared.broken);
    try std.testing.expectEqual(@as(u16, 2), cleared.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), cleared.outstanding_chain_count);

    readiness = try summarizeResetReadiness(&ring, 2);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 2), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), readiness.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.pending_used_chain_count);

    const kick = try ring.prepareKick(2);
    try std.testing.expect(kick.needs_kick);
    try std.testing.expectEqual(@as(u16, 2), kick.num_added);

    readiness = try summarizeResetReadiness(&ring, 2);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 0), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 2), readiness.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.pending_used_chain_count);

    try ring.recordUsedChains(2, 2);
    readiness = try summarizeResetReadiness(&ring, 2);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(readiness.blocker.?));
    try std.testing.expectEqual(@as(u16, 0), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 2), readiness.pending_used_chain_count);
    try std.testing.expect(queueNeedsResetPoll(readiness));

    const poll = try ring.pollUsedBuffers(2);
    try std.testing.expectEqual(@as(u16, 2), poll.newly_used_chain_count);

    readiness = try summarizeResetReadiness(&ring, 2);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expect(readiness.blocker == null);
    try std.testing.expectEqual(@as(u16, 0), readiness.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), readiness.pending_used_chain_count);
    try std.testing.expect(!queueNeedsResetPoll(readiness));
}

test "phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(6, 8, .packed_ring, true, true);

    var readiness = try summarizeResetReadiness(&ring, 6);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expect(readiness.blocker == null);
    try std.testing.expect(!queueNeedsResetPoll(readiness));

    try ring.publishDescriptorChain(6);
    readiness = try summarizeResetReadiness(&ring, 6);
    try std.testing.expectEqualStrings("unpublished_chains", @tagName(readiness.blocker.?));

    _ = try ring.prepareKick(6);
    readiness = try summarizeResetReadiness(&ring, 6);
    try std.testing.expectEqualStrings("outstanding_chains", @tagName(readiness.blocker.?));

    try ring.recordUsedChains(6, 1);
    readiness = try summarizeResetReadiness(&ring, 6);
    try std.testing.expectEqualStrings("unpolled_used_chains", @tagName(readiness.blocker.?));
    try std.testing.expect(queueNeedsResetPoll(readiness));

    _ = try ring.pollUsedBuffers(6);
    readiness = try summarizeResetReadiness(&ring, 6);
    try std.testing.expect(readiness.reset_ready);
    try std.testing.expect(readiness.blocker == null);
    try std.testing.expect(!queueNeedsResetPoll(readiness));
}

test "phase10 virtio ring verify keeps reset wrapper explicit after queue-local readiness clears" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(1, 8, .packed_ring, true, true);

    try ring.publishDescriptorChain(1);
    _ = try ring.prepareKick(1);
    try ring.recordUsedChains(1, 1);
    _ = try ring.pollUsedBuffers(1);

    const reset = try summarizeResetQueue(&ring, 1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", reset.anchor);
    try std.testing.expectEqual(@as(u16, 1), reset.queue_index);
    try std.testing.expectEqual(@as(u16, 8), reset.descriptor_count);
    try std.testing.expectEqual(virtio_ring.QueueLayout.packed_ring, reset.layout);
    try std.testing.expect(reset.uses_event_idx);
    try std.testing.expect(reset.uses_indirect_descriptors);
    try std.testing.expect(reset.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), reset.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), reset.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 0), reset.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset.unpublished_chain_count);
    try std.testing.expectEqual(@as(u16, 0), reset.pending_used_chain_count);
    try std.testing.expectEqual(@as(usize, 0), reset.notification_count);
}
