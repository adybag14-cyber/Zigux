const std = @import("std");

pub const queue_capacity: usize = 8;
pub const max_descriptor_count: u16 = 1024;
pub const packed_notification_wrap_bit: u16 = 1 << 15;

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

pub const QueuePublishReadinessBlocker = enum {
    queue_broken,
    queue_full,
};

pub const QueuePublishReadinessSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    descriptor_count: u16,
    outstanding_chain_count: u16,
    unpublished_chain_count: u16,
    available_descriptor_count: u16,
    broken: bool,
    can_publish: bool,
    blocker: ?QueuePublishReadinessBlocker,
};

pub const NotificationDataSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    descriptor_count: u16,
    layout: QueueLayout,
    avail_idx_shadow: u16,
    next_avail_idx: u16,
    next_avail_wrap_counter: bool,
    encoded_next: u16,
    notification_data: u32,
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

pub const BrokenQueueSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    broken: bool,
    callback_enabled: bool,
    last_used_idx: u16,
    last_polled_used_idx: u16,
    outstanding_chain_count: u16,
    unpublished_chain_count: u16,
    pending_used_chain_count: u16,
};

pub const QueueResetReadinessBlocker = enum {
    queue_broken,
    unpublished_chains,
    outstanding_chains,
    unpolled_used_chains,
};

pub const QueueResetReadinessSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    callback_enabled: bool,
    broken: bool,
    avail_idx_shadow: u16,
    last_used_idx: u16,
    last_polled_used_idx: u16,
    outstanding_chain_count: u16,
    unpublished_chain_count: u16,
    pending_used_chain_count: u16,
    reset_ready: bool,
    blocker: ?QueueResetReadinessBlocker,
};

pub const QueueResetSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    descriptor_count: u16,
    layout: QueueLayout,
    uses_event_idx: bool,
    uses_indirect_descriptors: bool,
    callback_enabled: bool,
    avail_idx_shadow: u16,
    last_used_idx: u16,
    last_polled_used_idx: u16,
    outstanding_chain_count: u16,
    unpublished_chain_count: u16,
    pending_used_chain_count: u16,
    notification_count: usize,
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
        if (slot.broken) return error.QueueBroken;
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

    pub fn disableCallback(self: *Self, queue_index: u16) !void {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.callback_enabled = false;
    }

    pub fn enableCallback(self: *Self, queue_index: u16) !CallbackEnableSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        if (slot.broken) return error.QueueBroken;
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

    pub fn enableCallbackDelayed(self: *Self, queue_index: u16) !DelayedCallbackSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        if (slot.broken) return error.QueueBroken;
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

    pub fn queuePublishReadinessSummary(self: *const Self, queue_index: u16) !QueuePublishReadinessSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotDefined;

        const blocker: ?QueuePublishReadinessBlocker = if (slot.broken)
            .queue_broken
        else if (slot.outstanding_chain_count == slot.descriptor_count)
            .queue_full
        else
            null;

        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .descriptor_count = slot.descriptor_count,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .unpublished_chain_count = slot.num_added,
            .available_descriptor_count = slot.descriptor_count - slot.outstanding_chain_count,
            .broken = slot.broken,
            .can_publish = blocker == null,
            .blocker = blocker,
        };
    }

    pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotDefined;

        const pending_used_chain_count = slot.last_used_idx -% slot.last_polled_used_idx;
        const blocker: ?QueueResetReadinessBlocker = if (slot.broken)
            .queue_broken
        else if (slot.num_added != 0)
            .unpublished_chains
        else if (slot.outstanding_chain_count != 0)
            .outstanding_chains
        else if (pending_used_chain_count != 0)
            .unpolled_used_chains
        else
            null;

        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .callback_enabled = slot.callback_enabled,
            .broken = slot.broken,
            .avail_idx_shadow = slot.avail_idx_shadow,
            .last_used_idx = slot.last_used_idx,
            .last_polled_used_idx = slot.last_polled_used_idx,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .unpublished_chain_count = slot.num_added,
            .pending_used_chain_count = pending_used_chain_count,
            .reset_ready = blocker == null,
            .blocker = blocker,
        };
    }

    pub fn resetQueue(self: *Self, queue_index: u16) !QueueResetSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        const pending_used_chain_count = slot.last_used_idx -% slot.last_polled_used_idx;

        if (slot.broken) return error.QueueResetWhileBroken;
        if (slot.num_added != 0) return error.QueueResetHasUnpublishedChains;
        if (slot.outstanding_chain_count != 0) return error.QueueResetHasOutstandingChains;
        if (pending_used_chain_count != 0) return error.QueueResetHasUnpolledUsedChains;

        slot.avail_idx_shadow = 0;
        slot.last_used_idx = 0;
        slot.last_polled_used_idx = 0;
        slot.callback_enabled = true;
        slot.notification_count = 0;

        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .descriptor_count = slot.descriptor_count,
            .layout = slot.layout,
            .uses_event_idx = slot.uses_event_idx,
            .uses_indirect_descriptors = slot.uses_indirect_descriptors,
            .callback_enabled = slot.callback_enabled,
            .avail_idx_shadow = slot.avail_idx_shadow,
            .last_used_idx = slot.last_used_idx,
            .last_polled_used_idx = slot.last_polled_used_idx,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .unpublished_chain_count = slot.num_added,
            .pending_used_chain_count = 0,
            .notification_count = slot.notification_count,
        };
    }

    pub fn markBroken(self: *Self, queue_index: u16) !BrokenQueueSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.broken = true;
        slot.callback_enabled = false;
        return brokenQueueSummaryFromSlot(queue_index, slot);
    }

    pub fn clearBroken(self: *Self, queue_index: u16) !BrokenQueueSummary {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.broken = false;
        return brokenQueueSummaryFromSlot(queue_index, slot);
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

    pub fn notificationDataSummary(self: *const Self, queue_index: u16) !NotificationDataSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotDefined;

        const NextState = struct {
            next_avail_idx: u16,
            next_avail_wrap_counter: bool,
            encoded_next: u16,
        };

        const next: NextState = switch (slot.layout) {
            .split => .{
                .next_avail_idx = slot.avail_idx_shadow,
                .next_avail_wrap_counter = false,
                .encoded_next = slot.avail_idx_shadow,
            },
            .packed_ring => blk: {
                const wrapped_total: u32 = slot.avail_idx_shadow;
                const next_avail_idx: u16 = @intCast(wrapped_total % slot.descriptor_count);
                const wrap_counter = ((wrapped_total / slot.descriptor_count) & 1) != 0;
                const encoded_next = next_avail_idx |
                    (if (wrap_counter) packed_notification_wrap_bit else 0);
                break :blk .{
                    .next_avail_idx = next_avail_idx,
                    .next_avail_wrap_counter = wrap_counter,
                    .encoded_next = encoded_next,
                };
            },
        };

        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .descriptor_count = slot.descriptor_count,
            .layout = slot.layout,
            .avail_idx_shadow = slot.avail_idx_shadow,
            .next_avail_idx = next.next_avail_idx,
            .next_avail_wrap_counter = next.next_avail_wrap_counter,
            .encoded_next = next.encoded_next,
            .notification_data = (@as(u32, next.encoded_next) << 16) | queue_index,
        };
    }

    pub fn brokenQueueSummary(self: *const Self, queue_index: u16) !BrokenQueueSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotDefined;
        return brokenQueueSummaryFromQueue(queue_index, slot);
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

    fn brokenQueueSummaryFromSlot(queue_index: u16, slot: *const QueueSlot) BrokenQueueSummary {
        return brokenQueueSummaryFromQueue(queue_index, slot.*);
    }

    fn brokenQueueSummaryFromQueue(queue_index: u16, slot: QueueSlot) BrokenQueueSummary {
        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .broken = slot.broken,
            .callback_enabled = slot.callback_enabled,
            .last_used_idx = slot.last_used_idx,
            .last_polled_used_idx = slot.last_polled_used_idx,
            .outstanding_chain_count = slot.outstanding_chain_count,
            .unpublished_chain_count = slot.num_added,
            .pending_used_chain_count = slot.last_used_idx -% slot.last_polled_used_idx,
        };
    }
};