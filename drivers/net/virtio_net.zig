const std = @import("std");
const virtio = @import("virtio");

pub const feature_mergeable_rx_buffers: u16 = 15;
pub const feature_control_vq: u16 = 17;
pub const feature_multiqueue: u16 = 22;
pub const feature_any_layout: u16 = 27;
pub const feature_version_1: u16 = 32;
pub const feature_guest_tso4: u16 = 7;
pub const feature_guest_tso6: u16 = 8;
pub const feature_guest_ecn: u16 = 9;
pub const feature_guest_ufo: u16 = 10;
pub const feature_hash_report: u16 = 57;
pub const feature_rss: u16 = 60;
pub const feature_guest_uso4: u16 = 54;
pub const feature_guest_uso6: u16 = 55;
pub const feature_guest_udp_tunnel_gso: u16 = 65;
pub const feature_host_udp_tunnel_gso: u16 = 67;
pub const ethernet_default_mtu: u16 = 1500;
pub const ethernet_header_len: u16 = 14;
pub const vlan_header_len: u16 = 4;
pub const good_packet_len: u16 = ethernet_header_len + vlan_header_len + ethernet_default_mtu;
pub const ip_max_mtu: u16 = 65_535;

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
    requested_queue_pairs_clamped,
};

pub const RecoveryState = enum {
    stable,
    renegotiate_features,
    reset_required,
};

pub const QueueRecoveryAction = enum {
    none,
    clamp_queue_pairs,
    degrade_to_single_queue,
    renegotiate_features,
    require_reset,
};

pub const RssSummary = enum {
    not_requested,
    requested_but_unavailable,
    hash_report_only,
    downgraded_single_queue,
    active,
};

pub const HeaderShape = enum {
    legacy,
    mrg_rxbuf,
    hash_report,
    hash_report_tunnel,
};

pub const ReceiveBufferMode = enum {
    small,
    mergeable,
    big_packets,
};

pub const BigPacketReason = enum {
    none,
    mtu_above_default,
    guest_gso,
};

pub const ReceiveQueueRefillPath = enum {
    fresh_allocation,
    recycled_room_reuse,
};

pub const HeaderScatterPolicy = enum {
    separate_header_sg,
    combined_header_and_data,
};

pub const XdpConstraint = enum {
    not_requested,
    ready,
    blocked_by_big_packets,
    blocked_by_split_header,
};

pub const ProbeRequest = struct {
    driver_feature_bits: []const u16,
    requested_queue_pairs: u16,
    max_queue_pairs: u16,
    mtu: u16 = ethernet_default_mtu,
    transport_accepts_features: bool = true,
    device_signals_reset: bool = false,
    xdp_requested: bool = false,
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
    header_shape: HeaderShape,
    hdr_len_bytes: u16,
    uses_hash_report_header: bool,
    uses_udp_tunnel_header: bool,
    receive_buffer_mode: ReceiveBufferMode,
    big_packet_reason: BigPacketReason,
    header_scatter_policy: HeaderScatterPolicy,
    required_headroom_bytes: u16,
    xdp_constraint: XdpConstraint,
    rss_summary: RssSummary,
    fallback_reason: QueueFallbackReason,
    recovery_state: RecoveryState,
    queue_recovery_action: QueueRecoveryAction,
    requested_mtu: u16,
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
    remembered_rss_summary: RssSummary,
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
    remembered_rss_summary: RssSummary,
    remembered_fallback_reason: QueueFallbackReason,
    remembered_queue_recovery_action: QueueRecoveryAction,
    requires_control_queue_restore: bool,
    requires_rss_reapply: bool,
    requires_fresh_probe_snapshot: bool,
};

pub const MergeableReceiveRefillSummary = struct {
    anchor: []const u8,
    rx_queue_entries: u16,
    refill_path: ReceiveQueueRefillPath,
    uses_mergeable_buffers: bool,
    packet_budget_bytes: u32,
    min_buf_len_bytes: u32,
    required_headroom_bytes: u16,
    recycled_room_bytes: u32,
    fresh_allocation_bytes: u32,
    big_packet_reason: BigPacketReason,
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
        const has_any_layout = try self.core.hasNegotiatedFeature(feature_any_layout);
        const has_version_1 = try self.core.hasNegotiatedFeature(feature_version_1);
        const has_guest_tso4 = try self.core.hasNegotiatedFeature(feature_guest_tso4);
        const has_guest_tso6 = try self.core.hasNegotiatedFeature(feature_guest_tso6);
        const has_guest_ecn = try self.core.hasNegotiatedFeature(feature_guest_ecn);
        const has_guest_ufo = try self.core.hasNegotiatedFeature(feature_guest_ufo);
        const has_guest_uso4 = try self.core.hasNegotiatedFeature(feature_guest_uso4);
        const has_guest_uso6 = try self.core.hasNegotiatedFeature(feature_guest_uso6);
        const has_guest_udp_tunnel_gso = try self.core.hasNegotiatedFeature(feature_guest_udp_tunnel_gso);
        const has_host_udp_tunnel_gso = try self.core.hasNegotiatedFeature(feature_host_udp_tunnel_gso);
        const requested_rss = featureRequested(request.driver_feature_bits, feature_rss);
        const requested_hash_report = featureRequested(request.driver_feature_bits, feature_hash_report);

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

        if (fallback_reason == .none and request.requested_queue_pairs > max_queue_pairs) {
            fallback_reason = .requested_queue_pairs_clamped;
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
        const queue_recovery_action = summarizeQueueRecoveryAction(
            recovery_state,
            request.requested_queue_pairs,
            planned_queue_pairs,
        );
        const rss_summary = summarizeRss(
            requested_rss,
            requested_hash_report,
            has_rss,
            has_hash_report,
            request.requested_queue_pairs,
            planned_queue_pairs,
        );
        const header_shape = summarizeHeaderShape(
            mergeable_rx_buffers,
            has_hash_report,
            has_version_1,
            has_guest_udp_tunnel_gso,
            has_host_udp_tunnel_gso,
        );
        const guest_gso = has_guest_tso4 or has_guest_tso6 or has_guest_ecn or has_guest_ufo or
            has_guest_uso4 or has_guest_uso6;
        const receive_buffer_mode = summarizeReceiveBufferMode(
            mergeable_rx_buffers,
            request.mtu,
            guest_gso,
        );
        const header_scatter = summarizeHeaderScatter(
            has_any_layout or has_version_1,
            header_shape.hdr_len_bytes,
        );
        const xdp_constraint = summarizeXdpConstraint(
            request.xdp_requested,
            receive_buffer_mode,
            mergeable_rx_buffers,
            header_scatter.policy,
        );

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
            .header_shape = header_shape.shape,
            .hdr_len_bytes = header_shape.hdr_len_bytes,
            .uses_hash_report_header = header_shape.uses_hash_report_header,
            .uses_udp_tunnel_header = header_shape.uses_udp_tunnel_header,
            .receive_buffer_mode = receive_buffer_mode.mode,
            .big_packet_reason = receive_buffer_mode.big_packet_reason,
            .header_scatter_policy = header_scatter.policy,
            .required_headroom_bytes = header_scatter.required_headroom_bytes,
            .xdp_constraint = xdp_constraint,
            .rss_summary = rss_summary,
            .fallback_reason = fallback_reason,
            .recovery_state = recovery_state,
            .queue_recovery_action = queue_recovery_action,
            .requested_mtu = request.mtu,
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

    pub fn planMergeableReceiveRefill(
        self: *Self,
        rx_queue_entries: u16,
    ) !MergeableReceiveRefillSummary {
        if (rx_queue_entries == 0) return error.InvalidRxQueueEntries;

        const snapshot = self.last_snapshot orelse return error.ProbeSnapshotUnavailable;
        return summarizeMergeableReceiveRefill(snapshot, rx_queue_entries);
    }

    fn checkedMulU16(lhs: u16, rhs: u16) !u16 {
        const value = @as(u32, lhs) * rhs;
        return std.math.cast(u16, value) orelse error.QueueCountOverflow;
    }

    fn checkedAddU16(lhs: u16, rhs: u16) !u16 {
        const value = @as(u32, lhs) + rhs;
        return std.math.cast(u16, value) orelse error.QueueCountOverflow;
    }

    fn featureRequested(feature_bits: []const u16, wanted: u16) bool {
        for (feature_bits) |feature_bit| {
            if (feature_bit == wanted) return true;
        }
        return false;
    }

    fn summarizeRss(
        requested_rss: bool,
        requested_hash_report: bool,
        has_rss: bool,
        has_hash_report: bool,
        requested_queue_pairs: u16,
        planned_queue_pairs: u16,
    ) RssSummary {
        if (!requested_rss and !requested_hash_report) return .not_requested;
        if (has_rss and planned_queue_pairs > 1) return .active;
        if (has_rss and requested_queue_pairs > planned_queue_pairs) return .downgraded_single_queue;
        if (has_hash_report) return .hash_report_only;
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
            .remembered_rss_summary = snapshot.rss_summary,
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
        const requires_rss_reapply = snapshot.rss_summary == .active;
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
            .remembered_rss_summary = snapshot.rss_summary,
            .remembered_fallback_reason = snapshot.fallback_reason,
            .remembered_queue_recovery_action = snapshot.queue_recovery_action,
            .requires_control_queue_restore = requires_control_queue_restore,
            .requires_rss_reapply = requires_rss_reapply,
            .requires_fresh_probe_snapshot = true,
        };
    }

    fn summarizeMergeableReceiveRefill(
        snapshot: ProbeSnapshot,
        rx_queue_entries: u16,
    ) MergeableReceiveRefillSummary {
        const packet_payload_bytes: u16 = switch (snapshot.big_packet_reason) {
            .guest_gso => ip_max_mtu,
            .none, .mtu_above_default => snapshot.requested_mtu,
        };
        const packet_budget_bytes = @as(u32, snapshot.hdr_len_bytes) +
            ethernet_header_len +
            vlan_header_len +
            packet_payload_bytes;
        const per_buffer_budget = std.math.divCeil(u32, packet_budget_bytes, rx_queue_entries) catch unreachable;
        const hdr_len_bytes = @as(u32, snapshot.hdr_len_bytes);
        const min_buf_len_bytes = if (snapshot.mergeable_rx_buffers)
            @max(@max(per_buffer_budget, hdr_len_bytes) - hdr_len_bytes, good_packet_len)
        else
            good_packet_len;
        const recycled_room_bytes = if (snapshot.mergeable_rx_buffers)
            @min(@as(u32, snapshot.required_headroom_bytes), min_buf_len_bytes)
        else
            0;
        const fresh_allocation_bytes = min_buf_len_bytes - recycled_room_bytes;

        return .{
            .anchor = descriptor().anchor,
            .rx_queue_entries = rx_queue_entries,
            .refill_path = if (recycled_room_bytes > 0) .recycled_room_reuse else .fresh_allocation,
            .uses_mergeable_buffers = snapshot.mergeable_rx_buffers,
            .packet_budget_bytes = packet_budget_bytes,
            .min_buf_len_bytes = min_buf_len_bytes,
            .required_headroom_bytes = snapshot.required_headroom_bytes,
            .recycled_room_bytes = recycled_room_bytes,
            .fresh_allocation_bytes = fresh_allocation_bytes,
            .big_packet_reason = snapshot.big_packet_reason,
        };
    }

    const HeaderShapeSummary = struct {
        shape: HeaderShape,
        hdr_len_bytes: u16,
        uses_hash_report_header: bool,
        uses_udp_tunnel_header: bool,
    };

    const ReceiveBufferSummary = struct {
        mode: ReceiveBufferMode,
        big_packet_reason: BigPacketReason,
    };

    const HeaderScatterSummary = struct {
        policy: HeaderScatterPolicy,
        required_headroom_bytes: u16,
    };

    fn summarizeHeaderShape(
        mergeable_rx_buffers: bool,
        has_hash_report: bool,
        has_version_1: bool,
        has_guest_udp_tunnel_gso: bool,
        has_host_udp_tunnel_gso: bool,
    ) HeaderShapeSummary {
        if (has_guest_udp_tunnel_gso or has_host_udp_tunnel_gso) {
            return .{
                .shape = .hash_report_tunnel,
                .hdr_len_bytes = 24,
                .uses_hash_report_header = true,
                .uses_udp_tunnel_header = true,
            };
        }

        if (has_hash_report) {
            return .{
                .shape = .hash_report,
                .hdr_len_bytes = 20,
                .uses_hash_report_header = true,
                .uses_udp_tunnel_header = false,
            };
        }

        if (mergeable_rx_buffers or has_version_1) {
            return .{
                .shape = .mrg_rxbuf,
                .hdr_len_bytes = 12,
                .uses_hash_report_header = false,
                .uses_udp_tunnel_header = false,
            };
        }

        return .{
            .shape = .legacy,
            .hdr_len_bytes = 10,
            .uses_hash_report_header = false,
            .uses_udp_tunnel_header = false,
        };
    }

    fn summarizeReceiveBufferMode(
        mergeable_rx_buffers: bool,
        mtu: u16,
        guest_gso: bool,
    ) ReceiveBufferSummary {
        if (mergeable_rx_buffers) {
            const big_packet_reason: BigPacketReason = if (mtu > ethernet_default_mtu)
                .mtu_above_default
            else if (guest_gso)
                .guest_gso
            else
                .none;
            return .{
                .mode = .mergeable,
                .big_packet_reason = big_packet_reason,
            };
        }

        if (mtu > ethernet_default_mtu) {
            return .{
                .mode = .big_packets,
                .big_packet_reason = .mtu_above_default,
            };
        }

        if (guest_gso) {
            return .{
                .mode = .big_packets,
                .big_packet_reason = .guest_gso,
            };
        }

        return .{
            .mode = .small,
            .big_packet_reason = .none,
        };
    }

    fn summarizeHeaderScatter(
        any_header_sg: bool,
        hdr_len_bytes: u16,
    ) HeaderScatterSummary {
        if (any_header_sg) {
            return .{
                .policy = .combined_header_and_data,
                .required_headroom_bytes = hdr_len_bytes,
            };
        }

        return .{
            .policy = .separate_header_sg,
            .required_headroom_bytes = 0,
        };
    }

    fn summarizeXdpConstraint(
        xdp_requested: bool,
        receive_buffer_mode: ReceiveBufferSummary,
        mergeable_rx_buffers: bool,
        header_scatter_policy: HeaderScatterPolicy,
    ) XdpConstraint {
        if (!xdp_requested) return .not_requested;
        if (receive_buffer_mode.mode == .big_packets) return .blocked_by_big_packets;
        if (mergeable_rx_buffers and header_scatter_policy == .separate_header_sg) {
            return .blocked_by_split_header;
        }
        return .ready;
    }
};
