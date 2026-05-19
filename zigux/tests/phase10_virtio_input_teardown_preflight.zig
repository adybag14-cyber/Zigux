const std = @import("std");
const virtio_input = @import("virtio_input");
const teardown_preflight = @import("virtio_input_teardown_preflight");

test "phase10 virtio input teardown preflight blocks reset-local teardown until queued statuses drain" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-29", 8, null);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();

    _ = try device.sendStatus(0x02, 0x01, 7);
    _ = try device.sendStatus(0x02, 0x02, 9);

    var summary = teardown_preflight.summarize(&device);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqualStrings(
        "pending_status_drain",
        teardown_preflight.blockerTag(summary.blocker.?),
    );
    try std.testing.expect(!summary.ready_for_teardown);
    try std.testing.expect(teardown_preflight.runtimeStateArmed(summary));
    try std.testing.expect(!teardown_preflight.capabilityStateArmed(summary));
    try std.testing.expect(teardown_preflight.preservesIdentity(summary));
    try std.testing.expectEqual(@as(usize, 2), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 0), summary.suppressed_status_count);

    _ = try device.drainStatusQueue(2);

    summary = teardown_preflight.summarize(&device);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(summary.ready_for_teardown);
    try std.testing.expect(teardown_preflight.runtimeStateArmed(summary));
    try std.testing.expectEqual(@as(usize, 0), summary.queued_status_count);
}

test "phase10 virtio input teardown preflight keeps suppressed multitouch timestamps non-blocking" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-30", 9, null);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 3,
    });
    _ = try device.planMultitouchSlots();

    const suppressed = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 99);
    try std.testing.expect(!suppressed.sent);

    const summary = teardown_preflight.summarize(&device);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(summary.ready_for_teardown);
    try std.testing.expect(teardown_preflight.runtimeStateArmed(summary));
    try std.testing.expect(teardown_preflight.capabilityStateArmed(summary));
    try std.testing.expect(teardown_preflight.preservesIdentity(summary));
    try std.testing.expectEqual(@as(usize, 0), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);
}
