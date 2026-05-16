const std = @import("std");
const virtio_input = @import("virtio_input");
const probe_preflight = @import("virtio_input_probe_preflight");

test "phase10 virtio input probe preflight helper keeps blocker tags and ready transition reviewable" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-26", 5, null);

    var summary = probe_preflight.summarize(&device);
    try std.testing.expect(summary.identity_ready);
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expectEqualStrings("event_queue_unconfigured", probe_preflight.blockerTag(summary.blocker.?));
    try std.testing.expect(!summary.ready_for_probe_handoff);

    try device.configureEventQueue(16);
    summary = probe_preflight.summarize(&device);
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.status_queue_unconfigured, summary.blocker.?);

    try device.configureStatusQueue(8);
    summary = probe_preflight.summarize(&device);
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.event_buffers_unfilled, summary.blocker.?);

    _ = try device.fillEventBuffers();
    summary = probe_preflight.summarize(&device);
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.capability_setup_incomplete, summary.blocker.?);

    try device.markReady();
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 7,
    });
    summary = probe_preflight.summarize(&device);
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.multitouch_slots_unplanned, summary.blocker.?);
    try std.testing.expectEqualStrings("multitouch_slots_unplanned", probe_preflight.blockerTag(summary.blocker.?));

    const slot_plan = try device.planMultitouchSlots();
    try std.testing.expect(slot_plan.multitouch_enabled);

    summary = probe_preflight.summarize(&device);
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expect(summary.multitouch_slots_ready);
    try std.testing.expectEqual(@as(?virtio_input.ProbePreflightBlocker, null), summary.blocker);
    try std.testing.expect(summary.ready_for_probe_handoff);
}
