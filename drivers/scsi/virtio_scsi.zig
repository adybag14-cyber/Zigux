const std = @import("std");

pub const control_queue_index: u16 = 0;
pub const event_queue_index: u16 = 1;
pub const request_queue_base: u16 = 2;
pub const event_buffer_count: u16 = 8;
pub const min_request_queues: u16 = 1;
pub const default_cdb_size: u32 = 32;
pub const default_dma_boundary: u32 = std.math.maxInt(u32);
pub const default_cmd_per_lun: u32 = 1;
pub const default_max_sectors: u32 = 0xFFFF;

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
    provides_host_shape_summary: bool,
    touches_live_dma: bool,
    touches_scsi_host: bool,
    touches_transport_reset: bool,
};

pub const QueueLayoutSummary = struct {
    anchor: []const u8,
    request_queues: u16,
    requested_poll_queues: u16,
    default_queues: u16,
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

pub const QueueWindowSummary = struct {
    anchor: []const u8,
    control_queue_index: u16,
    event_queue_index: u16,
    first_default_queue_index: u16,
    last_default_queue_index: u16,
    default_queue_count: u16,
    first_poll_queue_index: ?u16,
    last_poll_queue_index: ?u16,
    poll_queue_count: u16,
    total_queues: u16,
    preserves_control_event_gap: bool,
    keeps_default_queues_before_poll_queues: bool,
};

pub const ProbeConfigSnapshot = struct {
    anchor: []const u8,
    num_queues: u16,
    requested_poll_queues: u16,
    seg_max: u32,
    cmd_per_lun: u32,
    max_target: u32,
    max_lun: u32,
    max_sectors: u32,
    default_queues: u16,
    poll_queues: u16,
    total_queues: u16,
    control_queue_index: u16,
    event_queue_index: u16,
    first_request_queue_index: u16,
    first_poll_queue_index: ?u16,
    event_buffer_count: u16,
    uses_control_queue: bool,
    uses_event_queue: bool,
    respects_poll_queue_clamp: bool,
    preserves_probe_only_scope: bool,
    blocks_dma_submission: bool,
};

pub const HostShapeRequest = struct {
    num_queues: u16,
    requested_poll_queues: u16,
    seg_max: u32,
    cmd_per_lun: u32,
    max_target: u32,
    max_lun: u32,
    max_sectors: u32,
};

pub const HostShapeSummary = struct {
    anchor: []const u8,
    request_queues: u16,
    default_queues: u16,
    poll_queues: u16,
    sg_tablesize: u32,
    cmd_per_lun: u32,
    max_sectors: u32,
    max_id: u32,
    max_lun: u32,
    max_cmd_len: u32,
    nr_hw_queues: u16,
    nr_maps: u16,
    dma_boundary: u32,
    uses_map_queues: bool,
    uses_commit_rqs: bool,
    uses_mq_poll: bool,
    preserves_pre_registration_scope: bool,
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

pub const RecoveryRestoreSummary = struct {
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
    requires_find_vqs: bool,
    find_vqs_before_device_ready: bool,
    device_ready_before_event_rearm: bool,
    preserves_scsi_host_registration: bool,
    reruns_host_scan: bool,
};

pub const RecoveryRestoreQueueRebindSummary = struct {
    anchor: []const u8,
    control_queue_index: u16,
    event_queue_index: u16,
    first_default_queue_index: u16,
    last_default_queue_index: u16,
    default_queue_count: u16,
    first_poll_queue_index: ?u16,
    last_poll_queue_index: ?u16,
    poll_queue_count: u16,
    total_queues: u16,
    recreates_control_and_event_queues: bool,
    recreates_request_queues_before_device_ready: bool,
    defers_event_buffers_until_after_device_ready: bool,
};

pub const RecoveryRequestQueueRestartSummary = struct {
    anchor: []const u8,
    request_queues: u16,
    default_queues: u16,
    poll_queues: u16,
    total_queues: u16,
    event_queue_index: u16,
    first_request_queue_index: u16,
    first_poll_queue_index: ?u16,
    event_buffer_count: u16,
    recovery_generation: u16,
    requires_find_vqs_before_restart: bool,
    requires_device_ready_before_restart: bool,
    requires_event_rearm_before_restart: bool,
    requires_replan_before_restart: bool,
    preserves_default_before_poll_partition: bool,
};

pub const RecoveryRequestQueueOwnershipSummary = struct {
    anchor: []const u8,
    request_queues: u16,
    default_queues: u16,
    poll_queues: u16,
    total_queues: u16,
    event_queue_index: u16,
    first_request_queue_index: u16,
    first_poll_queue_index: ?u16,
    event_buffer_count: u16,
    recovery_generation: u16,
    request_queue_access_stays_blocked_until_restore: bool,
    request_queue_access_requires_replan_after_restore: bool,
    poll_queues_resume_only_after_default_queues: bool,
    event_rearm_completes_before_request_queue_reuse: bool,
};

pub const RecoveryEventBufferOwnershipSummary = struct {
    anchor: []const u8,
    event_queue_index: u16,
    request_queues: u16,
    default_queues: u16,
    poll_queues: u16,
    event_buffer_count: u16,
    event_queue_reserved_during_freeze: bool,
    event_buffers_stay_on_event_queue: bool,
    request_queues_cannot_borrow_event_buffers: bool,
    defers_event_buffers_until_after_device_ready: bool,
    requires_restore_rearm_before_reuse: bool,
};

pub const RecoveryEventRearmSummary = struct {
    anchor: []const u8,
    event_queue_index: u16,
    request_queues: u16,
    default_queues: u16,
    poll_queues: u16,
    event_buffer_count: u16,
    reuses_frozen_event_queue_index: bool,
    requires_device_ready_before_rearm: bool,
    rearms_event_queue_before_event_recycling: bool,
    rearms_event_queue_before_request_queue_reuse: bool,
};

pub const RecoveryRollbackSummary = struct {
    anchor: []const u8,
    request_queues: u16,
    default_queues: u16,
    poll_queues: u16,
    total_queues: u16,
    event_buffer_count: u16,
    recovery_generation: u16,
    blocks_queue_planning_until_restore: bool,
    blocks_request_queue_access_until_restore: bool,
    keeps_frozen_layout_for_restore: bool,
    clears_live_layout_after_restore: bool,
    requires_replan_before_queue_reuse: bool,
};

pub const VirtioScsiQueueLab = struct {
    const Self = @This();

    last_layout: ?QueueLayoutSummary = null,
    frozen_layout: ?QueueLayoutSummary = null,
    transport_frozen: bool = false,
    recovery_generation: u16 = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_scsi_queue_lab",
            .anchor = "drivers/scsi/virtio_scsi.c",
            .provides_queue_family_planner = true,
            .provides_host_shape_summary = true,
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

    pub fn probeConfigSnapshot(
        self: *Self,
        num_queues: u16,
        requested_poll_queues: u16,
        seg_max: u32,
        cmd_per_lun: u32,
        max_target: u32,
        max_lun: u32,
        max_sectors: u32,
    ) !ProbeConfigSnapshot {
        const layout = try self.planQueueLayout(num_queues, requested_poll_queues);
        return .{
            .anchor = descriptor().anchor,
            .num_queues = num_queues,
            .requested_poll_queues = requested_poll_queues,
            .seg_max = seg_max,
            .cmd_per_lun = cmd_per_lun,
            .max_target = max_target,
            .max_lun = max_lun,
            .max_sectors = max_sectors,
            .default_queues = layout.default_queues,
            .poll_queues = layout.poll_queues,
            .total_queues = layout.total_queues,
            .control_queue_index = layout.control_queue_index,
            .event_queue_index = layout.event_queue_index,
            .first_request_queue_index = layout.first_request_queue_index,
            .first_poll_queue_index = layout.first_poll_queue_index,
            .event_buffer_count = layout.event_buffer_count,
            .uses_control_queue = true,
            .uses_event_queue = true,
            .respects_poll_queue_clamp = layout.poll_queues <= layout.request_queues - 1,
            .preserves_probe_only_scope = true,
            .blocks_dma_submission = true,
        };
    }

    pub fn captureHostShapeSummary(self: *Self, request: HostShapeRequest) !HostShapeSummary {
        const probe = try self.probeConfigSnapshot(
            request.num_queues,
            request.requested_poll_queues,
            request.seg_max,
            request.cmd_per_lun,
            request.max_target,
            request.max_lun,
            request.max_sectors,
        );
        const nr_maps: u16 = if (probe.poll_queues == 0) 1 else 3;

        return .{
            .anchor = descriptor().anchor,
            .request_queues = probe.num_queues,
            .default_queues = probe.default_queues,
            .poll_queues = probe.poll_queues,
            .sg_tablesize = defaultIfZeroU32(request.seg_max, 1),
            .cmd_per_lun = defaultIfZeroU32(request.cmd_per_lun, default_cmd_per_lun),
            .max_sectors = defaultIfZeroU32(request.max_sectors, default_max_sectors),
            .max_id = try checkedAddU32(request.max_target, 1),
            .max_lun = try checkedAddU32(request.max_lun, 0x4001),
            .max_cmd_len = default_cdb_size,
            .nr_hw_queues = probe.num_queues,
            .nr_maps = nr_maps,
            .dma_boundary = default_dma_boundary,
            .uses_map_queues = true,
            .uses_commit_rqs = true,
            .uses_mq_poll = probe.poll_queues != 0,
            .preserves_pre_registration_scope = true,
        };
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

    pub fn queueWindowSummary(self: *const Self) !QueueWindowSummary {
        if (self.transport_frozen) {
            return error.TransportFrozen;
        }

        const layout = self.last_layout orelse return error.QueueLayoutUnavailable;
        const last_default_queue_index = try checkedAddU16(
            layout.first_request_queue_index,
            layout.default_queues - 1,
        );
        const last_poll_queue_index = if (layout.first_poll_queue_index) |first_poll_queue_index|
            try checkedAddU16(first_poll_queue_index, layout.poll_queues - 1)
        else
            null;

        return .{
            .anchor = descriptor().anchor,
            .control_queue_index = layout.control_queue_index,
            .event_queue_index = layout.event_queue_index,
            .first_default_queue_index = layout.first_request_queue_index,
            .last_default_queue_index = last_default_queue_index,
            .default_queue_count = layout.default_queues,
            .first_poll_queue_index = layout.first_poll_queue_index,
            .last_poll_queue_index = last_poll_queue_index,
            .poll_queue_count = layout.poll_queues,
            .total_queues = layout.total_queues,
            .preserves_control_event_gap = layout.first_request_queue_index == request_queue_base,
            .keeps_default_queues_before_poll_queues = if (layout.first_poll_queue_index) |first_poll_queue_index|
                last_default_queue_index < first_poll_queue_index
            else
                true,
        };
    }

    pub fn freezeForTransportReset(self: *Self) !RecoverySummary {
        if (self.transport_frozen) {
            return error.TransportAlreadyFrozen;
        }

        const layout = self.last_layout orelse return error.QueueLayoutUnavailable;
        self.transport_frozen = true;
        self.frozen_layout = layout;

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

    pub fn recoveryRestoreSummary(self: *const Self) !RecoveryRestoreSummary {
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
            .requires_find_vqs = true,
            .find_vqs_before_device_ready = true,
            .device_ready_before_event_rearm = true,
            .preserves_scsi_host_registration = true,
            .reruns_host_scan = false,
        };
    }

    pub fn recoveryRestoreQueueRebindSummary(self: *const Self) !RecoveryRestoreQueueRebindSummary {
        if (!self.transport_frozen) {
            return error.TransportNotFrozen;
        }

        const layout = self.frozen_layout orelse return error.QueueLayoutUnavailable;
        const last_default_queue_index = try checkedAddU16(
            layout.first_request_queue_index,
            layout.default_queues - 1,
        );
        const last_poll_queue_index = if (layout.first_poll_queue_index) |first_poll_queue_index|
            try checkedAddU16(first_poll_queue_index, layout.poll_queues - 1)
        else
            null;

        return .{
            .anchor = descriptor().anchor,
            .control_queue_index = layout.control_queue_index,
            .event_queue_index = layout.event_queue_index,
            .first_default_queue_index = layout.first_request_queue_index,
            .last_default_queue_index = last_default_queue_index,
            .default_queue_count = layout.default_queues,
            .first_poll_queue_index = layout.first_poll_queue_index,
            .last_poll_queue_index = last_poll_queue_index,
            .poll_queue_count = layout.poll_queues,
            .total_queues = layout.total_queues,
            .recreates_control_and_event_queues = true,
            .recreates_request_queues_before_device_ready = true,
            .defers_event_buffers_until_after_device_ready = true,
        };
    }

    pub fn recoveryRequestQueueRestartSummary(self: *const Self) !RecoveryRequestQueueRestartSummary {
        if (!self.transport_frozen) {
            return error.TransportNotFrozen;
        }

        const layout = self.frozen_layout orelse return error.QueueLayoutUnavailable;
        const preserves_default_before_poll_partition = if (layout.first_poll_queue_index) |first_poll_queue_index|
            try checkedAddU16(layout.first_request_queue_index, layout.default_queues - 1) < first_poll_queue_index
        else
            true;

        return .{
            .anchor = descriptor().anchor,
            .request_queues = layout.request_queues,
            .default_queues = layout.default_queues,
            .poll_queues = layout.poll_queues,
            .total_queues = layout.total_queues,
            .event_queue_index = layout.event_queue_index,
            .first_request_queue_index = layout.first_request_queue_index,
            .first_poll_queue_index = layout.first_poll_queue_index,
            .event_buffer_count = layout.event_buffer_count,
            .recovery_generation = self.recovery_generation,
            .requires_find_vqs_before_restart = true,
            .requires_device_ready_before_restart = true,
            .requires_event_rearm_before_restart = true,
            .requires_replan_before_restart = true,
            .preserves_default_before_poll_partition = preserves_default_before_poll_partition,
        };
    }

    pub fn recoveryRequestQueueOwnershipSummary(self: *const Self) !RecoveryRequestQueueOwnershipSummary {
        if (!self.transport_frozen) {
            return error.TransportNotFrozen;
        }

        const layout = self.frozen_layout orelse return error.QueueLayoutUnavailable;
        const poll_queues_resume_only_after_default_queues = if (layout.first_poll_queue_index) |first_poll_queue_index|
            try checkedAddU16(layout.first_request_queue_index, layout.default_queues - 1) < first_poll_queue_index
        else
            true;

        return .{
            .anchor = descriptor().anchor,
            .request_queues = layout.request_queues,
            .default_queues = layout.default_queues,
            .poll_queues = layout.poll_queues,
            .total_queues = layout.total_queues,
            .event_queue_index = layout.event_queue_index,
            .first_request_queue_index = layout.first_request_queue_index,
            .first_poll_queue_index = layout.first_poll_queue_index,
            .event_buffer_count = layout.event_buffer_count,
            .recovery_generation = self.recovery_generation,
            .request_queue_access_stays_blocked_until_restore = true,
            .request_queue_access_requires_replan_after_restore = true,
            .poll_queues_resume_only_after_default_queues = poll_queues_resume_only_after_default_queues,
            .event_rearm_completes_before_request_queue_reuse = true,
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
            .request_queues = layout.request_queues,
            .default_queues = layout.default_queues,
            .poll_queues = layout.poll_queues,
            .event_buffer_count = layout.event_buffer_count,
            .event_queue_reserved_during_freeze = true,
            .event_buffers_stay_on_event_queue = true,
            .request_queues_cannot_borrow_event_buffers = true,
            .defers_event_buffers_until_after_device_ready = true,
            .requires_restore_rearm_before_reuse = true,
        };
    }

    pub fn recoveryEventRearmSummary(self: *const Self) !RecoveryEventRearmSummary {
        if (!self.transport_frozen) {
            return error.TransportNotFrozen;
        }

        const layout = self.frozen_layout orelse return error.QueueLayoutUnavailable;
        return .{
            .anchor = descriptor().anchor,
            .event_queue_index = layout.event_queue_index,
            .request_queues = layout.request_queues,
            .default_queues = layout.default_queues,
            .poll_queues = layout.poll_queues,
            .event_buffer_count = layout.event_buffer_count,
            .reuses_frozen_event_queue_index = true,
            .requires_device_ready_before_rearm = true,
            .rearms_event_queue_before_event_recycling = true,
            .rearms_event_queue_before_request_queue_reuse = true,
        };
    }

    pub fn recoveryRollbackSummary(self: *const Self) !RecoveryRollbackSummary {
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
            .event_buffer_count = layout.event_buffer_count,
            .recovery_generation = self.recovery_generation,
            .blocks_queue_planning_until_restore = true,
            .blocks_request_queue_access_until_restore = true,
            .keeps_frozen_layout_for_restore = true,
            .clears_live_layout_after_restore = true,
            .requires_replan_before_queue_reuse = true,
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

    fn defaultIfZeroU32(value: u32, fallback: u32) u32 {
        return if (value == 0) fallback else value;
    }
};