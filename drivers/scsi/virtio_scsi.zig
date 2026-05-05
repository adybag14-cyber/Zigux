const std = @import("std");

pub const control_queue_index: u16 = 0;
pub const event_queue_index: u16 = 1;
pub const request_queue_base: u16 = 2;
pub const event_buffer_count: u16 = 8;
pub const min_request_queues: u16 = 1;

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
};