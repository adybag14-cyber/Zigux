const std = @import("std");

pub const control_queue_index: u16 = 0;
pub const event_queue_index: u16 = 1;
pub const request_queue_base: u16 = 2;
pub const event_buffer_count: u16 = 8;
pub const min_request_queues: u16 = 1;
pub const default_seg_max: u32 = 1;
pub const default_cmd_per_lun: u32 = 1;
pub const default_max_sectors: u32 = 0xFFFF;
pub const max_lun_format_one_bias: u32 = 0x4001;

pub const RequestQueueKind = enum {
    request,
    request_poll,
};

pub const RecoveryAction = enum {
    freeze,
    restore,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_queue_family_planner: bool,
    provides_probe_config_snapshot: bool,
    provides_host_limit_summary: bool,
    provides_queue_depth_summary: bool,
    touches_live_dma: bool,
    touches_scsi_host: bool,
    touches_transport_reset: bool,
};

pub const QueueLayoutSummary = struct {
    anchor: []const u8,
    request_queues: u16,
    requested_poll_queues: u16,
    default_queues: u16,
    read_queues: u16,
    poll_queues: u16,
    total_queues: u16,
    control_queue_index: u16,
    event_queue_index: u16,
    first_request_queue_index: u16,
    first_poll_queue_index: ?u16,
    event_buffer_count: u16,
};

pub const RequestQueueSummary = struct {
    anchor: []const u8,
    local_index: u16,
    global_index: u16,
    kind: RequestQueueKind,
};

pub const RecoverySummary = struct {
    anchor: []const u8,
    action: RecoveryAction,
    was_frozen: bool,
    is_frozen: bool,
    request_planning_available: bool,
    event_recycling_enabled: bool,
    remembered_request_queues: u16,
    remembered_poll_queues: u16,
    remembered_event_buffer_count: u16,
    recovery_generation: u16,
};

pub const RecoveryQueuePlan = struct {
    anchor: []const u8,
    request_queues: u16,
    default_queues: u16,
    poll_queues: u16,
    total_queues: u16,
    control_queue_index: u16,
    event_queue_index: u16,
    first_request_queue_index: u16,
    first_poll_queue_index: ?u16,
    event_buffer_count: u16,
    requires_control_queue_restore: bool,
    requires_event_queue_refill: bool,
    requires_request_queue_restore: bool,
};

pub const RecoveryIoQueueMapSummary = struct {
    anchor: []const u8,
    nr_maps: u16,
    default_queue_count: u16,
    read_queue_count: u16,
    poll_queue_count: u16,
    default_queue_offset: u16,
    read_queue_offset: u16,
    poll_queue_offset: u16,
    requires_blk_mq_map_restore: bool,
    requires_virtio_affinity_restore: bool,
    requires_poll_map_restore: bool,
};

pub const RecoveryEventBufferOwnershipSummary = struct {
    anchor: []const u8,
    event_queue_index: u16,
    remembered_event_buffer_count: u16,
    request_queue_count: u16,
    poll_queue_count: u16,
    event_buffers_reserved_for_event_queue: bool,
    request_queues_can_borrow_event_buffers: bool,
    requires_device_ready_before_event_rearm: bool,
    requires_event_rearm_before_request_queue_reuse: bool,
};

pub const ProbeRequest = struct {
    num_queues: u16,
    requested_poll_queues: u16 = 0,
    seg_max: u32 = 0,
    cmd_per_lun: u32 = 0,
    max_target: u32 = 0,
    max_lun: u32 = 0,
    max_sectors: u32 = 0,
};

pub const ProbeSnapshot = struct {
    anchor: []const u8,
    config_num_queues: u16,
    config_seg_max: u32,
    config_cmd_per_lun: u32,
    config_max_target: u32,
    config_max_lun: u32,
    config_max_sectors: u32,
    effective_seg_max: u32,
    effective_cmd_per_lun: u32,
    effective_max_target_count: u32,
    effective_max_lun: u32,
    effective_max_sectors: u32,
    control_queue_count: u16,
    event_queue_count: u16,
    request_queue_count: u16,
    default_queue_count: u16,
    poll_queue_count: u16,
    total_queue_count: u16,
    first_request_queue_index: u16,
    first_poll_queue_index: ?u16,
};

pub const HostLimitRequest = struct {
    probe: ProbeRequest,
    synthetic_can_queue: u32 = 0,
};

pub const HostLimitSummary = struct {
    anchor: []const u8,
    config_cmd_per_lun: u32,
    config_can_queue: u32,
    effective_can_queue: u32,
    effective_cmd_per_lun: u32,
    max_target: u32,
    max_lun: u32,
    max_sectors: u32,
    nr_hw_queues: u16,
};

pub const QueueDepthRequest = struct {
    host_limit: HostLimitRequest,
    requested_depth: u32,
};

pub const QueueDepthSummary = struct {
    anchor: []const u8,
    requested_depth: u32,
    effective_can_queue: u32,
    effective_cmd_per_lun: u32,
    clamped_queue_depth: u32,
    tracks_queue_depth: bool,
    uses_change_queue_depth: bool,
};

pub const RecoveryQueueDepthSummary = struct {
    anchor: []const u8,
    requested_depth: u32,
    effective_can_queue: u32,
    effective_cmd_per_lun: u32,
    clamped_queue_depth: u32,
    tracks_queue_depth: bool,
    requires_change_queue_depth_restore: bool,
};

pub const IoQueueMapSummary = struct {
    anchor: []const u8,
    nr_maps: u16,
    default_queue_count: u16,
    read_queue_count: u16,
    poll_queue_count: u16,
    default_queue_offset: u16,
    read_queue_offset: u16,
    poll_queue_offset: u16,
    default_queues_use_virtio_affinity: bool,
    poll_queues_use_blk_mq_mapping: bool,
};

pub const VirtioScsiQueueLab = struct {
    const Self = @This();

    last_layout: ?QueueLayoutSummary = null,
    last_probe_snapshot: ?ProbeSnapshot = null,
    last_host_limit_summary: ?HostLimitSummary = null,
    last_queue_depth_summary: ?QueueDepthSummary = null,
    last_io_queue_map_summary: ?IoQueueMapSummary = null,
    frozen_layout: ?QueueLayoutSummary = null,
    frozen_queue_depth_summary: ?QueueDepthSummary = null,
    transport_frozen: bool = false,
    recovery_generation: u16 = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_scsi_queue_lab",
            .anchor = "drivers/scsi/virtio_scsi.c",
            .provides_queue_family_planner = true,
            .provides_probe_config_snapshot = true,
            .provides_host_limit_summary = true,
            .provides_queue_depth_summary = true,
            .touches_live_dma = false,
            .touches_scsi_host = false,
            .touches_transport_reset = true,
        };
    }

    pub fn init() Self {
        return .{};
    }

    pub fn planQueueLayout(
        self: *Self,
        request_queues: u16,
        requested_poll_queues: u16,
    ) !QueueLayoutSummary {
        if (self.transport_frozen) {
            return error.TransportFrozen;
        }
        if (request_queues < min_request_queues) {
            return error.InvalidRequestQueueCount;
        }

        const max_poll_queues = request_queues - 1;
        const poll_queues = @min(requested_poll_queues, max_poll_queues);
        const default_queues = request_queues - poll_queues;
        const total_queues = try checkedAddU16(request_queues, request_queue_base);
        const first_poll_queue_index = if (poll_queues == 0)
            null
        else
            try checkedAddU16(request_queue_base, default_queues);

        const summary = QueueLayoutSummary{
            .anchor = descriptor().anchor,
            .request_queues = request_queues,
            .requested_poll_queues = requested_poll_queues,
            .default_queues = default_queues,
            .read_queues = 0,
            .poll_queues = poll_queues,
            .total_queues = total_queues,
            .control_queue_index = control_queue_index,
            .event_queue_index = event_queue_index,
            .first_request_queue_index = request_queue_base,
            .first_poll_queue_index = first_poll_queue_index,
            .event_buffer_count = event_buffer_count,
        };
        self.last_layout = summary;
        return summary;
    }

    pub fn requestQueue(self: *const Self, local_index: u16) !RequestQueueSummary {
        if (self.transport_frozen) {
            return error.TransportFrozen;
        }

        const layout = self.last_layout orelse return error.QueueLayoutUnavailable;
        if (local_index >= layout.request_queues) {
            return error.RequestQueueIndexOutOfRange;
        }

        return .{
            .anchor = descriptor().anchor,
            .local_index = local_index,
            .global_index = try checkedAddU16(request_queue_base, local_index),
            .kind = if (local_index < layout.default_queues) .request else .request_poll,
        };
    }

    pub fn captureProbeSnapshot(self: *Self, request: ProbeRequest) !ProbeSnapshot {
        const layout = try self.planQueueLayout(request.num_queues, request.requested_poll_queues);

        const snapshot = ProbeSnapshot{
            .anchor = descriptor().anchor,
            .config_num_queues = request.num_queues,
            .config_seg_max = request.seg_max,
            .config_cmd_per_lun = request.cmd_per_lun,
            .config_max_target = request.max_target,
            .config_max_lun = request.max_lun,
            .config_max_sectors = request.max_sectors,
            .effective_seg_max = if (request.seg_max == 0) default_seg_max else request.seg_max,
            .effective_cmd_per_lun = if (request.cmd_per_lun == 0) default_cmd_per_lun else request.cmd_per_lun,
            .effective_max_target_count = try checkedAddU32(request.max_target, 1),
            .effective_max_lun = try checkedAddU32(request.max_lun, max_lun_format_one_bias),
            .effective_max_sectors = if (request.max_sectors == 0) default_max_sectors else request.max_sectors,
            .control_queue_count = 1,
            .event_queue_count = 1,
            .request_queue_count = layout.request_queues,
            .default_queue_count = layout.default_queues,
            .poll_queue_count = layout.poll_queues,
            .total_queue_count = layout.total_queues,
            .first_request_queue_index = layout.first_request_queue_index,
            .first_poll_queue_index = layout.first_poll_queue_index,
        };
        self.last_probe_snapshot = snapshot;
        return snapshot;
    }

    pub fn captureHostLimitSummary(self: *Self, request: HostLimitRequest) !HostLimitSummary {
        const snapshot = try self.captureProbeSnapshot(request.probe);
        const effective_can_queue = if (request.synthetic_can_queue == 0)
            @as(u32, snapshot.request_queue_count)
        else
            request.synthetic_can_queue;

        const summary = HostLimitSummary{
            .anchor = descriptor().anchor,
            .config_cmd_per_lun = snapshot.config_cmd_per_lun,
            .config_can_queue = request.synthetic_can_queue,
            .effective_can_queue = effective_can_queue,
            .effective_cmd_per_lun = @min(snapshot.effective_cmd_per_lun, effective_can_queue),
            .max_target = snapshot.effective_max_target_count,
            .max_lun = snapshot.effective_max_lun,
            .max_sectors = snapshot.effective_max_sectors,
            .nr_hw_queues = snapshot.request_queue_count,
        };
        self.last_host_limit_summary = summary;
        return summary;
    }

    pub fn captureQueueDepthSummary(self: *Self, request: QueueDepthRequest) !QueueDepthSummary {
        const host_limit = try self.captureHostLimitSummary(request.host_limit);

        const summary = QueueDepthSummary{
            .anchor = descriptor().anchor,
            .requested_depth = request.requested_depth,
            .effective_can_queue = host_limit.effective_can_queue,
            .effective_cmd_per_lun = host_limit.effective_cmd_per_lun,
            .clamped_queue_depth = @min(request.requested_depth, host_limit.effective_cmd_per_lun),
            .tracks_queue_depth = true,
            .uses_change_queue_depth = true,
        };
        self.last_queue_depth_summary = summary;
        return summary;
    }

    pub fn captureIoQueueMapSummary(
        self: *Self,
        request_queues: u16,
        requested_poll_queues: u16,
    ) !IoQueueMapSummary {
        const layout = try self.planQueueLayout(request_queues, requested_poll_queues);
        const default_queue_offset: u16 = 0;
        const read_queue_offset = layout.default_queues;
        const poll_queue_offset = layout.default_queues;

        const summary = IoQueueMapSummary{
            .anchor = descriptor().anchor,
            .nr_maps = if (layout.poll_queues == 0) 1 else 3,
            .default_queue_count = layout.default_queues,
            .read_queue_count = layout.read_queues,
            .poll_queue_count = layout.poll_queues,
            .default_queue_offset = default_queue_offset,
            .read_queue_offset = read_queue_offset,
            .poll_queue_offset = poll_queue_offset,
            .default_queues_use_virtio_affinity = layout.default_queues > 0,
            .poll_queues_use_blk_mq_mapping = layout.poll_queues > 0,
        };
        self.last_io_queue_map_summary = summary;
        return summary;
    }

    pub fn freezeForTransportReset(self: *Self) !RecoverySummary {
        if (self.transport_frozen) {
            return error.TransportAlreadyFrozen;
        }

        const layout = self.last_layout orelse return error.QueueLayoutUnavailable;
        self.transport_frozen = true;
        self.frozen_layout = layout;
        self.frozen_queue_depth_summary = self.last_queue_depth_summary;

        return .{
            .anchor = descriptor().anchor,
            .action = .freeze,
            .was_frozen = false,
            .is_frozen = true,
            .request_planning_available = false,
            .event_recycling_enabled = false,
            .remembered_request_queues = layout.request_queues,
            .remembered_poll_queues = layout.poll_queues,
            .remembered_event_buffer_count = layout.event_buffer_count,
            .recovery_generation = self.recovery_generation,
        };
    }

    pub fn recoveryQueuePlan(self: *const Self) !RecoveryQueuePlan {
        if (!self.transport_frozen) {
            return error.TransportNotFrozen;
        }

        const layout = self.frozen_layout orelse return error.QueueLayoutUnavailable;
        return .{
            .anchor = descriptor().anchor,
            .request_queues = layout.request_queues,
            .default_queues = layout.default_queues,
            .poll_queues = layout.poll_queues,
            .total_queues = layout.total_queues,
            .control_queue_index = layout.control_queue_index,
            .event_queue_index = layout.event_queue_index,
            .first_request_queue_index = layout.first_request_queue_index,
            .first_poll_queue_index = layout.first_poll_queue_index,
            .event_buffer_count = layout.event_buffer_count,
            .requires_control_queue_restore = true,
            .requires_event_queue_refill = true,
            .requires_request_queue_restore = true,
        };
    }

    pub fn recoveryQueueDepthSummary(self: *const Self) !RecoveryQueueDepthSummary {
        if (!self.transport_frozen) {
            return error.TransportNotFrozen;
        }

        const summary = self.frozen_queue_depth_summary orelse return error.QueueDepthSummaryUnavailable;
        return .{
            .anchor = descriptor().anchor,
            .requested_depth = summary.requested_depth,
            .effective_can_queue = summary.effective_can_queue,
            .effective_cmd_per_lun = summary.effective_cmd_per_lun,
            .clamped_queue_depth = summary.clamped_queue_depth,
            .tracks_queue_depth = summary.tracks_queue_depth,
            .requires_change_queue_depth_restore = summary.uses_change_queue_depth,
        };
    }

    pub fn recoveryIoQueueMapSummary(self: *const Self) !RecoveryIoQueueMapSummary {
        if (!self.transport_frozen) {
            return error.TransportNotFrozen;
        }

        const layout = self.frozen_layout orelse return error.QueueLayoutUnavailable;
        const default_queue_offset: u16 = 0;
        const read_queue_offset = layout.default_queues;
        const poll_queue_offset = layout.default_queues;

        return .{
            .anchor = descriptor().anchor,
            .nr_maps = if (layout.poll_queues == 0) 1 else 3,
            .default_queue_count = layout.default_queues,
            .read_queue_count = layout.read_queues,
            .poll_queue_count = layout.poll_queues,
            .default_queue_offset = default_queue_offset,
            .read_queue_offset = read_queue_offset,
            .poll_queue_offset = poll_queue_offset,
            .requires_blk_mq_map_restore = true,
            .requires_virtio_affinity_restore = layout.default_queues > 0,
            .requires_poll_map_restore = layout.poll_queues > 0,
        };
    }

    pub fn recoveryEventBufferOwnershipSummary(self: *const Self) !RecoveryEventBufferOwnershipSummary {
        if (!self.transport_frozen) {
            return error.TransportNotFrozen;
        }

        const layout = self.frozen_layout orelse return error.QueueLayoutUnavailable;
        return .{
            .anchor = descriptor().anchor,
            .event_queue_index = layout.event_queue_index,
            .remembered_event_buffer_count = layout.event_buffer_count,
            .request_queue_count = layout.request_queues,
            .poll_queue_count = layout.poll_queues,
            .event_buffers_reserved_for_event_queue = true,
            .request_queues_can_borrow_event_buffers = false,
            .requires_device_ready_before_event_rearm = true,
            .requires_event_rearm_before_request_queue_reuse = true,
        };
    }

    pub fn restoreAfterTransportReset(self: *Self) !RecoverySummary {
        if (!self.transport_frozen) {
            return error.TransportNotFrozen;
        }

        const layout = self.frozen_layout orelse return error.QueueLayoutUnavailable;
        self.transport_frozen = false;
        self.frozen_layout = null;
        self.last_layout = null;
        self.last_probe_snapshot = null;
        self.last_host_limit_summary = null;
        self.last_queue_depth_summary = null;
        self.last_io_queue_map_summary = null;
        self.frozen_queue_depth_summary = null;
        self.recovery_generation = try checkedAddU16(self.recovery_generation, 1);

        return .{
            .anchor = descriptor().anchor,
            .action = .restore,
            .was_frozen = true,
            .is_frozen = false,
            .request_planning_available = true,
            .event_recycling_enabled = true,
            .remembered_request_queues = layout.request_queues,
            .remembered_poll_queues = layout.poll_queues,
            .remembered_event_buffer_count = layout.event_buffer_count,
            .recovery_generation = self.recovery_generation,
        };
    }

    fn checkedAddU16(lhs: u16, rhs: u16) !u16 {
        const value = @as(u32, lhs) + rhs;
        return std.math.cast(u16, value) orelse error.QueueCountOverflow;
    }

    fn checkedAddU32(lhs: u32, rhs: u32) !u32 {
        const value = @as(u64, lhs) + rhs;
        return std.math.cast(u32, value) orelse error.QueueCountOverflow;
    }
};