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
        if (slot.outstanding_chain_count == slot.descriptor_count) return error.QueueFull;

        slot.avail_idx_shadow +%= 1;
        slot.outstanding_chain_count += 1;
        slot.num_added += 1;
    }

    pub fn prepareKick(self: *Self, queue_index: u16) !QueueNotificationSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = &self.queues[index];
        if (!slot.active) return error.QueueNotDefined;

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
