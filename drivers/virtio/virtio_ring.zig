const std = @import("std");

pub const queue_capacity: usize = 8;
pub const max_descriptor_count: u16 = 1024;

pub const QueueLayout = enum {
    split,
    packed_ring,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_lab_validation: bool,
    touches_transport_mmio: bool,
    touches_dma_paths: bool,
};

pub const QueueShapeSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    descriptor_count: u16,
    layout: QueueLayout,
    uses_event_idx: bool,
    uses_indirect_descriptors: bool,
};

pub const QueueNotificationSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    avail_idx_shadow: u16,
    last_used_idx: u16,
    outstanding_chain_count: u16,
    num_added: u16,
    notification_count: usize,
    needs_kick: bool,
};

pub const UsedBufferPollSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    last_used_idx: u16,
    last_polled_used_idx: u16,
    newly_used_chain_count: u16,
    outstanding_chain_count: u16,
    has_newly_used_chains: bool,
};

pub const CallbackEnableSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    callback_enabled: bool,
    last_used_idx: u16,
    last_polled_used_idx: u16,
    pending_used_chain_count: u16,
    should_poll: bool,
};

pub const CallbackEnablePrepareSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    callback_enabled: bool,
    last_used_idx_snapshot: u16,
};

pub const CallbackPreparedPollSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    last_used_idx_snapshot: u16,
    current_last_used_idx: u16,
    has_used_buffers_since_prepare: bool,
};

pub const CallbackDisableSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    callback_enabled: bool,
    last_used_idx: u16,
    last_polled_used_idx: u16,
    pending_used_chain_count: u16,
    should_poll: bool,
};

pub const DelayedCallbackSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    callback_enabled: bool,
    last_used_idx: u16,
    last_polled_used_idx: u16,
    outstanding_chain_count: u16,
    delay_budget_count: u16,
    delayed_event_target_idx: u16,
    pending_used_chain_count: u16,
    should_poll: bool,
};

pub const QueueResetSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    descriptor_count: u16,
    layout: QueueLayout,
    callback_enabled: bool,
    avail_idx_shadow: u16,
    last_used_idx: u16,
    last_polled_used_idx: u16,
    outstanding_chain_count: u16,
    pending_used_chain_count: u16,
    notification_count: usize,
};

pub const QueueResetGuardSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    outstanding_chain_count: u16,
    pending_used_chain_count: u16,
    unpublished_chain_count: u16,
    reset_allowed: bool,
};

pub const QueueBrokenSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    broken: bool,
    outstanding_chain_count: u16,
    pending_used_chain_count: u16,
    unpublished_chain_count: u16,
};

pub const BrokenQueueRecoveryGuardSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    broken: bool,
    outstanding_chain_count: u16,
    pending_used_chain_count: u16,
    unpublished_chain_count: u16,
    recovery_allowed: bool,
};

pub const BrokenQueueRecoverySummary = struct {
    anchor: []const u8,
    queue_index: u16,
    descriptor_count: u16,
    layout: QueueLayout,
    broken_before_recovery: bool,
    callback_enabled_after_recovery: bool,
    avail_idx_shadow_after_recovery: u16,
    last_used_idx_after_recovery: u16,
    last_polled_used_idx_after_recovery: u16,
    outstanding_chain_count_after_recovery: u16,
    pending_used_chain_count_after_recovery: u16,
    notification_count_after_recovery: usize,
};

pub const QueueTeardownSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    broken: bool,
    callback_enabled: bool,
    outstanding_chain_count: u16,
    pending_used_chain_count: u16,
    unpublished_chain_count: u16,
    notification_count: usize,
    requires_poll_before_teardown: bool,
    ready_for_drained_teardown: bool,
};

pub const VirtioRingLab = struct {
    const Self = @This();
    const QueueSlot = struct {
        active: bool = false,
        descriptor_count: u16 = 0,
        layout: QueueLayout = .split,
        uses_event_idx: bool = false,
        uses_indirect_descriptors: bool = false,
        avail_idx_shadow: u16 = 0,
        last_used_idx: u16 = 0,
        last_polled_used_idx: u16 = 0,
        callback_enabled: bool = true,
        broken: bool = false,
        outstanding_chain_count: u16 = 0,
        num_added: u16 = 0,
        notification_count: usize = 0,
    };

    queues: [queue_capacity]QueueSlot = [_]QueueSlot{QueueSlot{}} ** queue_capacity,
    registered_queue_count: usize = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_ring_lab",
            .anchor = "drivers/virtio/virtio_ring.c",
            .provides_lab_validation = true,
            .touches_transport_mmio = false,
            .touches_dma_paths = false,
        };
    }

    pub fn defineQueue(
        self: *Self,
        queue_index: u16,
        descriptor_count: u16,
        layout: QueueLayout,
        uses_event_idx: bool,
        uses_indirect_descriptors: bool,
    ) !void {
        const index = try checkedQueueIndex(queue_index);
        if (descriptor_count == 0) return error.EmptyDescriptorCount;
        if (descriptor_count > max_descriptor_count) return error.DescriptorCountTooLarge;
        if (!std.math.isPowerOfTwo(descriptor_count)) return error.DescriptorCountMustBePowerOfTwo;

        const slot = &self.queues[index];
        if (slot.active) return error.QueueAlreadyDefined;

        slot.* = .{
            .active = true,
            .descriptor_count = descriptor_count,
            .layout = layout,
            .uses_event_idx = uses_event_idx,
            .uses_indirect_descriptors = uses_indirect_descriptors,
        };
        self.registered_queue_count += 1;
    }

    pub fn publishDescriptorChain(self: *Self, queue_index: u16) !void {
        const slot = try self.checkedQueueSlot(queue_index);
        if (slot.broken) return error.QueueBroken;
        if (slot.outstanding_chain_count == slot.descriptor_count) return error.QueueFull;

        slot.avail_idx_shadow +%= 1;
        slot.outstanding_chain_count += 1;
        slot.num_added += 1;
        if (slot.num_added == std.math.maxInt(u16)) {
            slot.notification_count += 1;
            slot.num_added = 0;
        }
    }

    pub fn prepareKick(self: *Self, queue_index: u16) !QueueNotificationSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = &self.queues[index];
        if (!slot.active) return error.QueueNotDefined;
        if (slot.broken) return error.QueueBroken;

        const needs_kick = slot.num_added != 0;
        if (needs_kick) {
            slot.notification_count += 1;
        }

        const summary = QueueNotificationSummary{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .avail_idx_shadow = slot.avail_idx_shadow,
            .last_used_idx = slot.last_used_idx,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .num_added = slot.num_added,
            .notification_count = slot.notification_count,
            .needs_kick = needs_kick,
        };
        slot.num_added = 0;
        return summary;
    }

    pub fn recordUsedChains(self: *Self, queue_index: u16, used_chain_count: u16) !void {
        const slot = try self.checkedQueueSlot(queue_index);
        if (used_chain_count == 0) return error.EmptyUsedBatch;
        if (used_chain_count > slot.outstanding_chain_count) return error.UsedBatchExceedsOutstanding;

        slot.outstanding_chain_count -= used_chain_count;
        slot.last_used_idx +%= used_chain_count;
    }

    pub fn pollUsedBuffers(self: *Self, queue_index: u16) !UsedBufferPollSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        if (slot.broken) return error.QueueBroken;
        const previous_poll_idx = slot.last_polled_used_idx;
        const newly_used_chain_count = slot.last_used_idx -% previous_poll_idx;

        const summary = UsedBufferPollSummary{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .last_used_idx = slot.last_used_idx,
            .last_polled_used_idx = previous_poll_idx,
            .newly_used_chain_count = newly_used_chain_count,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .has_newly_used_chains = newly_used_chain_count != 0,
        };
        slot.last_polled_used_idx = slot.last_used_idx;
        return summary;
    }

    pub fn disableCallback(self: *Self, queue_index: u16) !CallbackDisableSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.callback_enabled = false;

        const pending_used_chain_count = slot.last_used_idx -% slot.last_polled_used_idx;
        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .callback_enabled = slot.callback_enabled,
            .last_used_idx = slot.last_used_idx,
            .last_polled_used_idx = slot.last_polled_used_idx,
            .pending_used_chain_count = pending_used_chain_count,
            .should_poll = pending_used_chain_count != 0,
        };
    }

    pub fn enableCallback(self: *Self, queue_index: u16) !CallbackEnableSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.callback_enabled = true;

        const pending_used_chain_count = slot.last_used_idx -% slot.last_polled_used_idx;
        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .callback_enabled = slot.callback_enabled,
            .last_used_idx = slot.last_used_idx,
            .last_polled_used_idx = slot.last_polled_used_idx,
            .pending_used_chain_count = pending_used_chain_count,
            .should_poll = pending_used_chain_count != 0,
        };
    }

    pub fn enableCallbackPrepare(self: *Self, queue_index: u16) !CallbackEnablePrepareSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.callback_enabled = true;

        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .callback_enabled = slot.callback_enabled,
            .last_used_idx_snapshot = slot.last_used_idx,
        };
    }

    pub fn pollAfterEnable(
        self: *const Self,
        queue_index: u16,
        last_used_idx_snapshot: u16,
    ) !CallbackPreparedPollSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotDefined;
        if (slot.broken) return error.QueueBroken;

        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .last_used_idx_snapshot = last_used_idx_snapshot,
            .current_last_used_idx = slot.last_used_idx,
            .has_used_buffers_since_prepare = slot.last_used_idx != last_used_idx_snapshot,
        };
    }

    pub fn enableCallbackDelayed(self: *Self, queue_index: u16) !DelayedCallbackSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.callback_enabled = true;

        const pending_used_chain_count = slot.last_used_idx -% slot.last_polled_used_idx;
        const delay_budget_count = @as(u16, @intCast((@as(u32, slot.outstanding_chain_count) * 3) / 4));
        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .callback_enabled = slot.callback_enabled,
            .last_used_idx = slot.last_used_idx,
            .last_polled_used_idx = slot.last_polled_used_idx,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .delay_budget_count = delay_budget_count,
            .delayed_event_target_idx = slot.last_used_idx +% delay_budget_count,
            .pending_used_chain_count = pending_used_chain_count,
            .should_poll = pending_used_chain_count > delay_budget_count,
        };
    }

    pub fn resetQueue(self: *Self, queue_index: u16) !QueueResetSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        const pending_used_chain_count = slot.last_used_idx -% slot.last_polled_used_idx;
        if (slot.outstanding_chain_count != 0 or pending_used_chain_count != 0 or slot.num_added != 0) {
            return error.QueueResetRequiresDrainedQueue;
        }
        const descriptor_count = slot.descriptor_count;
        const layout = slot.layout;

        slot.avail_idx_shadow = 0;
        slot.last_used_idx = 0;
        slot.last_polled_used_idx = 0;
        slot.callback_enabled = true;
        slot.broken = false;
        slot.outstanding_chain_count = 0;
        slot.num_added = 0;
        slot.notification_count = 0;

        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .descriptor_count = descriptor_count,
            .layout = layout,
            .callback_enabled = slot.callback_enabled,
            .avail_idx_shadow = slot.avail_idx_shadow,
            .last_used_idx = slot.last_used_idx,
            .last_polled_used_idx = slot.last_polled_used_idx,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .pending_used_chain_count = pending_used_chain_count,
            .notification_count = slot.notification_count,
        };
    }

    pub fn recoverBrokenQueue(self: *Self, queue_index: u16) !BrokenQueueRecoverySummary {
        const guard = try self.brokenQueueRecoveryGuardSummary(queue_index);
        if (!guard.broken) return error.QueueNotBroken;
        if (!guard.recovery_allowed) return error.QueueResetRequiresDrainedQueue;

        const slot = try self.checkedQueueSlot(queue_index);
        const broken_before_recovery = slot.broken;
        const reset_summary = try self.resetQueue(queue_index);
        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .descriptor_count = reset_summary.descriptor_count,
            .layout = reset_summary.layout,
            .broken_before_recovery = broken_before_recovery,
            .callback_enabled_after_recovery = reset_summary.callback_enabled,
            .avail_idx_shadow_after_recovery = reset_summary.avail_idx_shadow,
            .last_used_idx_after_recovery = reset_summary.last_used_idx,
            .last_polled_used_idx_after_recovery = reset_summary.last_polled_used_idx,
            .outstanding_chain_count_after_recovery = reset_summary.outstanding_chain_count,
            .pending_used_chain_count_after_recovery = reset_summary.pending_used_chain_count,
            .notification_count_after_recovery = reset_summary.notification_count,
        };
    }

    pub fn resetGuardSummary(self: *const Self, queue_index: u16) !QueueResetGuardSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotDefined;

        const pending_used_chain_count = slot.last_used_idx -% slot.last_polled_used_idx;
        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .pending_used_chain_count = pending_used_chain_count,
            .unpublished_chain_count = slot.num_added,
            .reset_allowed = slot.outstanding_chain_count == 0 and pending_used_chain_count == 0 and slot.num_added == 0,
        };
    }

    pub fn breakQueue(self: *Self, queue_index: u16) !QueueBrokenSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.broken = true;
        return self.brokenSummary(queue_index);
    }

    pub fn unbreakQueue(self: *Self, queue_index: u16) !QueueBrokenSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.broken = false;
        return self.brokenSummary(queue_index);
    }

    pub fn brokenSummary(self: *const Self, queue_index: u16) !QueueBrokenSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotDefined;

        const pending_used_chain_count = slot.last_used_idx -% slot.last_polled_used_idx;
        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .broken = slot.broken,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .pending_used_chain_count = pending_used_chain_count,
            .unpublished_chain_count = slot.num_added,
        };
    }

    pub fn brokenQueueRecoveryGuardSummary(self: *const Self, queue_index: u16) !BrokenQueueRecoveryGuardSummary {
        const broken_summary = try self.brokenSummary(queue_index);
        return .{
            .anchor = broken_summary.anchor,
            .queue_index = broken_summary.queue_index,
            .broken = broken_summary.broken,
            .outstanding_chain_count = broken_summary.outstanding_chain_count,
            .pending_used_chain_count = broken_summary.pending_used_chain_count,
            .unpublished_chain_count = broken_summary.unpublished_chain_count,
            .recovery_allowed = broken_summary.broken and
                broken_summary.outstanding_chain_count == 0 and
                broken_summary.pending_used_chain_count == 0 and
                broken_summary.unpublished_chain_count == 0,
        };
    }

    pub fn teardownSummary(self: *const Self, queue_index: u16) !QueueTeardownSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotDefined;

        const pending_used_chain_count = slot.last_used_idx -% slot.last_polled_used_idx;
        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .broken = slot.broken,
            .callback_enabled = slot.callback_enabled,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .pending_used_chain_count = pending_used_chain_count,
            .unpublished_chain_count = slot.num_added,
            .notification_count = slot.notification_count,
            .requires_poll_before_teardown = pending_used_chain_count != 0,
            .ready_for_drained_teardown = slot.outstanding_chain_count == 0 and pending_used_chain_count == 0 and slot.num_added == 0,
        };
    }

    pub fn queueShapeSummary(self: *const Self, queue_index: u16) !QueueShapeSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotDefined;

        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .descriptor_count = slot.descriptor_count,
            .layout = slot.layout,
            .uses_event_idx = slot.uses_event_idx,
            .uses_indirect_descriptors = slot.uses_indirect_descriptors,
        };
    }

    pub fn notificationSummary(self: *const Self, queue_index: u16) !QueueNotificationSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotDefined;

        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .avail_idx_shadow = slot.avail_idx_shadow,
            .last_used_idx = slot.last_used_idx,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .num_added = slot.num_added,
            .notification_count = slot.notification_count,
            .needs_kick = slot.num_added != 0,
        };
    }

    pub fn registeredQueueCount(self: *const Self) usize {
        return self.registered_queue_count;
    }

    fn checkedQueueIndex(queue_index: u16) !usize {
        if (queue_index >= queue_capacity) return error.QueueIndexOutOfRange;
        return @intCast(queue_index);
    }

    fn checkedQueueSlot(self: *Self, queue_index: u16) !*QueueSlot {
        const index = try checkedQueueIndex(queue_index);
        const slot = &self.queues[index];
        if (!slot.active) return error.QueueNotDefined;
        return slot;
    }
};

test "phase10 virtio ring recovers a drained broken queue without dropping shape metadata" {
    var ring = VirtioRingLab{};
    try ring.defineQueue(0, 8, .packed_ring, true, true);

    try ring.publishDescriptorChain(0);
    _ = try ring.prepareKick(0);
    try ring.recordUsedChains(0, 1);
    _ = try ring.pollUsedBuffers(0);
    _ = try ring.breakQueue(0);

    const guard = try ring.brokenQueueRecoveryGuardSummary(0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", guard.anchor);
    try std.testing.expectEqual(@as(u16, 0), guard.queue_index);
    try std.testing.expect(guard.broken);
    try std.testing.expectEqual(@as(u16, 0), guard.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), guard.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), guard.unpublished_chain_count);
    try std.testing.expect(guard.recovery_allowed);

    const recovery = try ring.recoverBrokenQueue(0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", recovery.anchor);
    try std.testing.expectEqual(@as(u16, 0), recovery.queue_index);
    try std.testing.expectEqual(@as(u16, 8), recovery.descriptor_count);
    try std.testing.expectEqual(QueueLayout.packed_ring, recovery.layout);
    try std.testing.expect(recovery.broken_before_recovery);
    try std.testing.expect(recovery.callback_enabled_after_recovery);
    try std.testing.expectEqual(@as(u16, 0), recovery.avail_idx_shadow_after_recovery);
    try std.testing.expectEqual(@as(u16, 0), recovery.last_used_idx_after_recovery);
    try std.testing.expectEqual(@as(u16, 0), recovery.last_polled_used_idx_after_recovery);
    try std.testing.expectEqual(@as(u16, 0), recovery.outstanding_chain_count_after_recovery);
    try std.testing.expectEqual(@as(u16, 0), recovery.pending_used_chain_count_after_recovery);
    try std.testing.expectEqual(@as(usize, 0), recovery.notification_count_after_recovery);

    const broken_summary = try ring.brokenSummary(0);
    try std.testing.expect(!broken_summary.broken);

    const shape = try ring.queueShapeSummary(0);
    try std.testing.expectEqual(@as(u16, 8), shape.descriptor_count);
    try std.testing.expectEqual(QueueLayout.packed_ring, shape.layout);
    try std.testing.expect(shape.uses_event_idx);
    try std.testing.expect(shape.uses_indirect_descriptors);
}

test "phase10 virtio ring recovery guard keeps non-broken queues parked" {
    var ring = VirtioRingLab{};
    try ring.defineQueue(1, 8, .split, true, false);

    const guard = try ring.brokenQueueRecoveryGuardSummary(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", guard.anchor);
    try std.testing.expectEqual(@as(u16, 1), guard.queue_index);
    try std.testing.expect(!guard.broken);
    try std.testing.expectEqual(@as(u16, 0), guard.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), guard.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), guard.unpublished_chain_count);
    try std.testing.expect(!guard.recovery_allowed);

    try std.testing.expectError(error.QueueNotBroken, ring.recoverBrokenQueue(1));
}

test "phase10 virtio ring recovery guard reports outstanding and unpolled debt before recovery" {
    var ring = VirtioRingLab{};
    try ring.defineQueue(2, 8, .split, true, false);

    try ring.publishDescriptorChain(2);
    _ = try ring.breakQueue(2);

    var guard = try ring.brokenQueueRecoveryGuardSummary(2);
    try std.testing.expect(guard.broken);
    try std.testing.expectEqual(@as(u16, 1), guard.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), guard.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 1), guard.unpublished_chain_count);
    try std.testing.expect(!guard.recovery_allowed);
    try std.testing.expectError(error.QueueResetRequiresDrainedQueue, ring.recoverBrokenQueue(2));

    _ = try ring.unbreakQueue(2);
    _ = try ring.prepareKick(2);
    try ring.recordUsedChains(2, 1);
    _ = try ring.breakQueue(2);

    guard = try ring.brokenQueueRecoveryGuardSummary(2);
    try std.testing.expect(guard.broken);
    try std.testing.expectEqual(@as(u16, 0), guard.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), guard.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), guard.unpublished_chain_count);
    try std.testing.expect(!guard.recovery_allowed);
    try std.testing.expectError(error.QueueResetRequiresDrainedQueue, ring.recoverBrokenQueue(2));
}

test "phase10 virtio ring teardown summary marks drained broken queues ready for parked teardown" {
    var ring = VirtioRingLab{};
    try ring.defineQueue(3, 8, .packed_ring, true, true);

    try ring.publishDescriptorChain(3);
    _ = try ring.prepareKick(3);
    try ring.recordUsedChains(3, 1);
    _ = try ring.pollUsedBuffers(3);
    _ = try ring.breakQueue(3);

    const summary = try ring.teardownSummary(3);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 3), summary.queue_index);
    try std.testing.expect(summary.broken);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expectEqual(@as(usize, 1), summary.notification_count);
    try std.testing.expect(!summary.requires_poll_before_teardown);
    try std.testing.expect(summary.ready_for_drained_teardown);
}

test "phase10 virtio ring teardown summary keeps publish and poll debt visible" {
    var ring = VirtioRingLab{};
    try ring.defineQueue(4, 8, .split, true, false);

    try ring.publishDescriptorChain(4);

    var summary = try ring.teardownSummary(4);
    try std.testing.expectEqual(@as(u16, 1), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.unpublished_chain_count);
    try std.testing.expect(!summary.requires_poll_before_teardown);
    try std.testing.expect(!summary.ready_for_drained_teardown);

    _ = try ring.prepareKick(4);
    try ring.recordUsedChains(4, 1);
    _ = try ring.disableCallback(4);

    summary = try ring.teardownSummary(4);
    try std.testing.expectEqual(@as(u16, 0), summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), summary.unpublished_chain_count);
    try std.testing.expect(summary.requires_poll_before_teardown);
    try std.testing.expect(!summary.ready_for_drained_teardown);
}

test "phase10 virtio ring blocks poll helpers while the queue stays broken" {
    var ring = VirtioRingLab{};
    try ring.defineQueue(5, 8, .split, true, false);

    try ring.publishDescriptorChain(5);
    _ = try ring.breakQueue(5);

    try std.testing.expectError(error.QueueBroken, ring.pollUsedBuffers(5));
    try std.testing.expectError(error.QueueBroken, ring.pollAfterEnable(5, 0));

    const broken_summary = try ring.brokenSummary(5);
    try std.testing.expect(broken_summary.broken);
    try std.testing.expectEqual(@as(u16, 1), broken_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 1), broken_summary.unpublished_chain_count);
}

test "phase10 virtio ring keeps pending used debt visible without advancing poll bookkeeping while broken" {
    var ring = VirtioRingLab{};
    try ring.defineQueue(6, 8, .packed_ring, true, true);

    try ring.publishDescriptorChain(6);
    _ = try ring.prepareKick(6);
    const prepare_summary = try ring.enableCallbackPrepare(6);
    try ring.recordUsedChains(6, 1);
    _ = try ring.breakQueue(6);

    const broken_summary = try ring.brokenSummary(6);
    try std.testing.expect(broken_summary.broken);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), broken_summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.unpublished_chain_count);

    try std.testing.expectError(error.QueueBroken, ring.pollUsedBuffers(6));
    try std.testing.expectError(error.QueueBroken, ring.pollAfterEnable(6, prepare_summary.last_used_idx_snapshot));

    _ = try ring.unbreakQueue(6);

    const enable_poll = try ring.pollAfterEnable(6, prepare_summary.last_used_idx_snapshot);
    try std.testing.expectEqual(@as(u16, 0), enable_poll.last_used_idx_snapshot);
    try std.testing.expectEqual(@as(u16, 1), enable_poll.current_last_used_idx);
    try std.testing.expect(enable_poll.has_used_buffers_since_prepare);

    const used_poll = try ring.pollUsedBuffers(6);
    try std.testing.expectEqual(@as(u16, 1), used_poll.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), used_poll.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), used_poll.newly_used_chain_count);
    try std.testing.expect(used_poll.has_newly_used_chains);
}
