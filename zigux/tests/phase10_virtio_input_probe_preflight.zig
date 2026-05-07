const std = @import("std");
const virtio_input = @import("virtio_input");
const virtio_input_probe_preflight = @import("virtio_input_probe_preflight");

test "phase10 virtio input probe preflight keeps identity visible before queue setup" {
    var anonymous = try virtio_input.VirtioInputLab.init("", "", 21, null);

    const summary = virtio_input_probe_preflight.summarize(&anonymous);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expect(!summary.name_ready);
    try std.testing.expect(!summary.serial_ready);
    try std.testing.expect(summary.phys_ready);
    try std.testing.expect(!summary.identity_ready);
    try std.testing.expect(!summary.registration_preflight_ready);
    try std.testing.expectEqual(
        virtio_input_probe_preflight.ProbePreflightBlocker.identity_incomplete,
        summary.blocker.?,
    );
    try std.testing.expect(!summary.ready_for_probe_handoff);
}

test "phase10 virtio input probe preflight reports the next bounded blocker before handoff" {
    var device = try virtio_input.VirtioInputLab.init("probe-tablet", "probe-serial", 22, null);

    var summary = virtio_input_probe_preflight.summarize(&device);
    try std.testing.expect(summary.identity_ready);
    try std.testing.expectEqual(
        virtio_input_probe_preflight.ProbePreflightBlocker.queue_plan_incomplete,
        summary.blocker.?,
    );

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    summary = virtio_input_probe_preflight.summarize(&device);
    try std.testing.expectEqual(
        virtio_input_probe_preflight.ProbePreflightBlocker.device_not_ready,
        summary.blocker.?,
    );
    try std.testing.expect(summary.queue_plan_ready);

    try device.markReady();
    summary = virtio_input_probe_preflight.summarize(&device);
    try std.testing.expectEqual(
        virtio_input_probe_preflight.ProbePreflightBlocker.capability_setup_incomplete,
        summary.blocker.?,
    );
    try std.testing.expect(summary.device_ready);

    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 5,
    });

    summary = virtio_input_probe_preflight.summarize(&device);
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expect(!summary.multitouch_slots_ready);
    try std.testing.expectEqual(
        virtio_input_probe_preflight.ProbePreflightBlocker.multitouch_slots_unplanned,
        summary.blocker.?,
    );

    _ = try device.planMultitouchSlots();
    summary = virtio_input_probe_preflight.summarize(&device);
    try std.testing.expect(summary.multitouch_slots_ready);
    try std.testing.expect(summary.registration_preflight_ready);
    try std.testing.expect(summary.ready_for_probe_handoff);
    try std.testing.expect(summary.blocker == null);
}
