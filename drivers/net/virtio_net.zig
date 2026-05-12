const std = @import("std");

pub const page_size: u32 = 4096;
pub const default_headroom_bytes: u16 = 12;
pub const default_queue_pairs: u16 = 1;
pub const tunnel_header_len_bytes: u16 = 24;

pub const QueueFallbackReason = enum {
    none,
    device_single_queue,
    negotiated_pair_cap,
};

pub const HeaderShape = enum {
    legacy,
    hash_report,
    hash_report_tunnel,
};

pub const ReceiveBufferMode = enum {
    single_page,
    mergeable,
    recycled_room,
};

pub const BigPacketReason = enum {
    none,
    exceeds_single_buffer,
};

pub const RecoveryAction = enum {
    freeze,
    restore,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_probe_snapshot: bool,
    provides_queue_topology_summary: bool,
    provides_mergeable_receive_buffer_planner: bool,
    provides_queue_recovery_planner: bool,
    touches_live_dma: bool,
    touches_net_device: bool,
    touches_control_virtqueue_runtime: bool,
};

pub const ProbeRequest = struct {
    requested_queue_pairs: u16,
    device_queue_pairs: u16,
    has_control_vq: bool = false,
    has_rss: bool = false,
    uses_hash_report: bool = true,
    uses_udp_tunnel_headers: bool = false,
};

pub const ProbeSnapshot = struct {
    anchor: []const u8,
    requested_queue_pairs: u16,
    device_queue_pairs: u16,
    effective_queue_pairs: u16,
    fallback_reason: QueueFallbackReason,
    control_vq_present: bool,
    rss_enabled: bool,
    header_shape: HeaderShape,
    hdr_len_bytes: u16,
};

pub const QueueTopologySummary = struct {
    anchor: []const u8,
    requested_queue_pairs: u16,
    device_queue_pairs: u16,
    effective_queue_pairs: u16,
    receive_queue_count: u16,
    transmit_queue_count: u16,
    first_receive_queue_index: u16,
    first_transmit_queue_index: u16,
    first_control_queue_index: ?u16,
    control_queue_count: u16,
    total_queue_count: u16,
    fallback_reason: QueueFallbackReason,
    multi_queue: bool,
    control_vq_present: bool,
    rss_enabled: bool,
};

pub const MergeableReceiveBufferRequest = struct {
    packet_bytes: u32,
    existing_room_bytes: u32 = 0,
    headroom_bytes: u16 = default_headroom_bytes,
    mergeable_rx_bufs: bool = true,
};

pub const MergeableReceiveBufferPlan = struct {
    anchor: []const u8,
    packet_bytes: u32,
    total_bytes: u32,
    required_buffers: u16,
    buffer_mode: ReceiveBufferMode,
    big_packet_reason: BigPacketReason,
    reuses_existing_room: bool,
    fits_single_page: bool,
    uses_mergeable_path: bool,
};

pub const RecoverySummary = struct {
    anchor: []const u8,
    action: RecoveryAction,
    was_resetting: bool,
    is_resetting: bool,
    remembered_queue_pairs: u16,
    remembered_total_queue_count: u16,
    remembered_control_queue_count: u16,
    receive_buffer_refill_required: bool,
    mergeable_buffer_refill_required: bool,
    recovery_generation: u16,
};

pub const RecoveryQueuePlan = struct {
    anchor: []const u8,
    effective_queue_pairs: u16,
    receive_queue_count: u16,
    transmit_queue_count: u16,
    first_receive_queue_index: u16,
    first_transmit_queue_index: u16,
    first_control_queue_index: ?u16,
    total_queue_count: u16,
    rss_enabled: bool,
    requires_receive_queue_restore: bool,
    requires_transmit_queue_restore: bool,
    requires_control_queue_restore: bool,
    requires_receive_buffer_refill: bool,
    requires_mergeable_buffer_refill: bool,
};

pub const VirtioNetProbeLab = struct {
    const Self = @This();

    last_probe_snapshot: ?ProbeSnapshot = null,
    last_queue_topology_summary: ?QueueTopologySummary = null,
    last_mergeable_plan: ?MergeableReceiveBufferPlan = null,
    frozen_probe_snapshot: ?ProbeSnapshot = null,
    frozen_queue_topology_summary: ?QueueTopologySummary = null,
    frozen_mergeable_plan: ?MergeableReceiveBufferPlan = null,
    resetting: bool = false,
    recovery_generation: u16 = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_net_probe_lab",
            .anchor = "drivers/net/virtio_net.c",
            .provides_probe_snapshot = true,
            .provides_queue_topology_summary = true,
            .provides_mergeable_receive_buffer_planner = true,
            .provides_queue_recovery_planner = true,
            .touches_live_dma = false,
            .touches_net_device = false,
            .touches_control_virtqueue_runtime = false,
        };
    }

    pub fn init() Self {
        return .{};
    }

    pub fn captureProbeSnapshot(self: *Self, request: ProbeRequest) ProbeSnapshot {
        const snapshot = ProbeSnapshot{
            .anchor = descriptor().anchor,
            .requested_queue_pairs = request.requested_queue_pairs,
            .device_queue_pairs = request.device_queue_pairs,
            .effective_queue_pairs = negotiatedQueuePairs(request),
            .fallback_reason = queueFallbackReason(request),
            .control_vq_present = request.has_control_vq,
            .rss_enabled = request.has_rss,
            .header_shape = queueHeaderShape(request),
            .hdr_len_bytes = if (request.uses_udp_tunnel_headers) tunnel_header_len_bytes else default_headroom_bytes,
        };
        self.last_probe_snapshot = snapshot;
        return snapshot;
    }

    pub fn summarizeQueueTopology(self: *Self, request: ProbeRequest) !QueueTopologySummary {
        const effective_queue_pairs = negotiatedQueuePairs(request);
        const first_transmit_queue_index = effective_queue_pairs;
        const control_queue_count: u16 = if (request.has_control_vq) 1 else 0;
        const first_control_queue_index = if (control_queue_count == 0)
            null
        else
            try checkedAddU16(first_transmit_queue_index, effective_queue_pairs);
        const total_queue_count = try checkedAddU16(
            try checkedAddU16(effective_queue_pairs, effective_queue_pairs),
            control_queue_count,
        );

        const summary = QueueTopologySummary{
            .anchor = descriptor().anchor,
            .requested_queue_pairs = request.requested_queue_pairs,
            .device_queue_pairs = request.device_queue_pairs,
            .effective_queue_pairs = effective_queue_pairs,
            .receive_queue_count = effective_queue_pairs,
            .transmit_queue_count = effective_queue_pairs,
            .first_receive_queue_index = 0,
            .first_transmit_queue_index = first_transmit_queue_index,
            .first_control_queue_index = first_control_queue_index,
            .control_queue_count = control_queue_count,
            .total_queue_count = total_queue_count,
            .fallback_reason = queueFallbackReason(request),
            .multi_queue = effective_queue_pairs > 1,
            .control_vq_present = request.has_control_vq,
            .rss_enabled = request.has_rss and effective_queue_pairs > 1,
        };
        self.last_queue_topology_summary = summary;
        return summary;
    }

    pub fn planMergeableReceiveBuffer(self: *Self, request: MergeableReceiveBufferRequest) !MergeableReceiveBufferPlan {
        const total_bytes = request.packet_bytes + request.headroom_bytes;
        const reuses_existing_room = request.existing_room_bytes >= total_bytes;
        const fits_single_page = total_bytes <= page_size;

        const required_buffers_u32 = if (reuses_existing_room)
            @as(u32, 1)
        else
            std.math.divCeil(u32, total_bytes, page_size) catch unreachable;
        const required_buffers = std.math.cast(u16, required_buffers_u32) orelse return error.BufferCountOverflow;

        if (!reuses_existing_room and !fits_single_page and !request.mergeable_rx_bufs) {
            return error.MergeableReceiveBuffersRequired;
        }

        const plan = MergeableReceiveBufferPlan{
            .anchor = descriptor().anchor,
            .packet_bytes = request.packet_bytes,
            .total_bytes = total_bytes,
            .required_buffers = required_buffers,
            .buffer_mode = if (reuses_existing_room)
                .recycled_room
            else if (fits_single_page)
                .single_page
            else
                .mergeable,
            .big_packet_reason = if (fits_single_page) .none else .exceeds_single_buffer,
            .reuses_existing_room = reuses_existing_room,
            .fits_single_page = fits_single_page,
            .uses_mergeable_path = !reuses_existing_room and !fits_single_page,
        };
        self.last_mergeable_plan = plan;
        return plan;
    }

    pub fn freezeForReset(self: *Self) !RecoverySummary {
        if (self.resetting) {
            return error.TransportResetInProgress;
        }

        const probe_snapshot = self.last_probe_snapshot orelse return error.ProbeSnapshotUnavailable;
        const topology = self.last_queue_topology_summary orelse return error.QueueTopologyUnavailable;
        const mergeable_plan = self.last_mergeable_plan;

        self.resetting = true;
        self.frozen_probe_snapshot = probe_snapshot;
        self.frozen_queue_topology_summary = topology;
        self.frozen_mergeable_plan = mergeable_plan;

        return .{
            .anchor = descriptor().anchor,
            .action = .freeze,
            .was_resetting = false,
            .is_resetting = true,
            .remembered_queue_pairs = topology.effective_queue_pairs,
            .remembered_total_queue_count = topology.total_queue_count,
            .remembered_control_queue_count = topology.control_queue_count,
            .receive_buffer_refill_required = mergeable_plan != null,
            .mergeable_buffer_refill_required = if (mergeable_plan) |plan| plan.uses_mergeable_path else false,
            .recovery_generation = self.recovery_generation,
        };
    }

    pub fn recoveryQueuePlan(self: *const Self) !RecoveryQueuePlan {
        if (!self.resetting) {
            return error.TransportNotResetting;
        }

        const topology = self.frozen_queue_topology_summary orelse return error.QueueTopologyUnavailable;
        const mergeable_plan = self.frozen_mergeable_plan;

        return .{
            .anchor = descriptor().anchor,
            .effective_queue_pairs = topology.effective_queue_pairs,
            .receive_queue_count = topology.receive_queue_count,
            .transmit_queue_count = topology.transmit_queue_count,
            .first_receive_queue_index = topology.first_receive_queue_index,
            .first_transmit_queue_index = topology.first_transmit_queue_index,
            .first_control_queue_index = topology.first_control_queue_index,
            .total_queue_count = topology.total_queue_count,
            .rss_enabled = topology.rss_enabled,
            .requires_receive_queue_restore = topology.receive_queue_count > 0,
            .requires_transmit_queue_restore = topology.transmit_queue_count > 0,
            .requires_control_queue_restore = topology.control_queue_count > 0,
            .requires_receive_buffer_refill = mergeable_plan != null,
            .requires_mergeable_buffer_refill = if (mergeable_plan) |plan| plan.uses_mergeable_path else false,
        };
    }

    pub fn restoreAfterReset(self: *Self) !RecoverySummary {
        if (!self.resetting) {
            return error.TransportNotResetting;
        }

        const topology = self.frozen_queue_topology_summary orelse return error.QueueTopologyUnavailable;
        const mergeable_plan = self.frozen_mergeable_plan;

        self.resetting = false;
        self.last_probe_snapshot = null;
        self.last_queue_topology_summary = null;
        self.last_mergeable_plan = null;
        self.frozen_probe_snapshot = null;
        self.frozen_queue_topology_summary = null;
        self.frozen_mergeable_plan = null;
        self.recovery_generation = try checkedAddU16(self.recovery_generation, 1);

        return .{
            .anchor = descriptor().anchor,
            .action = .restore,
            .was_resetting = true,
            .is_resetting = false,
            .remembered_queue_pairs = topology.effective_queue_pairs,
            .remembered_total_queue_count = topology.total_queue_count,
            .remembered_control_queue_count = topology.control_queue_count,
            .receive_buffer_refill_required = mergeable_plan != null,
            .mergeable_buffer_refill_required = if (mergeable_plan) |plan| plan.uses_mergeable_path else false,
            .recovery_generation = self.recovery_generation,
        };
    }

    fn negotiatedQueuePairs(request: ProbeRequest) u16 {
        if (request.device_queue_pairs == 0) return default_queue_pairs;
        if (request.requested_queue_pairs == 0) return default_queue_pairs;
        return @min(request.requested_queue_pairs, request.device_queue_pairs);
    }

    fn queueFallbackReason(request: ProbeRequest) QueueFallbackReason {
        if (request.device_queue_pairs == 0 or request.requested_queue_pairs == 0) {
            return .device_single_queue;
        }
        if (request.requested_queue_pairs > request.device_queue_pairs) {
            return .negotiated_pair_cap;
        }
        return .none;
    }

    fn queueHeaderShape(request: ProbeRequest) HeaderShape {
        if (request.uses_udp_tunnel_headers) return .hash_report_tunnel;
        if (request.uses_hash_report) return .hash_report;
        return .legacy;
    }

    fn checkedAddU16(lhs: u16, rhs: u16) !u16 {
        const value = @as(u32, lhs) + rhs;
        return std.math.cast(u16, value) orelse error.QueueCountOverflow;
    }
};

test "captureProbeSnapshot clamps queue pairs to device capacity" {
    var lab = VirtioNetProbeLab.init();
    const snapshot = lab.captureProbeSnapshot(.{
        .requested_queue_pairs = 8,
        .device_queue_pairs = 4,
        .has_control_vq = true,
        .has_rss = true,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", snapshot.anchor);
    try std.testing.expectEqual(@as(u16, 4), snapshot.effective_queue_pairs);
    try std.testing.expectEqual(QueueFallbackReason.negotiated_pair_cap, snapshot.fallback_reason);
    try std.testing.expect(snapshot.control_vq_present);
    try std.testing.expect(snapshot.rss_enabled);
    try std.testing.expectEqual(HeaderShape.hash_report, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, default_headroom_bytes), snapshot.hdr_len_bytes);
    try std.testing.expectEqual(snapshot, lab.last_probe_snapshot.?);
}

test "summarizeQueueTopology lays out rx tx and control queues for multiqueue" {
    var lab = VirtioNetProbeLab.init();
    const summary = try lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 8,
        .device_queue_pairs = 4,
        .has_control_vq = true,
        .has_rss = true,
    });

    try std.testing.expectEqual(@as(u16, 4), summary.receive_queue_count);
    try std.testing.expectEqual(@as(u16, 4), summary.transmit_queue_count);
    try std.testing.expectEqual(@as(u16, 4), summary.first_transmit_queue_index);
    try std.testing.expectEqual(@as(?u16, 8), summary.first_control_queue_index);
    try std.testing.expectEqual(@as(u16, 9), summary.total_queue_count);
    try std.testing.expect(summary.multi_queue);
    try std.testing.expect(summary.rss_enabled);
    try std.testing.expectEqual(summary, lab.last_queue_topology_summary.?);
}

test "summarizeQueueTopology keeps rss off when fallback collapses to one pair" {
    var lab = VirtioNetProbeLab.init();
    const summary = try lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 4,
        .device_queue_pairs = 0,
        .has_control_vq = false,
        .has_rss = true,
    });

    try std.testing.expectEqual(@as(u16, default_queue_pairs), summary.effective_queue_pairs);
    try std.testing.expectEqual(QueueFallbackReason.device_single_queue, summary.fallback_reason);
    try std.testing.expectEqual(@as(u16, 2), summary.total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), summary.first_control_queue_index);
    try std.testing.expect(!summary.multi_queue);
    try std.testing.expect(!summary.rss_enabled);
}

test "planMergeableReceiveBuffer reuses existing room when available" {
    var lab = VirtioNetProbeLab.init();
    const plan = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 1500,
        .existing_room_bytes = 2048,
    });

    try std.testing.expectEqual(ReceiveBufferMode.recycled_room, plan.buffer_mode);
    try std.testing.expect(plan.reuses_existing_room);
    try std.testing.expect(plan.fits_single_page);
    try std.testing.expectEqual(@as(u16, 1), plan.required_buffers);
    try std.testing.expectEqual(plan, lab.last_mergeable_plan.?);
}

test "planMergeableReceiveBuffer uses mergeable path for multi page packets" {
    var lab = VirtioNetProbeLab.init();
    const plan = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 5000,
        .headroom_bytes = 64,
        .mergeable_rx_bufs = true,
    });

    try std.testing.expectEqual(ReceiveBufferMode.mergeable, plan.buffer_mode);
    try std.testing.expectEqual(BigPacketReason.exceeds_single_buffer, plan.big_packet_reason);
    try std.testing.expectEqual(@as(u32, 5064), plan.total_bytes);
    try std.testing.expectEqual(@as(u16, 2), plan.required_buffers);
    try std.testing.expect(!plan.reuses_existing_room);
    try std.testing.expect(!plan.fits_single_page);
    try std.testing.expect(plan.uses_mergeable_path);
}

test "planMergeableReceiveBuffer rejects big packets without mergeable support" {
    var lab = VirtioNetProbeLab.init();
    try std.testing.expectError(error.MergeableReceiveBuffersRequired, lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 5000,
        .headroom_bytes = 64,
        .mergeable_rx_bufs = false,
    }));
}

test "freezeForReset captures the last queue summary and refill expectations" {
    var lab = VirtioNetProbeLab.init();

    try std.testing.expectError(error.ProbeSnapshotUnavailable, lab.freezeForReset());

    _ = lab.captureProbeSnapshot(.{
        .requested_queue_pairs = 4,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = true,
    });
    try std.testing.expectError(error.QueueTopologyUnavailable, lab.freezeForReset());

    _ = try lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 4,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = true,
    });
    _ = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 6000,
        .headroom_bytes = 64,
        .mergeable_rx_bufs = true,
    });

    const frozen = try lab.freezeForReset();
    try std.testing.expectEqual(RecoveryAction.freeze, frozen.action);
    try std.testing.expect(!frozen.was_resetting);
    try std.testing.expect(frozen.is_resetting);
    try std.testing.expectEqual(@as(u16, 2), frozen.remembered_queue_pairs);
    try std.testing.expectEqual(@as(u16, 5), frozen.remembered_total_queue_count);
    try std.testing.expectEqual(@as(u16, 1), frozen.remembered_control_queue_count);
    try std.testing.expect(frozen.receive_buffer_refill_required);
    try std.testing.expect(frozen.mergeable_buffer_refill_required);
    try std.testing.expectEqual(@as(u16, 0), frozen.recovery_generation);
    try std.testing.expectError(error.TransportResetInProgress, lab.freezeForReset());
}

test "recoveryQueuePlan mirrors the frozen queue summary" {
    var lab = VirtioNetProbeLab.init();
    try std.testing.expectError(error.TransportNotResetting, lab.recoveryQueuePlan());

    _ = lab.captureProbeSnapshot(.{
        .requested_queue_pairs = 4,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = true,
    });
    _ = try lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 4,
        .device_queue_pairs = 2,
        .has_control_vq = true,
        .has_rss = true,
    });
    _ = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 6000,
        .headroom_bytes = 64,
        .mergeable_rx_bufs = true,
    });
    _ = try lab.freezeForReset();

    const plan = try lab.recoveryQueuePlan();
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", plan.anchor);
    try std.testing.expectEqual(@as(u16, 2), plan.effective_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), plan.receive_queue_count);
    try std.testing.expectEqual(@as(u16, 2), plan.transmit_queue_count);
    try std.testing.expectEqual(@as(u16, 0), plan.first_receive_queue_index);
    try std.testing.expectEqual(@as(u16, 2), plan.first_transmit_queue_index);
    try std.testing.expectEqual(@as(?u16, 4), plan.first_control_queue_index);
    try std.testing.expectEqual(@as(u16, 5), plan.total_queue_count);
    try std.testing.expect(plan.rss_enabled);
    try std.testing.expect(plan.requires_receive_queue_restore);
    try std.testing.expect(plan.requires_transmit_queue_restore);
    try std.testing.expect(plan.requires_control_queue_restore);
    try std.testing.expect(plan.requires_receive_buffer_refill);
    try std.testing.expect(plan.requires_mergeable_buffer_refill);
}

test "restoreAfterReset clears remembered queue state and increments generation" {
    var lab = VirtioNetProbeLab.init();
    try std.testing.expectError(error.TransportNotResetting, lab.restoreAfterReset());

    _ = lab.captureProbeSnapshot(.{
        .requested_queue_pairs = 2,
        .device_queue_pairs = 2,
        .has_control_vq = false,
        .has_rss = false,
    });
    _ = try lab.summarizeQueueTopology(.{
        .requested_queue_pairs = 2,
        .device_queue_pairs = 2,
        .has_control_vq = false,
        .has_rss = false,
    });
    _ = try lab.planMergeableReceiveBuffer(.{
        .packet_bytes = 2048,
        .existing_room_bytes = 4096,
        .headroom_bytes = 32,
        .mergeable_rx_bufs = true,
    });
    _ = try lab.freezeForReset();

    const restored = try lab.restoreAfterReset();
    try std.testing.expectEqual(RecoveryAction.restore, restored.action);
    try std.testing.expect(restored.was_resetting);
    try std.testing.expect(!restored.is_resetting);
    try std.testing.expectEqual(@as(u16, 1), restored.recovery_generation);
    try std.testing.expect(restored.receive_buffer_refill_required);
    try std.testing.expect(!restored.mergeable_buffer_refill_required);
    try std.testing.expectError(error.TransportNotResetting, lab.recoveryQueuePlan());
    try std.testing.expectError(error.QueueTopologyUnavailable, lab.restoreAfterReset());
}
