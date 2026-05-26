const std = @import("std");
const virtio_core = @import("virtio_core");

pub const LifecycleGuardSummary = virtio_core.LifecycleGuardSummary;
pub const DriverModelSummary = virtio_core.DriverModelSummary;
pub const QueueBookkeepingSummary = virtio_core.QueueBookkeepingSummary;
pub const InterruptAckSummary = virtio_core.InterruptAckSummary;
pub const DriverLifecycleBlocker = virtio_core.DriverLifecycleBlocker;
pub const DriverModelStage = virtio_core.DriverModelStage;
pub const ResetTeardownSummary = struct {
    blocker_before: ?DriverLifecycleBlocker,
    blocker_after: ?DriverLifecycleBlocker,
    failed_before: bool,
    failed_after: bool,
    needs_reset_before: bool,
    needs_reset_after: bool,
    queue_count_preserved: bool,
    selected_queue_cleared: bool,
    config_generation_advanced: bool,
};
pub const DriverReadinessReviewSummary = struct {
    anchor: []const u8,
    status_bits_ready: bool,
    lifecycle_ready: bool,
    queue_selected: bool,
    queue_selected_valid: bool,
    needs_reset: bool,
    failed: bool,
    blocker: ?DriverLifecycleBlocker,
    config_generation: u8,
};

pub fn summarizeLifecycleGuard(core: *const virtio_core.VirtioCoreLab) LifecycleGuardSummary {
    return core.lifecycleGuardSummary();
}

pub fn summarizeDriverModel(core: *const virtio_core.VirtioCoreLab) DriverModelSummary {
    return core.driverModelSummary();
}

pub fn summarizeDriverReadinessReview(core: *const virtio_core.VirtioCoreLab) DriverReadinessReviewSummary {
    const status = core.statusSummary();
    const guard = core.lifecycleGuardSummary();
    return .{
        .anchor = guard.anchor,
        .status_bits_ready = status.driver_ready,
        .lifecycle_ready = guard.driver_ready,
        .queue_selected = guard.queue_selected,
        .queue_selected_valid = guard.queue_selected_valid,
        .needs_reset = guard.needs_reset,
        .failed = guard.failed,
        .blocker = guard.blocker,
        .config_generation = guard.config_generation,
    };
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

pub fn summarizeResetTeardown(core: *virtio_core.VirtioCoreLab) ResetTeardownSummary {
    const before_guard = core.lifecycleGuardSummary();
    const before_queue = core.queueBookkeepingSummary();
    const after_queue = core.resetForReplay();
    const after_guard = core.lifecycleGuardSummary();

    return .{
        .blocker_before = before_guard.blocker,
        .blocker_after = after_guard.blocker,
        .failed_before = before_guard.failed,
        .failed_after = after_guard.failed,
        .needs_reset_before = before_guard.needs_reset,
        .needs_reset_after = after_guard.needs_reset,
        .queue_count_preserved = before_queue.queue_count == after_queue.queue_count,
        .selected_queue_cleared = after_queue.selected_queue == null and !after_queue.selected_queue_valid,
        .config_generation_advanced = before_queue.config_generation != after_queue.config_generation,
    };
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

test "phase10 virtio core verify keeps status-bit readiness separate from queue-gated lifecycle readiness" {
    var core = try virtio_core.VirtioCoreLab.init(0x1045, 2);
    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    core.setStatusBits(virtio_core.status_driver_ok);

    var summary = summarizeDriverReadinessReview(&core);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expect(summary.status_bits_ready);
    try std.testing.expect(!summary.lifecycle_ready);
    try std.testing.expect(!summary.queue_selected);
    try std.testing.expect(!summary.queue_selected_valid);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .queue_selection_missing), summary.blocker);
    try std.testing.expectEqual(@as(u8, 0), summary.config_generation);

    _ = try core.selectQueue(1);
    summary = summarizeDriverReadinessReview(&core);
    try std.testing.expect(summary.status_bits_ready);
    try std.testing.expect(summary.lifecycle_ready);
    try std.testing.expect(summary.queue_selected);
    try std.testing.expect(summary.queue_selected_valid);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, null), summary.blocker);
}

test "phase10 virtio core verify keeps readiness review blocked when reset becomes required" {
    var core = try virtio_core.VirtioCoreLab.init(0x1046, 1);
    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(0);
    core.setStatusBits(virtio_core.status_driver_ok);

    var summary = summarizeDriverReadinessReview(&core);
    try std.testing.expect(summary.status_bits_ready);
    try std.testing.expect(summary.lifecycle_ready);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, null), summary.blocker);

    core.setStatusBits(virtio_core.status_device_needs_reset);
    summary = summarizeDriverReadinessReview(&core);
    try std.testing.expect(!summary.status_bits_ready);
    try std.testing.expect(!summary.lifecycle_ready);
    try std.testing.expect(summary.needs_reset);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .device_needs_reset), summary.blocker);
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

test "phase10 virtio core verify keeps failed-status teardown visible until reset clears it" {
    var core = try virtio_core.VirtioCoreLab.init(0x1044, 1);
    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(0);
    core.setStatusBits(
        virtio_core.status_driver_ok |
            virtio_core.status_device_needs_reset |
            virtio_core.status_failed,
    );

    const teardown = summarizeResetTeardown(&core);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .device_failed), teardown.blocker_before);
    try std.testing.expect(teardown.failed_before);
    try std.testing.expect(teardown.needs_reset_before);
    try std.testing.expect(teardown.queue_count_preserved);
    try std.testing.expect(teardown.selected_queue_cleared);
    try std.testing.expect(teardown.config_generation_advanced);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .acknowledge_missing), teardown.blocker_after);
    try std.testing.expect(!teardown.failed_after);
    try std.testing.expect(!teardown.needs_reset_after);
}
