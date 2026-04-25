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

pub const VirtioScsiQueueLab = struct {
    const Self = @This();

    last_layout: ?QueueLayoutSummary = null,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_scsi_queue_lab",
            .anchor = "drivers/scsi/virtio_scsi.c",
            .provides_queue_family_planner = true,
            .touches_live_dma = false,
            .touches_scsi_host = false,
            .touches_transport_reset = false,
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

    fn checkedAddU16(lhs: u16, rhs: u16) !u16 {
        const value = @as(u32, lhs) + rhs;
        return std.math.cast(u16, value) orelse error.QueueCountOverflow;
    }
};