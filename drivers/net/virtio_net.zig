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

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_probe_snapshot: bool,
    provides_mergeable_receive_buffer_planner: bool,
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

pub const VirtioNetProbeLab = struct {
    const Self = @This();

    last_probe_snapshot: ?ProbeSnapshot = null,
    last_mergeable_plan: ?MergeableReceiveBufferPlan = null,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_net_probe_lab",
            .anchor = "drivers/net/virtio_net.c",
            .provides_probe_snapshot = true,
            .provides_mergeable_receive_buffer_planner = true,
            .touches_live_dma = false,
            .touches_net_device = false,
            .touches_control_virtqueue_runtime = false,
        };
    }

    pub fn init() Self {
        return .{};
    }

    pub fn captureProbeSnapshot(self: *Self, request: ProbeRequest) ProbeSnapshot {
        const effective_queue_pairs = blk: {
            if (request.device_queue_pairs == 0) break :blk default_queue_pairs;
            if (request.requested_queue_pairs == 0) break :blk default_queue_pairs;
            break :blk @min(request.requested_queue_pairs, request.device_queue_pairs);
        };

        const fallback_reason: QueueFallbackReason = if (request.device_queue_pairs == 0 or request.requested_queue_pairs == 0)
            .device_single_queue
        else if (request.requested_queue_pairs > request.device_queue_pairs)
            .negotiated_pair_cap
        else
            .none;

        const header_shape: HeaderShape = if (request.uses_udp_tunnel_headers)
            .hash_report_tunnel
        else if (request.uses_hash_report)
            .hash_report
        else
            .legacy;

        const snapshot = ProbeSnapshot{
            .anchor = descriptor().anchor,
            .requested_queue_pairs = request.requested_queue_pairs,
            .device_queue_pairs = request.device_queue_pairs,
            .effective_queue_pairs = effective_queue_pairs,
            .fallback_reason = fallback_reason,
            .control_vq_present = request.has_control_vq,
            .rss_enabled = request.has_rss,
            .header_shape = header_shape,
            .hdr_len_bytes = if (request.uses_udp_tunnel_headers) tunnel_header_len_bytes else default_headroom_bytes,
        };
        self.last_probe_snapshot = snapshot;
        return snapshot;
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
};
