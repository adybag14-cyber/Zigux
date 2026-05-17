const std = @import("std");

pub const anchor_path = "drivers/virtio/virtio.c";

pub const status_acknowledge: u8 = 0x01;
pub const status_driver: u8 = 0x02;
pub const status_driver_ok: u8 = 0x04;
pub const status_features_ok: u8 = 0x08;
pub const status_device_needs_reset: u8 = 0x40;
pub const status_failed: u8 = 0x80;

pub const DeviceStatusSummary = struct {
    anchor: []const u8,
    device_present: bool,
    queue_count: u16,
    status: u8,
    config_generation: u8,
    features_negotiated: bool,
    driver_ready: bool,
    needs_reset: bool,
    failed: bool,
    selected_queue: ?u16,
};

pub const QueueBookkeepingSummary = struct {
    anchor: []const u8,
    queue_count: u16,
    selected_queue: ?u16,
    selected_queue_valid: bool,
    config_generation: u8,
    queue_bookkeeping_ready: bool,
};

pub const InterruptAckSummary = struct {
    anchor: []const u8,
    pending_before: u8,
    ack_mask: u8,
    cleared_bits: u8,
    pending_after: u8,
    all_acknowledged: bool,
};

pub const VirtioCoreLab = struct {
    const Self = @This();

    device_id: u32,
    queue_count: u16,
    selected_queue: ?u16 = null,
    config_generation: u8 = 0,
    status: u8 = 0,
    features_negotiated: bool = false,
    pending_interrupts: u8 = 0,

    pub fn init(device_id: u32, queue_count: u16) !Self {
        if (device_id == 0) return error.DeviceAbsent;
        if (queue_count == 0) return error.EmptyQueueSet;
        return .{
            .device_id = device_id,
            .queue_count = queue_count,
        };
    }

    pub fn setStatusBits(self: *Self, bits: u8) void {
        self.status |= bits;
        if ((bits & status_features_ok) != 0) {
            self.features_negotiated = true;
        }
    }

    pub fn clearStatusBits(self: *Self, bits: u8) void {
        self.status &= ~bits;
        if ((bits & status_features_ok) != 0) {
            self.features_negotiated = false;
        }
    }

    pub fn noteFeaturesNegotiated(self: *Self) void {
        self.features_negotiated = true;
        self.status |= status_features_ok;
    }

    pub fn selectQueue(self: *Self, queue_index: u16) !QueueBookkeepingSummary {
        if (queue_index >= self.queue_count) return error.QueueSelectionOutOfRange;
        self.selected_queue = queue_index;
        return self.queueBookkeepingSummary();
    }

    pub fn bumpConfigGeneration(self: *Self) void {
        self.config_generation +%= 1;
    }

    pub fn stageInterrupt(self: *Self, pending_bits: u8) void {
        self.pending_interrupts |= pending_bits;
    }

    pub fn ackInterrupt(self: *Self, ack_mask: u8) InterruptAckSummary {
        const pending_before = self.pending_interrupts;
        const cleared_bits = pending_before & ack_mask;
        self.pending_interrupts = pending_before & ~ack_mask;
        return .{
            .anchor = anchor_path,
            .pending_before = pending_before,
            .ack_mask = ack_mask,
            .cleared_bits = cleared_bits,
            .pending_after = self.pending_interrupts,
            .all_acknowledged = self.pending_interrupts == 0,
        };
    }

    pub fn resetForReplay(self: *Self) QueueBookkeepingSummary {
        self.selected_queue = null;
        self.status = 0;
        self.features_negotiated = false;
        self.pending_interrupts = 0;
        self.bumpConfigGeneration();
        return self.queueBookkeepingSummary();
    }

    pub fn statusSummary(self: *const Self) DeviceStatusSummary {
        const failed = (self.status & status_failed) != 0;
        const needs_reset = failed or (self.status & status_device_needs_reset) != 0;
        return .{
            .anchor = anchor_path,
            .device_present = self.device_id != 0,
            .queue_count = self.queue_count,
            .status = self.status,
            .config_generation = self.config_generation,
            .features_negotiated = self.features_negotiated,
            .driver_ready = self.features_negotiated and
                (self.status & status_acknowledge) != 0 and
                (self.status & status_driver) != 0 and
                (self.status & status_driver_ok) != 0 and
                !needs_reset,
            .needs_reset = needs_reset,
            .failed = failed,
            .selected_queue = self.selected_queue,
        };
    }

    pub fn queueBookkeepingSummary(self: *const Self) QueueBookkeepingSummary {
        const selected_queue_valid = if (self.selected_queue) |queue_index|
            queue_index < self.queue_count
        else
            false;
        const status = self.statusSummary();
        return .{
            .anchor = anchor_path,
            .queue_count = self.queue_count,
            .selected_queue = self.selected_queue,
            .selected_queue_valid = selected_queue_valid,
            .config_generation = self.config_generation,
            .queue_bookkeeping_ready = status.device_present and self.queue_count != 0 and !status.needs_reset,
        };
    }
};

test "phase10 virtio core status summary keeps lab-only driver readiness bounded to shared status bookkeeping" {
    var core = try VirtioCoreLab.init(71, 2);

    var summary = core.statusSummary();
    try std.testing.expect(summary.device_present);
    try std.testing.expect(!summary.features_negotiated);
    try std.testing.expect(!summary.driver_ready);
    try std.testing.expect(!summary.needs_reset);

    core.setStatusBits(status_acknowledge | status_driver);
    core.noteFeaturesNegotiated();
    core.setStatusBits(status_driver_ok);

    summary = core.statusSummary();
    try std.testing.expect(summary.features_negotiated);
    try std.testing.expect(summary.driver_ready);
    try std.testing.expect(!summary.failed);
    try std.testing.expect(!summary.needs_reset);
    try std.testing.expectEqual(@as(u8, status_acknowledge | status_driver | status_features_ok | status_driver_ok), summary.status);
}

test "phase10 virtio core queue bookkeeping keeps queue count stable across selection and reset-local replay" {
    var core = try VirtioCoreLab.init(88, 3);

    var queue_summary = try core.selectQueue(2);
    try std.testing.expectEqual(@as(u16, 3), queue_summary.queue_count);
    try std.testing.expectEqual(@as(?u16, 2), queue_summary.selected_queue);
    try std.testing.expect(queue_summary.selected_queue_valid);
    try std.testing.expect(queue_summary.queue_bookkeeping_ready);

    queue_summary = core.resetForReplay();
    try std.testing.expectEqual(@as(u16, 3), queue_summary.queue_count);
    try std.testing.expectEqual(@as(?u16, null), queue_summary.selected_queue);
    try std.testing.expect(!queue_summary.selected_queue_valid);
    try std.testing.expectEqual(@as(u8, 1), queue_summary.config_generation);
    try std.testing.expect(queue_summary.queue_bookkeeping_ready);
}

test "phase10 virtio core interrupt acknowledgements clear only requested bits" {
    var core = try VirtioCoreLab.init(99, 1);
    core.stageInterrupt(0b0101);

    var ack = core.ackInterrupt(0b0001);
    try std.testing.expectEqual(@as(u8, 0b0101), ack.pending_before);
    try std.testing.expectEqual(@as(u8, 0b0001), ack.cleared_bits);
    try std.testing.expectEqual(@as(u8, 0b0100), ack.pending_after);
    try std.testing.expect(!ack.all_acknowledged);

    ack = core.ackInterrupt(0b1111);
    try std.testing.expectEqual(@as(u8, 0b0100), ack.pending_before);
    try std.testing.expectEqual(@as(u8, 0b0100), ack.cleared_bits);
    try std.testing.expectEqual(@as(u8, 0), ack.pending_after);
    try std.testing.expect(ack.all_acknowledged);
}
