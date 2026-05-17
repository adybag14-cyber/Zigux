const std = @import("std");

pub const max_queue_size: u16 = 1024;

pub const QueueKind = enum {
    split,
    packed_ring,
};

pub const QueueDefinition = struct {
    queue_index: u16,
    queue_size: u16,
    kind: QueueKind,
    event_idx_enabled: bool,
    notification_data_enabled: bool,
};

pub const PrepareKickSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    needs_kick: bool,
    avail_idx_shadow: u16,
    outstanding_chain_count: u16,
    num_added: u16,
    notification_count: usize,
};

pub const PollUsedBuffersSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    last_used_idx: u16,
    last_polled_used_idx: u16,
    newly_used_chain_count: u16,
    outstanding_chain_count: u16,
    has_newly_used_chains: bool,
};

const QueueState = struct {
    defined: bool = false,
    definition: QueueDefinition = .{
        .queue_index = 0,
        .queue_size = 0,
        .kind = .split,
        .event_idx_enabled = false,
        .notification_data_enabled = false,
    },
    avail_idx_shadow: u16 = 0,
    used_idx_shadow: u16 = 0,
    last_polled_used_idx: u16 = 0,
    outstanding_chain_count: u16 = 0,
    num_added: u16 = 0,
    notification_count: usize = 0,
};

pub const VirtioRingLab = struct {
    const Self = @This();
    const max_queues = 8;

    queues: [max_queues]QueueState = [_]QueueState{QueueState{}} ** max_queues,

    pub fn defineQueue(
        self: *Self,
        queue_index: u16,
        queue_size: u16,
        kind: QueueKind,
        event_idx_enabled: bool,
        notification_data_enabled: bool,
    ) !void {
        if (queue_index >= max_queues) return error.QueueIndexOutOfRange;
        if (queue_size == 0) return error.EmptyQueueSize;
        if (queue_size > max_queue_size) return error.QueueSizeTooLarge;
        if (!std.math.isPowerOfTwo(queue_size)) return error.QueueSizeMustBePowerOfTwo;

        const queue = &self.queues[queue_index];
        if (queue.defined) return error.QueueAlreadyDefined;

        queue.* = .{
            .defined = true,
            .definition = .{
                .queue_index = queue_index,
                .queue_size = queue_size,
                .kind = kind,
                .event_idx_enabled = event_idx_enabled,
                .notification_data_enabled = notification_data_enabled,
            },
        };
    }

    pub fn publishDescriptorChain(self: *Self, queue_index: u16) !void {
        var queue = try self.requireQueue(queue_index);
        if (queue.outstanding_chain_count == std.math.maxInt(u16)) return error.OutstandingChainCountOverflow;
        if (queue.num_added == std.math.maxInt(u16)) return error.PendingPublishCountOverflow;

        queue.avail_idx_shadow +%= 1;
        queue.outstanding_chain_count += 1;
        queue.num_added += 1;
    }

    pub fn prepareKick(self: *Self, queue_index: u16) !PrepareKickSummary {
        var queue = try self.requireQueue(queue_index);
        const needs_kick = queue.num_added != 0 and queue.outstanding_chain_count != 0;
        if (needs_kick) queue.notification_count += 1;
        const published_count = queue.num_added;
        queue.num_added = 0;

        return .{
            .anchor = anchor(),
            .queue_index = queue_index,
            .needs_kick = needs_kick,
            .avail_idx_shadow = queue.avail_idx_shadow,
            .outstanding_chain_count = queue.outstanding_chain_count,
            .num_added = published_count,
            .notification_count = queue.notification_count,
        };
    }

    pub fn recordUsedChains(self: *Self, queue_index: u16, used_count: u16) !void {
        var queue = try self.requireQueue(queue_index);
        if (used_count > queue.outstanding_chain_count) return error.UsedChainCountExceedsOutstanding;
        queue.used_idx_shadow +%= used_count;
    }

    pub fn pollUsedBuffers(self: *Self, queue_index: u16) !PollUsedBuffersSummary {
        var queue = try self.requireQueue(queue_index);
        const before = queue.last_polled_used_idx;
        const last_used_idx = queue.used_idx_shadow;
        const delta = last_used_idx -% before;
        if (delta > queue.outstanding_chain_count) return error.PolledUsedChainCountExceedsOutstanding;

        queue.last_polled_used_idx = last_used_idx;
        queue.outstanding_chain_count -= delta;

        return .{
            .anchor = anchor(),
            .queue_index = queue_index,
            .last_used_idx = last_used_idx,
            .last_polled_used_idx = before,
            .newly_used_chain_count = delta,
            .outstanding_chain_count = queue.outstanding_chain_count,
            .has_newly_used_chains = delta != 0,
        };
    }

    fn requireQueue(self: *Self, queue_index: u16) !*QueueState {
        if (queue_index >= max_queues) return error.QueueIndexOutOfRange;
        const queue = &self.queues[queue_index];
        if (!queue.defined) return error.QueueNotDefined;
        return queue;
    }

    fn anchor() []const u8 {
        return "drivers/virtio/virtio_ring.c";
    }
};