const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input drains queued status completions without touching suppressed multitouch counters" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-drain", 24, null);

    try std.testing.expectError(error.StatusQueueNotConfigured, device.drainStatusQueue(0));

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    device.setMultitouch(true);

    _ = try device.sendStatus(0x11, 0x01, 1);
    _ = try device.sendStatus(0x12, 0x02, 2);
    _ = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 3);

    var summary = try device.drainStatusQueue(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 1), summary.completed_status_count);
    try std.testing.expectEqual(@as(usize, 2), summary.pending_status_count_before);
    try std.testing.expectEqual(@as(usize, 1), summary.pending_status_count_after);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);
    try std.testing.expect(summary.ready);

    summary = try device.drainStatusQueue(1);
    try std.testing.expectEqual(@as(usize, 1), summary.completed_status_count);
    try std.testing.expectEqual(@as(usize, 1), summary.pending_status_count_before);
    try std.testing.expectEqual(@as(usize, 0), summary.pending_status_count_after);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);
    try std.testing.expect(summary.ready);

    try std.testing.expectError(error.StatusCompletionCountExceedsQueued, device.drainStatusQueue(1));
}

test "phase10 virtio input blocker summary stays reviewable across reset rollback" {
    var device = try virtio_input.VirtioInputLab.init("tablet", "serial-17", 17, null);

    var summary = try device.registrationBlockerSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expect(!summary.registration_preflight_ready);
    try std.testing.expect(!summary.queue_callback_ready);
    try std.testing.expect(!summary.probe_handoff_ready);
    try std.testing.expect(summary.input_registration_lifecycle_blocked);
    try std.testing.expect(summary.transport_queue_callbacks_blocked);
    try std.testing.expect(summary.freeze_restore_blocked);
    try std.testing.expect(summary.probe_remove_blocked);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", summary.risky_transport_posture);

    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{ 0x00, 0x01 });
    try device.configureAbsInfo(0x00, .{
        .minimum = -2048,
        .maximum = 2047,
        .resolution = 32,
    });
    try device.configureAbsInfo(0x01, .{
        .minimum = 0,
        .maximum = 4095,
        .resolution = 48,
    });

    summary = try device.registrationBlockerSummary();
    try std.testing.expect(summary.registration_preflight_ready);
    try std.testing.expect(!summary.queue_callback_ready);
    try std.testing.expect(!summary.probe_handoff_ready);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();

    summary = try device.registrationBlockerSummary();
    try std.testing.expect(summary.registration_preflight_ready);
    try std.testing.expect(summary.queue_callback_ready);
    try std.testing.expect(summary.probe_handoff_ready);
    try std.testing.expect(summary.input_registration_lifecycle_blocked);
    try std.testing.expect(summary.transport_queue_callbacks_blocked);

    device.reset();

    summary = try device.registrationBlockerSummary();
    try std.testing.expect(!summary.registration_preflight_ready);
    try std.testing.expect(!summary.queue_callback_ready);
    try std.testing.expect(!summary.probe_handoff_ready);
    try std.testing.expect(summary.input_registration_lifecycle_blocked);
    try std.testing.expect(summary.transport_queue_callbacks_blocked);
    try std.testing.expect(summary.freeze_restore_blocked);
    try std.testing.expect(summary.probe_remove_blocked);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", summary.risky_transport_posture);
}
