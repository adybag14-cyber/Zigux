const std = @import("std");
const virtio = @import("virtio");

pub const feature_mergeable_rx_buffers: u16 = 15;
pub const feature_control_vq: u16 = 17;
pub const feature_multiqueue: u16 = 22;
pub const feature_hash_report: u16 = 57;
pub const feature_rss: u16 = 60;

pub const RecoveryAction = enum {
    freeze,
    restore,
};

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

pub const RssRecoveryState = enum {
    not_requested,
    requested_but_unavailable,
    downgraded_single_queue,
    active,
};

pub const QueueRecoveryAction = enum {
    none,
    clamp_queue_pairs,
    degrade_to_single_queue,
    renegotiate_features,
    require_reset,
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
    rss_recovery_state: RssRecoveryState,
    fallback_reason: QueueFallbackReason,
    recovery_state: RecoveryState,
    queue_recovery_action: QueueRecoveryAction,
};

pub const QueueRecoverySummary = struct {
    anchor: []const u8,
    action: RecoveryAction,
    was_frozen: bool,
    is_frozen: bool,
    planned_queue_pairs_available: bool,
    remembered_planned_queue_pairs: u16,
    remembered_total_queue_count: u16,
    remembered_control_queue_index: ?u16,
    remembered_rss_recovery_state: RssRecoveryState,
    remembered_fallback_reason: QueueFallbackReason,
    remembered_recovery_state: RecoveryState,
    remembered_queue_recovery_action: QueueRecoveryAction,
    recovery_generation: u16,
};

pub const QueueResumeReadiness = enum {
    ready,
    requires_feature_renegotiation,
    requires_reset,
};

pub const QueueResumeScope = enum {
    data_queues_only,
    data_and_control_queue,
    data_control_and_rss,
};

pub const QueueResumeSummary = struct {
    anchor: []const u8,
    is_frozen: bool,
    recovery_generation: u16,
    readiness: QueueResumeReadiness,
    rebuild_scope: QueueResumeScope,
    resume_queue_pairs: u16,
    resume_total_queue_count: u16,
    resume_control_queue_index: ?u16,
    remembered_rss_recovery_state: RssRecoveryState,
    remembered_fallback_reason: QueueFallbackReason,
    remembered_queue_recovery_action: QueueRecoveryAction,
    requires_control_queue_restore: bool,
    requires_rss_reapply: bool,
    requires_fresh_probe_snapshot: bool,
};

pub const ReceiveBufferMode = enum {
    one_buffer_per_rx,
    mergeable_rx_buffers,
};

pub const ReceiveRefillSummary = struct {
    anchor: []const u8,
    recovery_generation: u16,
    readiness: QueueResumeReadiness,
    resume_scope: QueueResumeScope,
    buffer_mode: ReceiveBufferMode,
    refill_queue_pairs: u16,
    refill_rx_queue_count: u16,
    refill_total_queue_count: u16,
    resume_control_queue_index: ?u16,
    remembered_queue_recovery_action: QueueRecoveryAction,
    requires_control_queue_restore: bool,
    requires_rss_reapply: bool,
    requires_mergeable_buffer_headroom: bool,
    requires_fresh_probe_snapshot: bool,
    requires_post_restore_probe_replay: bool,
};

pub const MergeableBufferLengthSource = enum {
    page_minus_room,
    observed_average_packet,
    minimum_buffer_floor,
    page_size_cap,
};

pub const MergeableBufferLengthRequest = struct {
    observed_average_packet_len_bytes: u16,
    min_buf_len_bytes: u16,
    xdp_headroom_bytes: u16 = 0,
    page_bytes: u16 = 4096,
    cache_line_bytes: u16 = 64,
    skb_shared_info_bytes: u16 = 320,
};

pub const MergeableBufferLengthSummary = struct {
    anchor: []const u8,
    source: MergeableBufferLengthSource,
    observed_average_packet_len_bytes: u16,
    min_buf_len_bytes: u16,
    xdp_headroom_bytes: u16,
    tailroom_bytes: u16,
    room_bytes: u16,
    payload_limit_bytes: u16,
    selected_payload_bytes: u16,
    hdr_len_bytes: u16,
    submit_len_bytes: u16,
    allocation_len_bytes: u16,
};

pub const TransmitRecycleOrder = enum {
    data_queues_only,
    after_control_queue_restore,
    after_control_queue_restore_and_rss_reapply,
};

pub const TransmitRecycleSummary = struct {
    anchor: []const u8,
    recovery_generation: u16,
    readiness: QueueResumeReadiness,
    recycle_order: TransmitRecycleOrder,
    recycle_queue_pairs: u16,
    recycle_tx_queue_count: u16,
    recycle_total_queue_count: u16,
    resume_control_queue_index: ?u16,
    remembered_queue_recovery_action: QueueRecoveryAction,
    requires_control_queue_restore: bool,
    requires_rss_reapply: bool,
    requires_receive_refill_coordination: bool,
    requires_fresh_probe_snapshot: bool,
    requires_post_restore_probe_replay: bool,
};

pub const VirtioNetProbeLab = struct {
    const Self = @This();

    core: virtio.VirtioCoreLabDevice,
    last_snapshot: ?ProbeSnapshot = null,
    frozen_snapshot: ?ProbeSnapshot = null,
    transport_recovery_frozen: bool = false,
    recovery_generation: u16 = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_net_probe_lab",
            .anchor = "drivers/net/virtio_net.c",
            .provides_probe_queue_snapshot = true,
            .touches_live_dma = false,
            .touches_napi_poll = false,
            .touches_netdev_lifecycle = false,
            .touches_transport_recovery = true,
        };
    }

    pub fn init(device_feature_bits: []const u16) !Self {
        return .{
            .core = try virtio.VirtioCoreLabDevice.init(device_feature_bits),
        };
    }

    pub fn captureProbeSnapshot(self: *Self, request: ProbeRequest) !ProbeSnapshot {
        if (self.transport_recovery_frozen) return error.TransportRecoveryFrozen;
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
            .rss_recovery_state = summarizeRssRecoveryState(
                featureRequested(request.driver_feature_bits, feature_rss),
                has_rss,
                request.requested_queue_pairs,
                planned_queue_pairs,
            ),
            .fallback_reason = fallback_reason,
            .recovery_state = recovery_state,
            .queue_recovery_action = summarizeQueueRecoveryAction(
                recovery_state,
                request.requested_queue_pairs,
                planned_queue_pairs,
            ),
        };
        self.last_snapshot = snapshot;
        return snapshot;
    }

    pub fn freezeForRecovery(self: *Self) !QueueRecoverySummary {
        if (self.transport_recovery_frozen) return error.TransportRecoveryAlreadyFrozen;

        const snapshot = self.last_snapshot orelse return error.ProbeSnapshotUnavailable;
        self.transport_recovery_frozen = true;
        self.frozen_snapshot = snapshot;

        return summarizeRecovery(.freeze, false, true, false, snapshot, self.recovery_generation);
    }

    pub fn restoreAfterRecovery(self: *Self) !QueueRecoverySummary {
        if (!self.transport_recovery_frozen) return error.TransportRecoveryNotFrozen;

        const snapshot = self.frozen_snapshot orelse return error.ProbeSnapshotUnavailable;
        self.transport_recovery_frozen = false;
        self.frozen_snapshot = null;
        self.last_snapshot = null;
        self.recovery_generation = try checkedAddU16(self.recovery_generation, 1);

        return summarizeRecovery(.restore, true, false, true, snapshot, self.recovery_generation);
    }

    pub fn planQueueResume(self: *Self) !QueueResumeSummary {
        if (!self.transport_recovery_frozen) return error.TransportRecoveryNotFrozen;

        const snapshot = self.frozen_snapshot orelse return error.ProbeSnapshotUnavailable;
        return summarizeQueueResume(snapshot, self.recovery_generation);
    }

    pub fn planReceiveRefill(self: *Self) !ReceiveRefillSummary {
        if (!self.transport_recovery_frozen) return error.TransportRecoveryNotFrozen;

        const snapshot = self.frozen_snapshot orelse return error.ProbeSnapshotUnavailable;
        const resume_summary = summarizeQueueResume(snapshot, self.recovery_generation);
        return summarizeReceiveRefill(snapshot, resume_summary);
    }

    pub fn planMergeableBufferLength(
        self: *Self,
        request: MergeableBufferLengthRequest,
    ) !MergeableBufferLengthSummary {
        if (!self.transport_recovery_frozen) return error.TransportRecoveryNotFrozen;
        if (request.page_bytes == 0) return error.InvalidPageBytes;
        if (request.cache_line_bytes == 0) return error.InvalidCacheLineBytes;
        if (!std.math.isPowerOfTwo(request.cache_line_bytes)) return error.InvalidCacheLineBytes;

        const snapshot = self.frozen_snapshot orelse return error.ProbeSnapshotUnavailable;
        return summarizeMergeableBufferLength(snapshot, request);
    }

    pub fn planTransmitRecycle(self: *Self) !TransmitRecycleSummary {
        if (!self.transport_recovery_frozen) return error.TransportRecoveryNotFrozen;

        const snapshot = self.frozen_snapshot orelse return error.ProbeSnapshotUnavailable;
        const resume_summary = summarizeQueueResume(snapshot, self.recovery_generation);
        return summarizeTransmitRecycle(snapshot, resume_summary);
    }

    fn checkedMulU16(lhs: u16, rhs: u16) !u16 {
        const value = @as(u32, lhs) * rhs;
        return std.math.cast(u16, value) orelse error.QueueCountOverflow;
    }

    fn checkedAddU16(lhs: u16, rhs: u16) !u16 {
        const value = @as(u32, lhs) + rhs;
        return std.math.cast(u16, value) orelse error.QueueCountOverflow;
    }

    fn checkedAddBufferLengthU16(lhs: u16, rhs: u16) !u16 {
        const value = @as(u32, lhs) + rhs;
        return std.math.cast(u16, value) orelse error.BufferLengthOverflow;
    }

    fn alignForwardU16(value: u16, alignment: u16) !u16 {
        const widened_alignment = @as(u32, alignment);
        const widened_value = @as(u32, value);
        const adjusted = widened_value + widened_alignment - 1;
        const aligned = adjusted & ~(widened_alignment - 1);
        return std.math.cast(u16, aligned) orelse error.BufferLengthOverflow;
    }

    fn featureRequested(feature_bits: []const u16, wanted: u16) bool {
        for (feature_bits) |feature_bit| {
            if (feature_bit == wanted) return true;
        }
        return false;
    }

    fn summarizeRssRecoveryState(
        requested_rss: bool,
        has_rss: bool,
        requested_queue_pairs: u16,
        planned_queue_pairs: u16,
    ) RssRecoveryState {
        if (!requested_rss) return .not_requested;
        if (has_rss and planned_queue_pairs > 1) return .active;
        if (has_rss and requested_queue_pairs > planned_queue_pairs) return .downgraded_single_queue;
        return .requested_but_unavailable;
    }

    fn summarizeQueueRecoveryAction(
        recovery_state: RecoveryState,
        requested_queue_pairs: u16,
        planned_queue_pairs: u16,
    ) QueueRecoveryAction {
        return switch (recovery_state) {
            .reset_required => .require_reset,
            .renegotiate_features => .renegotiate_features,
            .stable => if (planned_queue_pairs < requested_queue_pairs)
                if (planned_queue_pairs <= 1) .degrade_to_single_queue else .clamp_queue_pairs
            else
                .none,
        };
    }

    fn summarizeRecovery(
        action: RecoveryAction,
        was_frozen: bool,
        is_frozen: bool,
        planned_queue_pairs_available: bool,
        snapshot: ProbeSnapshot,
        recovery_generation: u16,
    ) QueueRecoverySummary {
        return .{
            .anchor = descriptor().anchor,
            .action = action,
            .was_frozen = was_frozen,
            .is_frozen = is_frozen,
            .planned_queue_pairs_available = planned_queue_pairs_available,
            .remembered_planned_queue_pairs = snapshot.planned_queue_pairs,
            .remembered_total_queue_count = snapshot.total_queue_count,
            .remembered_control_queue_index = snapshot.control_queue_index,
            .remembered_rss_recovery_state = snapshot.rss_recovery_state,
            .remembered_fallback_reason = snapshot.fallback_reason,
            .remembered_recovery_state = snapshot.recovery_state,
            .remembered_queue_recovery_action = snapshot.queue_recovery_action,
            .recovery_generation = recovery_generation,
        };
    }

    fn summarizeQueueResume(
        snapshot: ProbeSnapshot,
        recovery_generation: u16,
    ) QueueResumeSummary {
        const readiness: QueueResumeReadiness = switch (snapshot.recovery_state) {
            .stable => .ready,
            .renegotiate_features => .requires_feature_renegotiation,
            .reset_required => .requires_reset,
        };
        const requires_control_queue_restore = snapshot.control_queue_index != null;
        const requires_rss_reapply = snapshot.rss_recovery_state == .active;
        const rebuild_scope: QueueResumeScope = if (requires_rss_reapply)
            .data_control_and_rss
        else if (requires_control_queue_restore)
            .data_and_control_queue
        else
            .data_queues_only;

        return .{
            .anchor = descriptor().anchor,
            .is_frozen = true,
            .recovery_generation = recovery_generation,
            .readiness = readiness,
            .rebuild_scope = rebuild_scope,
            .resume_queue_pairs = snapshot.planned_queue_pairs,
            .resume_total_queue_count = snapshot.total_queue_count,
            .resume_control_queue_index = snapshot.control_queue_index,
            .remembered_rss_recovery_state = snapshot.rss_recovery_state,
            .remembered_fallback_reason = snapshot.fallback_reason,
            .remembered_queue_recovery_action = snapshot.queue_recovery_action,
            .requires_control_queue_restore = requires_control_queue_restore,
            .requires_rss_reapply = requires_rss_reapply,
            .requires_fresh_probe_snapshot = true,
        };
    }

    fn summarizeReceiveRefill(
        snapshot: ProbeSnapshot,
        resume_summary: QueueResumeSummary,
    ) ReceiveRefillSummary {
        return .{
            .anchor = descriptor().anchor,
            .recovery_generation = resume_summary.recovery_generation,
            .readiness = resume_summary.readiness,
            .resume_scope = resume_summary.rebuild_scope,
            .buffer_mode = if (snapshot.mergeable_rx_buffers) .mergeable_rx_buffers else .one_buffer_per_rx,
            .refill_queue_pairs = snapshot.planned_queue_pairs,
            .refill_rx_queue_count = snapshot.rx_queue_count,
            .refill_total_queue_count = snapshot.total_queue_count,
            .resume_control_queue_index = snapshot.control_queue_index,
            .remembered_queue_recovery_action = resume_summary.remembered_queue_recovery_action,
            .requires_control_queue_restore = resume_summary.requires_control_queue_restore,
            .requires_rss_reapply = resume_summary.requires_rss_reapply,
            .requires_mergeable_buffer_headroom = snapshot.mergeable_rx_buffers,
            .requires_fresh_probe_snapshot = resume_summary.requires_fresh_probe_snapshot,
            .requires_post_restore_probe_replay = true,
        };
    }

    fn summarizeMergeableBufferLength(
        snapshot: ProbeSnapshot,
        request: MergeableBufferLengthRequest,
    ) !MergeableBufferLengthSummary {
        if (!snapshot.mergeable_rx_buffers) return error.ReceiveBufferModeNotMergeable;

        const hdr_len_bytes: u16 = if (snapshot.has_rss_hash_report) 20 else 12;
        if (request.page_bytes <= hdr_len_bytes) return error.PageTooSmallForMergeableBuffer;

        const tailroom_bytes: u16 = if (request.xdp_headroom_bytes != 0)
            request.skb_shared_info_bytes
        else
            0;
        const headroom_plus_tailroom = try checkedAddBufferLengthU16(request.xdp_headroom_bytes, tailroom_bytes);
        const room_bytes = try alignForwardU16(headroom_plus_tailroom, request.cache_line_bytes);
        if (room_bytes >= request.page_bytes) return error.PageTooSmallForMergeableBuffer;

        const payload_limit_bytes = request.page_bytes - hdr_len_bytes;
        if (room_bytes != 0) {
            const submit_len_bytes = request.page_bytes - room_bytes;
            if (submit_len_bytes <= hdr_len_bytes) return error.PageTooSmallForMergeableBuffer;

            return .{
                .anchor = descriptor().anchor,
                .source = .page_minus_room,
                .observed_average_packet_len_bytes = request.observed_average_packet_len_bytes,
                .min_buf_len_bytes = request.min_buf_len_bytes,
                .xdp_headroom_bytes = request.xdp_headroom_bytes,
                .tailroom_bytes = tailroom_bytes,
                .room_bytes = room_bytes,
                .payload_limit_bytes = payload_limit_bytes,
                .selected_payload_bytes = submit_len_bytes - hdr_len_bytes,
                .hdr_len_bytes = hdr_len_bytes,
                .submit_len_bytes = submit_len_bytes,
                .allocation_len_bytes = request.page_bytes,
            };
        }

        var selected_payload_bytes = request.observed_average_packet_len_bytes;
        var source: MergeableBufferLengthSource = .observed_average_packet;

        if (selected_payload_bytes < request.min_buf_len_bytes) {
            selected_payload_bytes = request.min_buf_len_bytes;
            source = .minimum_buffer_floor;
        } else if (selected_payload_bytes > payload_limit_bytes) {
            selected_payload_bytes = payload_limit_bytes;
            source = .page_size_cap;
        }

        const raw_submit_len_bytes = try checkedAddBufferLengthU16(hdr_len_bytes, selected_payload_bytes);
        const submit_len_bytes = try alignForwardU16(raw_submit_len_bytes, request.cache_line_bytes);

        return .{
            .anchor = descriptor().anchor,
            .source = source,
            .observed_average_packet_len_bytes = request.observed_average_packet_len_bytes,
            .min_buf_len_bytes = request.min_buf_len_bytes,
            .xdp_headroom_bytes = request.xdp_headroom_bytes,
            .tailroom_bytes = tailroom_bytes,
            .room_bytes = room_bytes,
            .payload_limit_bytes = payload_limit_bytes,
            .selected_payload_bytes = selected_payload_bytes,
            .hdr_len_bytes = hdr_len_bytes,
            .submit_len_bytes = submit_len_bytes,
            .allocation_len_bytes = submit_len_bytes,
        };
    }

    fn summarizeTransmitRecycle(
        snapshot: ProbeSnapshot,
        resume_summary: QueueResumeSummary,
    ) TransmitRecycleSummary {
        const recycle_order: TransmitRecycleOrder = if (resume_summary.requires_rss_reapply)
            .after_control_queue_restore_and_rss_reapply
        else if (resume_summary.requires_control_queue_restore)
            .after_control_queue_restore
        else
            .data_queues_only;

        return .{
            .anchor = descriptor().anchor,
            .recovery_generation = resume_summary.recovery_generation,
            .readiness = resume_summary.readiness,
            .recycle_order = recycle_order,
            .recycle_queue_pairs = snapshot.planned_queue_pairs,
            .recycle_tx_queue_count = snapshot.tx_queue_count,
            .recycle_total_queue_count = snapshot.total_queue_count,
            .resume_control_queue_index = snapshot.control_queue_index,
            .remembered_queue_recovery_action = resume_summary.remembered_queue_recovery_action,
            .requires_control_queue_restore = resume_summary.requires_control_queue_restore,
            .requires_rss_reapply = resume_summary.requires_rss_reapply,
            .requires_receive_refill_coordination = snapshot.mergeable_rx_buffers or
                resume_summary.requires_control_queue_restore or
                resume_summary.requires_rss_reapply,
            .requires_fresh_probe_snapshot = resume_summary.requires_fresh_probe_snapshot,
            .requires_post_restore_probe_replay = true,
        };
    }
};