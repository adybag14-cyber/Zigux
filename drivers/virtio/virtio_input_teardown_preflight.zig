const std = @import("std");
const virtio_input = @import("virtio_input");

pub const TeardownPreflightBlocker = enum {
    pending_status_drain,
};

pub const TeardownPreflightSummary = struct {
    anchor: []const u8,
    queued_status_count: usize,
    suppressed_status_count: usize,
    preserves_identity: bool,
    runtime_state_armed: bool,
    capability_state_armed: bool,
    blocker: ?TeardownPreflightBlocker,
    ready_for_teardown: bool,
};

pub fn summarize(device: *const virtio_input.VirtioInputLab) TeardownPreflightSummary {
    const observation = device.teardownObservationSummary();
    const blocker: ?TeardownPreflightBlocker = if (observation.queued_status_count != 0)
        .pending_status_drain
    else
        null;

    return .{
        .anchor = observation.anchor,
        .queued_status_count = observation.queued_status_count,
        .suppressed_status_count = observation.suppressed_status_count,
        .preserves_identity = observation.preserves_identity,
        .runtime_state_armed = observation.clears_runtime_state,
        .capability_state_armed = observation.clears_capability_state,
        .blocker = blocker,
        .ready_for_teardown = blocker == null,
    };
}

pub fn blockerTag(blocker: TeardownPreflightBlocker) []const u8 {
    return @tagName(blocker);
}

pub fn runtimeStateArmed(summary: TeardownPreflightSummary) bool {
    return summary.runtime_state_armed;
}

pub fn capabilityStateArmed(summary: TeardownPreflightSummary) bool {
    return summary.capability_state_armed;
}

pub fn preservesIdentity(summary: TeardownPreflightSummary) bool {
    return summary.preserves_identity;
}

pub fn queuedStatusCount(summary: TeardownPreflightSummary) usize {
    return summary.queued_status_count;
}

pub fn suppressedStatusCount(summary: TeardownPreflightSummary) usize {
    return summary.suppressed_status_count;
}

pub fn waitingOnPendingStatusDrain(summary: TeardownPreflightSummary) bool {
    return summary.blocker == .pending_status_drain;
}

pub fn readyForTeardown(summary: TeardownPreflightSummary) bool {
    return summary.ready_for_teardown;
}

test "phase10 virtio input teardown preflight stays teardown-ready when identity is preserved and no status drain is pending" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Tablet Lab", "serial-clean", 11, null);

    const summary = summarize(&device);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expect(preservesIdentity(summary));
    try std.testing.expect(!runtimeStateArmed(summary));
    try std.testing.expect(!capabilityStateArmed(summary));
    try std.testing.expectEqual(@as(usize, 0), queuedStatusCount(summary));
    try std.testing.expectEqual(@as(usize, 0), suppressedStatusCount(summary));
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(!waitingOnPendingStatusDrain(summary));
    try std.testing.expect(readyForTeardown(summary));
}

test "phase10 virtio input teardown preflight blocks teardown until queued status work is drained while preserving suppressed timestamp accounting" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-drain", 12, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 2,
    });
    _ = try device.planMultitouchSlots();

    _ = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 1);
    _ = try device.sendStatus(0x02, 0x01, 7);

    var summary = summarize(&device);
    try std.testing.expect(preservesIdentity(summary));
    try std.testing.expect(runtimeStateArmed(summary));
    try std.testing.expect(capabilityStateArmed(summary));
    try std.testing.expectEqualStrings("pending_status_drain", blockerTag(summary.blocker.?));
    try std.testing.expect(waitingOnPendingStatusDrain(summary));
    try std.testing.expectEqual(@as(usize, 1), queuedStatusCount(summary));
    try std.testing.expectEqual(@as(usize, 1), suppressedStatusCount(summary));
    try std.testing.expect(!readyForTeardown(summary));

    const drain = try device.drainStatusQueue(1);
    try std.testing.expectEqual(@as(usize, 1), drain.completed_status_count);
    try std.testing.expectEqual(@as(usize, 1), drain.pending_status_count_before);
    try std.testing.expectEqual(@as(usize, 0), drain.pending_status_count_after);
    try std.testing.expectEqual(@as(usize, 1), drain.suppressed_status_count);

    summary = summarize(&device);
    try std.testing.expect(preservesIdentity(summary));
    try std.testing.expect(runtimeStateArmed(summary));
    try std.testing.expect(capabilityStateArmed(summary));
    try std.testing.expectEqual(@as(usize, 0), queuedStatusCount(summary));
    try std.testing.expectEqual(@as(usize, 1), suppressedStatusCount(summary));
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(!waitingOnPendingStatusDrain(summary));
    try std.testing.expect(readyForTeardown(summary));
}
