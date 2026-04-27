const std = @import("std");
const virtio = @import("virtio");

pub const feature_mergeable_rx_buffers: u16 = 15;
pub const feature_control_vq: u16 = 17;
pub const feature_multiqueue: u16 = 22;
pub const feature_version_1: u16 = 32;
pub const feature_hash_report: u16 = 57;
pub const feature_rss: u16 = 60;
pub const feature_guest_udp_tunnel_gso: u16 = 65;
pub const feature_host_udp_tunnel_gso: u16 = 67;

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

pub const QueueRecoveryAction = enum {
    none,
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
    header_shape: HeaderShape,
    hdr_len_bytes: u16,
    uses_hash_report_header: bool,
    uses_udp_tunnel_header: bool,
    rss_summary: RssSummary,
    fallback_reason: QueueFallbackReason,
    recovery_state: RecoveryState,
    queue_recovery_action: QueueRecoveryAction,
};

pub const VirtioNetProbeLab = struct {
    const Self = @This();

    core: virtio.VirtioCoreLabDevice,
    last_snapshot: ?ProbeSnapshot = null,

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
        const has_version_1 = try self.core.hasNegotiatedFeature(feature_version_1);
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
            .rss_summary = rss_summary,
            .fallback_reason = fallback_reason,
            .recovery_state = recovery_state,
            .queue_recovery_action = queue_recovery_action,
        };
        self.last_snapshot = snapshot;
        return snapshot;
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
                .degrade_to_single_queue
            else
                .none,
        };
    }

    const HeaderShapeSummary = struct {
        shape: HeaderShape,
        hdr_len_bytes: u16,
        uses_hash_report_header: bool,
        uses_udp_tunnel_header: bool,
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
};
