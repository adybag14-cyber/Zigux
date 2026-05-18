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

pub const DriverLifecycleBlocker = enum {
    device_absent,
    acknowledge_missing,
    driver_missing,
    features_missing,
    queue_selection_missing,
    queue_selection_invalid,
    driver_ok_missing,
    device_needs_reset,
    device_failed,
};

pub const LifecycleGuardSummary = struct {
    anchor: []const u8,
    device_present: bool,
    attached: bool,
    features_negotiated: bool,
    queue_selected: bool,
    queue_selected_valid: bool,
    queue_registration_ready: bool,
    driver_ready: bool,
    needs_reset: bool,
    failed: bool,
    blocker: ?DriverLifecycleBlocker,
    config_generation: u8,
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

    pub fn lifecycleGuardSummary(self: *const Self) LifecycleGuardSummary {
        const status = self.statusSummary();
        const queue = self.queueBookkeepingSummary();
        const attached = status.device_present and (self.status & status_acknowledge) != 0;
        const queue_selected = self.selected_queue != null;
        const queue_registration_ready = attached and
            (self.status & status_driver) != 0 and
            status.features_negotiated and
            queue.selected_queue_valid and
            !status.needs_reset;

        const blocker: ?DriverLifecycleBlocker = if (!status.device_present)
            .device_absent
        else if (status.failed)
            .device_failed
        else if (status.needs_reset)
            .device_needs_reset
        else if ((self.status & status_acknowledge) == 0)
            .acknowledge_missing
        else if ((self.status & status_driver) == 0)
            .driver_missing
        else if (!status.features_negotiated)
            .features_missing
        else if (!queue_selected)
            .queue_selection_missing
        else if (!queue.selected_queue_valid)
            .queue_selection_invalid
        else if ((self.status & status_driver_ok) == 0)
            .driver_ok_missing
        else
            null;

        return .{
            .anchor = anchor_path,
            .device_present = status.device_present,
            .attached = attached,
            .features_negotiated = status.features_negotiated,
            .queue_selected = queue_selected,
            .queue_selected_valid = queue.selected_queue_valid,
            .queue_registration_ready = queue_registration_ready,
            .driver_ready = status.driver_ready and queue.selected_queue_valid,
            .needs_reset = status.needs_reset,
            .failed = status.failed,
            .blocker = blocker,
            .config_generation = status.config_generation,
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

test "phase10 virtio core lifecycle guard summary tracks staged driver progression" {
    var core = try VirtioCoreLab.init(51, 2);

    var summary = core.lifecycleGuardSummary();
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .acknowledge_missing), summary.blocker);
    try std.testing.expect(!summary.attached);
    try std.testing.expect(!summary.queue_registration_ready);
    try std.testing.expect(!summary.driver_ready);

    core.setStatusBits(status_acknowledge);
    summary = core.lifecycleGuardSummary();
    try std.testing.expect(summary.attached);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .driver_missing), summary.blocker);

    core.setStatusBits(status_driver);
    summary = core.lifecycleGuardSummary();
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .features_missing), summary.blocker);

    core.noteFeaturesNegotiated();
    summary = core.lifecycleGuardSummary();
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .queue_selection_missing), summary.blocker);

    _ = try core.selectQueue(1);
    summary = core.lifecycleGuardSummary();
    try std.testing.expect(summary.queue_registration_ready);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .driver_ok_missing), summary.blocker);

    core.setStatusBits(status_driver_ok);
    summary = core.lifecycleGuardSummary();
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, null), summary.blocker);
    try std.testing.expect(summary.driver_ready);
}

test "phase10 virtio core lifecycle guard summary blocks ready state when reset becomes required" {
    var core = try VirtioCoreLab.init(57, 1);
    core.setStatusBits(status_acknowledge | status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(0);
    core.setStatusBits(status_driver_ok);

    var summary = core.lifecycleGuardSummary();
    try std.testing.expect(summary.driver_ready);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, null), summary.blocker);

    core.setStatusBits(status_device_needs_reset);
    summary = core.lifecycleGuardSummary();
    try std.testing.expect(summary.needs_reset);
    try std.testing.expect(!summary.queue_registration_ready);
    try std.testing.expect(!summary.driver_ready);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .device_needs_reset), summary.blocker);

    core.setStatusBits(status_failed);
    summary = core.lifecycleGuardSummary();
    try std.testing.expect(summary.failed);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .device_failed), summary.blocker);
}
