const std = @import("std");
const virtio_input = @import("virtio_input");

pub const TeardownObservationSummary = virtio_input.TeardownObservationSummary;

pub fn summarize(device: *const virtio_input.VirtioInputLab) TeardownObservationSummary {
    return device.teardownObservationSummary();
}

pub fn runtimeStateArmed(summary: TeardownObservationSummary) bool {
    return summary.clears_runtime_state;
}

pub fn capabilityStateArmed(summary: TeardownObservationSummary) bool {
    return summary.clears_capability_state;
}

pub fn preservesIdentity(summary: TeardownObservationSummary) bool {
    return summary.preserves_identity;
}

test "phase10 virtio input teardown observation keeps identity while resettable runtime state stays explicit" {
    var device = try virtio_input.VirtioInputLab.init(
        "Virtio Touch Lab",
        "serial-24",
        3,
        .{
            .vendor = 0x1af4,
            .product = 0x1052,
            .version = 7,
        },
    );

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();

    const sent = try device.sendStatus(1, 2, 3);
    try std.testing.expect(sent.sent);
    try std.testing.expectEqual(@as(usize, 1), sent.queued_status_count);

    const summary = device.teardownObservationSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqualStrings("Virtio Touch Lab", summary.name);
    try std.testing.expectEqualStrings("serial-24", summary.serial);
    try std.testing.expectEqualStrings("virtio3/input0", summary.phys);
    try std.testing.expect(summary.event_queue_was_configured);
    try std.testing.expect(summary.status_queue_was_configured);
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);
    try std.testing.expectEqual(@as(usize, 1), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 0), summary.suppressed_status_count);
    try std.testing.expect(summary.ready_before_reset);
    try std.testing.expect(summary.preserves_identity);
    try std.testing.expect(summary.clears_runtime_state);
    try std.testing.expect(!summary.clears_capability_state);

    device.reset();

    const snapshot = device.configSnapshot();
    try std.testing.expectEqualStrings("Virtio Touch Lab", snapshot.name);
    try std.testing.expectEqualStrings("serial-24", snapshot.serial);
    try std.testing.expectEqualStrings("virtio3/input0", snapshot.phys);
    try std.testing.expectEqual(@as(u16, virtio_input.bus_virtual), snapshot.ids.bustype);
    try std.testing.expectEqual(@as(u16, 0x1af4), snapshot.ids.vendor);
    try std.testing.expectEqual(@as(u16, 0x1052), snapshot.ids.product);
    try std.testing.expectEqual(@as(u16, 7), snapshot.ids.version);
    try std.testing.expectEqual(@as(u16, 0), device.event_descriptor_count);
    try std.testing.expectEqual(@as(u16, 0), device.status_descriptor_count);
    try std.testing.expectEqual(@as(u16, 0), device.queued_event_buffer_count);
    try std.testing.expectEqual(@as(usize, 0), device.queued_status_count);
    try std.testing.expect(!device.ready);
}

test "phase10 virtio input teardown observation reports capability and suppressed-status cleanup before reset" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-25", 4, null);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 5,
    });

    const slot_plan = try device.planMultitouchSlots();
    try std.testing.expect(slot_plan.multitouch_enabled);
    try std.testing.expectEqual(@as(u16, 6), slot_plan.planned_slot_count);

    const suppressed = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 88);
    try std.testing.expect(!suppressed.sent);
    try std.testing.expect(suppressed.suppressed_msc_timestamp);
    try std.testing.expectEqual(@as(usize, 0), suppressed.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), suppressed.suppressed_status_count);

    const summary = device.teardownObservationSummary();
    try std.testing.expect(summary.event_queue_was_configured);
    try std.testing.expect(summary.status_queue_was_configured);
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);
    try std.testing.expectEqual(@as(usize, 0), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);
    try std.testing.expect(summary.ready_before_reset);
    try std.testing.expect(summary.multitouch_was_enabled);
    try std.testing.expectEqual(@as(u16, 6), summary.planned_multitouch_slots);
    try std.testing.expect(summary.clears_runtime_state);
    try std.testing.expect(summary.clears_capability_state);

    device.reset();

    try std.testing.expectEqual(@as(usize, 0), device.suppressed_status_count);
    try std.testing.expectEqual(@as(usize, 0), device.config_bitmap_count);
    try std.testing.expectEqual(@as(usize, 0), device.abs_info_count);
    try std.testing.expectEqual(@as(u16, 0), device.planned_multitouch_slots);
    try std.testing.expect(!device.multitouch_enabled);

    const post_reset = device.teardownObservationSummary();
    try std.testing.expect(!post_reset.clears_runtime_state);
    try std.testing.expect(!post_reset.clears_capability_state);
}
