const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input queue and probe preflight carry multitouch slot intent through ready state" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-mt", 21, null);
    device.setMultitouch(true);

    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{ virtio_input.abs_mt_slot, 0x30 });
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 7,
    });
    try device.configureAbsInfo(0x30, .{
        .minimum = 0,
        .maximum = 1024,
        .resolution = 16,
    });
    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();

    const callback_summary = try device.queueCallbackPreflightSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", callback_summary.anchor);
    try std.testing.expectEqual(@as(u16, virtio_input.event_queue_index), callback_summary.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_input.status_queue_index), callback_summary.status_queue_index);
    try std.testing.expectEqual(@as(u16, 16), callback_summary.queued_event_buffer_count);
    try std.testing.expect(callback_summary.event_buffers_ready);
    try std.testing.expect(callback_summary.status_queue_configured);
    try std.testing.expect(callback_summary.device_ready);
    try std.testing.expect(callback_summary.registration_ready);
    try std.testing.expect(callback_summary.ready_for_queue_callback);

    const probe_summary = try device.probePreflightSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", probe_summary.anchor);
    try std.testing.expectEqual(@as(usize, 6), probe_summary.supported_select_count);
    try std.testing.expect(probe_summary.identity_ready);
    try std.testing.expect(probe_summary.capability_ready);
    try std.testing.expect(probe_summary.registration_ready);
    try std.testing.expect(probe_summary.event_queue_configured);
    try std.testing.expect(probe_summary.status_queue_configured);
    try std.testing.expect(probe_summary.event_buffers_ready);
    try std.testing.expect(probe_summary.device_ready);
    try std.testing.expect(probe_summary.ready_for_probe_handoff);
}

test "phase10 virtio input invalid multitouch slot metadata blocks all later preflight summaries" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-bad-slot", 22, null);

    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{ virtio_input.abs_mt_slot, 0x30 });
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = -1,
        .maximum = 7,
    });
    try device.configureAbsInfo(0x30, .{
        .minimum = 0,
        .maximum = 1024,
        .resolution = 16,
    });
    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();

    try std.testing.expectError(error.MultitouchSlotMinimumNegative, device.registrationPreflightSummary());
    try std.testing.expectError(error.MultitouchSlotMinimumNegative, device.queueCallbackPreflightSummary());
    try std.testing.expectError(error.MultitouchSlotMinimumNegative, device.probePreflightSummary());
}
