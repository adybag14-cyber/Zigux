const std = @import("std");
const virtio_core = @import("virtio_core");

pub const LifecycleGuardSummary = virtio_core.LifecycleGuardSummary;
pub const DriverModelSummary = virtio_core.DriverModelSummary;
pub const QueueBookkeepingSummary = virtio_core.QueueBookkeepingSummary;
pub const InterruptAckSummary = virtio_core.InterruptAckSummary;
pub const DriverLifecycleBlocker = virtio_core.DriverLifecycleBlocker;
pub const DriverModelStage = virtio_core.DriverModelStage;

pub fn summarizeLifecycleGuard(core: *const virtio_core.VirtioCoreLab) LifecycleGuardSummary {
    return core.lifecycleGuardSummary();
}

pub fn summarizeDriverModel(core: *const virtio_core.VirtioCoreLab) DriverModelSummary {
    return core.driverModelSummary();
}

pub fn summarizeQueueBookkeeping(core: *const virtio_core.VirtioCoreLab) QueueBookkeepingSummary {
    return core.queueBookkeepingSummary();
}

pub fn summarizeInterruptAck(core: *virtio_core.VirtioCoreLab, ack_mask: u8) InterruptAckSummary {
    return core.ackInterrupt(ack_mask);
}

pub fn blockerTag(blocker: DriverLifecycleBlocker) []const u8 {
    return @tagName(blocker);
}

pub fn stageTag(stage: DriverModelStage) []const u8 {
    return @tagName(stage);
}

pub fn resetReplayPreservesQueueShape(before: QueueBookkeepingSummary, after: QueueBookkeepingSummary) bool {
    return before.queue_count == after.queue_count and
        after.selected_queue == null and
        !after.selected_queue_valid and
        before.config_generation != after.config_generation;
}

pub fn interruptAckFullyClears(summary: InterruptAckSummary) bool {
    return summary.pending_after == 0 and summary.all_acknowledged;
}

test "phase10 virtio core verify keeps lifecycle checkpoints explicit" {
    var core = try virtio_core.VirtioCoreLab.init(0x1040, 2);

    var guard = summarizeLifecycleGuard(&core);
    try std.testing.expectEqualStrings("acknowledge_missing", blockerTag(guard.blocker.?));
    try std.testing.expect(!guard.attached);

    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(1);

    var model = summarizeDriverModel(&core);
    try std.testing.expectEqualStrings("queue_registration_ready", stageTag(model.stage));
    try std.testing.expectEqualStrings("driver_ok_missing", blockerTag(model.blocker.?));
    try std.testing.expect(!model.driver_ready);

    core.setStatusBits(virtio_core.status_driver_ok);
    guard = summarizeLifecycleGuard(&core);
    model = summarizeDriverModel(&core);
    try std.testing.expect(guard.driver_ready);
    try std.testing.expect(model.driver_ready);
    try std.testing.expectEqualStrings("driver_ready", stageTag(model.stage));
}

test "phase10 virtio core verify keeps reset replay below transport lifecycle claims" {
    var core = try virtio_core.VirtioCoreLab.init(0x1041, 3);
    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    const before = try core.selectQueue(2);
    core.setStatusBits(virtio_core.status_driver_ok);
    core.stageInterrupt(0b0110);

    const after = core.resetForReplay();
    try std.testing.expect(resetReplayPreservesQueueShape(before, after));

    const status = core.statusSummary();
    const model = summarizeDriverModel(&core);
    try std.testing.expectEqual(@as(u8, 0), status.status);
    try std.testing.expect(!status.driver_ready);
    try std.testing.expectEqualStrings("unattached", stageTag(model.stage));
    try std.testing.expectEqualStrings("acknowledge_missing", blockerTag(model.blocker.?));
}

test "phase10 virtio core verify lets failed status override ready stages" {
    var core = try virtio_core.VirtioCoreLab.init(0x1042, 1);
    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(0);
    core.setStatusBits(virtio_core.status_driver_ok);

    core.setStatusBits(virtio_core.status_failed);
    const guard = summarizeLifecycleGuard(&core);
    const model = summarizeDriverModel(&core);
    try std.testing.expect(guard.failed);
    try std.testing.expect(guard.needs_reset);
    try std.testing.expectEqualStrings("device_failed", blockerTag(guard.blocker.?));
    try std.testing.expectEqualStrings("device_failed", stageTag(model.stage));
}

test "phase10 virtio core verify keeps interrupt acknowledgement reviewable" {
    var core = try virtio_core.VirtioCoreLab.init(0x1043, 1);
    core.stageInterrupt(0b0111);

    var ack = summarizeInterruptAck(&core, 0b0101);
    try std.testing.expectEqual(@as(u8, 0b0010), ack.pending_after);
    try std.testing.expect(!interruptAckFullyClears(ack));

    ack = summarizeInterruptAck(&core, 0b0010);
    try std.testing.expectEqual(@as(u8, 0), ack.pending_after);
    try std.testing.expect(interruptAckFullyClears(ack));
}
