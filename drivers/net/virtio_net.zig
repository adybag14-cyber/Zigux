const std = @import("std");
const virtio = @import("virtio");

pub const feature_mergeable_rx_buffers: u16 = 15;
pub const feature_control_vq: u16 = 17;
pub const feature_multiqueue: u16 = 22;
pub const feature_hash_report: u16 = 57;
pub const feature_rss: u16 = 60;
pub const default_page_size: u32 = 4096;
pub const default_cache_line_size: u32 = 64;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_probe_queue_snapshot: bool,
    touches_live_dma: bool,
    touches_napi_poll: bool,
    touches_netdev_lifecycle: bool,
    touches_transport_recovery: bool,
};

pub const QueueFallbackReason = enum {
    none,
    multiqueue_not_negotiated,
    missing_control_vq,
    invalid_max_queue_pairs,
};

pub const RecoveryState = enum {
    stable,
    renegotiate_features,
    reset_required,
};

pub const ProbeRequest = struct {
    driver_feature_bits: []const u16,
    requested_queue_pairs: u16,
    max_queue_pairs: u16,
    transport_accepts_features: bool = true,
    device_signals_reset: bool = false,
};

pub const ProbeSnapshot = struct {
    anchor: []const u8,
    offered_feature_count: usize,
    negotiated_feature_count: usize,
    requested_queue_pairs: u16,
    max_queue_pairs: u16,
    planned_queue_pairs: u16,
    rx_queue_count: u16,
    tx_queue_count: u16,
    total_queue_count: u16,
    control_queue_index: ?u16,
    mergeable_rx_buffers: bool,
    has_rss: bool,
    has_rss_hash_report: bool,
    fallback_reason: QueueFallbackReason,
    recovery_state: RecoveryState,
};

pub const MergeableReceiveBufferRequest = struct {
    header_len: u16,
    average_packet_len: u32,
    min_buf_len: u32,
    headroom: u32 = 0,
    recycled_room: u32 = 0,
    page_size: u32 = default_page_size,
    cache_line_size: u32 = default_cache_line_size,
    skb_shared_info_size: u32 = 0,
};

pub const MergeableReceiveBufferPlan = struct {
    anchor: []const u8,
    planned_queue_pairs: u16,
    rx_queue_count: u16,
    headroom: u32,
    tailroom: u32,
    room: u32,
    requested_len: u32,
    requested_alloc_len: u32,
    page_size: u32,
    uses_recycled_room: bool,
    uses_page_pool: bool,
};

pub const ReceiveQueueRefillPath = enum {
    mergeable_allocation,
    recycled_room,
};

pub const ReceiveQueueRefillSummary = struct {
    anchor: []const u8,
    planned_queue_pairs: u16,
    rx_queue_count: u16,
    refill_path: ReceiveQueueRefillPath,
    keeps_aligned_room: bool,
    room: u32,
    recycled_room: u32,
    requested_len: u32,
    requested_alloc_len: u32,
};

pub const ReceiveQueueRefillBatchRequest = struct {
    queue_capacity: u16,
    buffers_posted: u16,
    batch_limit: u16 = 0,
};

pub const ReceiveQueueRefillBatchPlan = struct {
    anchor: []const u8,
    planned_queue_pairs: u16,
    rx_queue_count: u16,
    queue_capacity: u16,
    buffers_posted: u16,
    missing_buffers: u16,
    refill_count: u16,
    buffers_after_refill: u16,
    queue_will_be_full: bool,
    refill_path: ReceiveQueueRefillPath,
    total_posted_bytes: u32,
    total_allocation_bytes: u32,
};

pub const ReceiveQueueRefillReservationRequest = struct {
    queue_capacity: u16,
    buffers_posted: u16,
    batch_limit: u16 = 0,
    descriptors_available: u16,
    descriptors_per_buffer: u16 = 1,
};

pub const ReceiveQueueRefillReservationPlan = struct {
    anchor: []const u8,
    planned_queue_pairs: u16,
    rx_queue_count: u16,
    queue_capacity: u16,
    buffers_posted: u16,
    descriptors_available: u16,
    descriptors_per_buffer: u16,
    requested_refill_count: u16,
    refill_count: u16,
    descriptors_reserved: u16,
    buffers_after_reservation: u16,
    buffers_left_pending: u16,
    descriptor_budget_exhausted: bool,
    queue_will_be_full: bool,
    refill_path: ReceiveQueueRefillPath,
    total_posted_bytes: u32,
    total_allocation_bytes: u32,
};

pub const ReceiveQueueRefillNotifyRequest = struct {
    queue_was_empty: bool,
    notifications_enabled: bool = true,
    notify_after_descriptors: u16 = 0,
};

pub const ReceiveQueueRefillNotifyDecision = struct {
    anchor: []const u8,
    planned_queue_pairs: u16,
    rx_queue_count: u16,
    queue_was_empty: bool,
    queue_became_non_empty: bool,
    notifications_enabled: bool,
    notify_after_descriptors: u16,
    refill_count: u16,
    descriptors_reserved: u16,
    buffers_after_reservation: u16,
    buffers_left_pending: u16,
    descriptor_budget_exhausted: bool,
    queue_will_be_full: bool,
    refill_path: ReceiveQueueRefillPath,
    reached_notify_threshold: bool,
    should_notify: bool,
};

pub const VirtioNetProbeLab = struct {
    const Self = @This();

    core: virtio.VirtioCoreLabDevice,
    last_snapshot: ?ProbeSnapshot = null,
    last_mergeable_buffer_plan: ?MergeableReceiveBufferPlan = null,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_net_probe_lab",
            .anchor = "drivers/net/virtio_net.c",
            .provides_probe_queue_snapshot = true,
            .touches_live_dma = false,
            .touches_napi_poll = false,
            .touches_netdev_lifecycle = false,
            .touches_transport_recovery = false,
        };
    }

    pub fn init(device_feature_bits: []const u16) !Self {
        return .{
            .core = try virtio.VirtioCoreLabDevice.init(device_feature_bits),
        };
    }

    pub fn captureProbeSnapshot(self: *Self, request: ProbeRequest) !ProbeSnapshot {
        if (request.requested_queue_pairs == 0) return error.InvalidRequestedQueuePairs;

        self.core.reset();
        self.core.acknowledge();
        try self.core.attachDriver();
        self.core.setTransportFeatureAcceptance(request.transport_accepts_features);

        for (request.driver_feature_bits) |feature_bit| {
            try self.core.offerDriverFeature(feature_bit);
        }

        const negotiation = try self.core.finalizeFeatures();
        if (request.device_signals_reset) {
            self.core.noteNeedsReset();
        }

        const has_control_vq = try self.core.hasNegotiatedFeature(feature_control_vq);
        const has_multiqueue = try self.core.hasNegotiatedFeature(feature_multiqueue);
        const has_rss = try self.core.hasNegotiatedFeature(feature_rss);
        const has_hash_report = try self.core.hasNegotiatedFeature(feature_hash_report);
        const mergeable_rx_buffers = try self.core.hasNegotiatedFeature(feature_mergeable_rx_buffers);

        var max_queue_pairs: u16 = 1;
        var fallback_reason: QueueFallbackReason = .none;

        if (has_multiqueue or has_rss) {
            if (!has_control_vq) {
                fallback_reason = .missing_control_vq;
            } else if (request.max_queue_pairs == 0) {
                fallback_reason = .invalid_max_queue_pairs;
            } else {
                max_queue_pairs = request.max_queue_pairs;
            }
        } else if (request.requested_queue_pairs > 1) {
            fallback_reason = .multiqueue_not_negotiated;
        }

        const planned_queue_pairs = @min(request.requested_queue_pairs, max_queue_pairs);
        const rx_queue_count = try checkedMulU16(planned_queue_pairs, 1);
        const tx_queue_count = try checkedMulU16(planned_queue_pairs, 1);
        const data_queue_count = try checkedAddU16(rx_queue_count, tx_queue_count);
        const total_queue_count = try checkedAddU16(data_queue_count, if (has_control_vq) 1 else 0);

        const recovery_state: RecoveryState = if (self.core.hasStatus(virtio.DeviceStatus.device_needs_reset))
            .reset_required
        else if (!negotiation.accepted_by_transport)
            .renegotiate_features
        else
            .stable;

        const snapshot = ProbeSnapshot{
            .anchor = descriptor().anchor,
            .offered_feature_count = negotiation.offered_feature_count,
            .negotiated_feature_count = negotiation.negotiated_feature_count,
            .requested_queue_pairs = request.requested_queue_pairs,
            .max_queue_pairs = max_queue_pairs,
            .planned_queue_pairs = planned_queue_pairs,
            .rx_queue_count = rx_queue_count,
            .tx_queue_count = tx_queue_count,
            .total_queue_count = total_queue_count,
            .control_queue_index = if (has_control_vq) data_queue_count else null,
            .mergeable_rx_buffers = mergeable_rx_buffers,
            .has_rss = has_rss,
            .has_rss_hash_report = has_hash_report,
            .fallback_reason = fallback_reason,
            .recovery_state = recovery_state,
        };
        self.last_snapshot = snapshot;
        return snapshot;
    }

    pub fn planMergeableReceiveBuffer(
        self: *Self,
        snapshot: ProbeSnapshot,
        request: MergeableReceiveBufferRequest,
    ) !MergeableReceiveBufferPlan {
        if (!snapshot.mergeable_rx_buffers) return error.MergeableBuffersNotNegotiated;
        if (request.header_len == 0) return error.InvalidHeaderLength;
        if (request.min_buf_len == 0) return error.EmptyMinimumBufferLength;
        if (request.cache_line_size == 0 or !std.math.isPowerOfTwo(request.cache_line_size))
            return error.InvalidCacheLineSize;
        if (request.page_size <= request.header_len) return error.InvalidPageSize;
        if (request.recycled_room >= request.page_size) return error.InvalidRecycledRoom;
        if (request.min_buf_len > request.page_size - request.header_len) return error.MinBufferLenTooLarge;
        if (request.headroom > 0 and request.skb_shared_info_size == 0)
            return error.MissingSkbSharedInfoSize;

        const tailroom: u32 = if (request.headroom > 0) request.skb_shared_info_size else 0;
        const room = try alignToPowerOfTwo(try checkedAddU32(request.headroom, tailroom), request.cache_line_size);

        const requested_len = if (request.recycled_room > 0)
            request.page_size - request.recycled_room
        else blk: {
            const clamped_payload = std.math.clamp(
                request.average_packet_len,
                request.min_buf_len,
                request.page_size - request.header_len,
            );
            break :blk try alignToPowerOfTwo(
                try checkedAddU32(request.header_len, clamped_payload),
                request.cache_line_size,
            );
        };
        const requested_alloc_len = try checkedAddU32(requested_len, room);

        const plan = MergeableReceiveBufferPlan{
            .anchor = descriptor().anchor,
            .planned_queue_pairs = snapshot.planned_queue_pairs,
            .rx_queue_count = snapshot.rx_queue_count,
            .headroom = request.headroom,
            .tailroom = tailroom,
            .room = room,
            .requested_len = requested_len,
            .requested_alloc_len = requested_alloc_len,
            .page_size = request.page_size,
            .uses_recycled_room = request.recycled_room > 0,
            .uses_page_pool = true,
        };
        self.last_mergeable_buffer_plan = plan;
        return plan;
    }

    pub fn summarizeReceiveQueueRefill(self: *Self) !ReceiveQueueRefillSummary {
        const plan = self.last_mergeable_buffer_plan orelse return error.MergeableBufferPlanUnavailable;
        return .{
            .anchor = descriptor().anchor,
            .planned_queue_pairs = plan.planned_queue_pairs,
            .rx_queue_count = plan.rx_queue_count,
            .refill_path = if (plan.uses_recycled_room) .recycled_room else .mergeable_allocation,
            .keeps_aligned_room = plan.room > 0 and !plan.uses_recycled_room,
            .room = plan.room,
            .recycled_room = if (plan.uses_recycled_room) plan.page_size - plan.requested_len else 0,
            .requested_len = plan.requested_len,
            .requested_alloc_len = plan.requested_alloc_len,
        };
    }

    pub fn planReceiveQueueRefillBatch(
        self: *Self,
        request: ReceiveQueueRefillBatchRequest,
    ) !ReceiveQueueRefillBatchPlan {
        if (request.queue_capacity == 0) return error.InvalidQueueCapacity;
        if (request.buffers_posted > request.queue_capacity) return error.InvalidBuffersPosted;

        const summary = try self.summarizeReceiveQueueRefill();
        const missing_buffers = request.queue_capacity - request.buffers_posted;
        const refill_count = if (request.batch_limit == 0)
            missing_buffers
        else
            @min(missing_buffers, request.batch_limit);
        const buffers_after_refill = try checkedAddU16(request.buffers_posted, refill_count);

        return .{
            .anchor = descriptor().anchor,
            .planned_queue_pairs = summary.planned_queue_pairs,
            .rx_queue_count = summary.rx_queue_count,
            .queue_capacity = request.queue_capacity,
            .buffers_posted = request.buffers_posted,
            .missing_buffers = missing_buffers,
            .refill_count = refill_count,
            .buffers_after_refill = buffers_after_refill,
            .queue_will_be_full = buffers_after_refill == request.queue_capacity,
            .refill_path = summary.refill_path,
            .total_posted_bytes = try checkedMulU32(summary.requested_len, refill_count),
            .total_allocation_bytes = try checkedMulU32(summary.requested_alloc_len, refill_count),
        };
    }

    pub fn reserveReceiveQueueRefillDescriptors(
        self: *Self,
        request: ReceiveQueueRefillReservationRequest,
    ) !ReceiveQueueRefillReservationPlan {
        if (request.descriptors_per_buffer == 0) return error.InvalidDescriptorsPerBuffer;

        const summary = try self.summarizeReceiveQueueRefill();
        const batch = try self.planReceiveQueueRefillBatch(.{
            .queue_capacity = request.queue_capacity,
            .buffers_posted = request.buffers_posted,
            .batch_limit = request.batch_limit,
        });
        const descriptor_budget = request.descriptors_available / request.descriptors_per_buffer;
        const refill_count = @min(batch.refill_count, descriptor_budget);
        const descriptors_reserved = try checkedMulU16(refill_count, request.descriptors_per_buffer);
        const buffers_after_reservation = try checkedAddU16(request.buffers_posted, refill_count);

        return .{
            .anchor = batch.anchor,
            .planned_queue_pairs = batch.planned_queue_pairs,
            .rx_queue_count = batch.rx_queue_count,
            .queue_capacity = batch.queue_capacity,
            .buffers_posted = batch.buffers_posted,
            .descriptors_available = request.descriptors_available,
            .descriptors_per_buffer = request.descriptors_per_buffer,
            .requested_refill_count = batch.refill_count,
            .refill_count = refill_count,
            .descriptors_reserved = descriptors_reserved,
            .buffers_after_reservation = buffers_after_reservation,
            .buffers_left_pending = batch.refill_count - refill_count,
            .descriptor_budget_exhausted = refill_count < batch.refill_count,
            .queue_will_be_full = buffers_after_reservation == batch.queue_capacity,
            .refill_path = batch.refill_path,
            .total_posted_bytes = try checkedMulU32(summary.requested_len, refill_count),
            .total_allocation_bytes = try checkedMulU32(summary.requested_alloc_len, refill_count),
        };
    }

    pub fn decideReceiveQueueRefillNotify(
        self: *Self,
        reservation: ReceiveQueueRefillReservationPlan,
        request: ReceiveQueueRefillNotifyRequest,
    ) ReceiveQueueRefillNotifyDecision {
        _ = self;
        const notify_after_descriptors = if (request.notify_after_descriptors == 0)
            reservation.descriptors_per_buffer
        else
            request.notify_after_descriptors;
        const queue_became_non_empty = request.queue_was_empty and reservation.refill_count != 0;
        const reached_notify_threshold = reservation.descriptors_reserved != 0 and
            reservation.descriptors_reserved >= notify_after_descriptors;

        return .{
            .anchor = reservation.anchor,
            .planned_queue_pairs = reservation.planned_queue_pairs,
            .rx_queue_count = reservation.rx_queue_count,
            .queue_was_empty = request.queue_was_empty,
            .queue_became_non_empty = queue_became_non_empty,
            .notifications_enabled = request.notifications_enabled,
            .notify_after_descriptors = notify_after_descriptors,
            .refill_count = reservation.refill_count,
            .descriptors_reserved = reservation.descriptors_reserved,
            .buffers_after_reservation = reservation.buffers_after_reservation,
            .buffers_left_pending = reservation.buffers_left_pending,
            .descriptor_budget_exhausted = reservation.descriptor_budget_exhausted,
            .queue_will_be_full = reservation.queue_will_be_full,
            .refill_path = reservation.refill_path,
            .reached_notify_threshold = reached_notify_threshold,
            .should_notify = request.notifications_enabled and
                reservation.descriptors_reserved != 0 and
                (queue_became_non_empty or reached_notify_threshold),
        };
    }

    fn checkedMulU16(lhs: u16, rhs: u16) !u16 {
        const value = @as(u32, lhs) * rhs;
        return std.math.cast(u16, value) orelse error.QueueCountOverflow;
    }

    fn checkedAddU16(lhs: u16, rhs: u16) !u16 {
        const value = @as(u32, lhs) + rhs;
        return std.math.cast(u16, value) orelse error.QueueCountOverflow;
    }

    fn checkedAddU32(lhs: u32, rhs: u32) !u32 {
        const value = @as(u64, lhs) + rhs;
        return std.math.cast(u32, value) orelse error.BufferLengthOverflow;
    }

    fn checkedMulU32(lhs: u32, rhs: u16) !u32 {
        const value = @as(u64, lhs) * rhs;
        return std.math.cast(u32, value) orelse error.BufferLengthOverflow;
    }

    fn alignToPowerOfTwo(value: u32, alignment: u32) !u32 {
        const widened = std.mem.alignForward(u64, value, alignment);
        return std.math.cast(u32, widened) orelse error.BufferLengthOverflow;
    }
}
