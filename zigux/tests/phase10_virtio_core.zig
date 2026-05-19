const std = @import("std");
const virtio_core = @import("virtio_core");

test "phase10 virtio core summary replay keeps status and feature bookkeeping reviewable" {
    var core = try virtio_core.VirtioCoreLab.init(0x1041, 4);

    var summary = core.statusSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expect(summary.device_present);
    try std.testing.expectEqual(@as(u16, 4), summary.queue_count);
    try std.testing.expectEqual(@as(u8, 0), summary.status);
    try std.testing.expectEqual(@as(u8, 0), summary.config_generation);
    try std.testing.expect(!summary.features_negotiated);
    try std.testing.expect(!summary.driver_ready);
    try std.testing.expect(!summary.needs_reset);
    try std.testing.expect(!summary.failed);
    try std.testing.expectEqual(@as(?u16, null), summary.selected_queue);

    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    core.setStatusBits(virtio_core.status_driver_ok);

    summary = core.statusSummary();
    try std.testing.expectEqual(
        @as(u8, virtio_core.status_acknowledge | virtio_core.status_driver | virtio_core.status_features_ok | virtio_core.status_driver_ok),
        summary.status,
    );
    try std.testing.expect(summary.features_negotiated);
    try std.testing.expect(summary.driver_ready);
    try std.testing.expect(!summary.needs_reset);
    try std.testing.expect(!summary.failed);
}

test "phase10 virtio core queue bookkeeping replay keeps queue selection and config generation aligned" {
    var core = try virtio_core.VirtioCoreLab.init(0x1042, 3);

    var queue = core.queueBookkeepingSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", queue.anchor);
    try std.testing.expectEqual(@as(u16, 3), queue.queue_count);
    try std.testing.expectEqual(@as(?u16, null), queue.selected_queue);
    try std.testing.expect(!queue.selected_queue_valid);
    try std.testing.expectEqual(@as(u8, 0), queue.config_generation);
    try std.testing.expect(queue.queue_bookkeeping_ready);

    queue = try core.selectQueue(2);
    try std.testing.expectEqual(@as(?u16, 2), queue.selected_queue);
    try std.testing.expect(queue.selected_queue_valid);
    try std.testing.expectEqual(@as(u8, 0), queue.config_generation);

    core.bumpConfigGeneration();
    queue = core.queueBookkeepingSummary();
    try std.testing.expectEqual(@as(?u16, 2), queue.selected_queue);
    try std.testing.expect(queue.selected_queue_valid);
    try std.testing.expectEqual(@as(u8, 1), queue.config_generation);
    try std.testing.expect(queue.queue_bookkeeping_ready);
}

test "phase10 virtio core driver model replay keeps wrapper stages reviewable" {
    var core = try virtio_core.VirtioCoreLab.init(0x1043, 2);

    var summary = core.driverModelSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expectEqual(virtio_core.DriverModelStage.unattached, summary.stage);
    try std.testing.expectEqual(@as(?virtio_core.DriverLifecycleBlocker, .acknowledge_missing), summary.blocker);
    try std.testing.expectEqual(@as(u8, 0), summary.config_generation);

    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(1);
    summary = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.queue_registration_ready, summary.stage);
    try std.testing.expect(summary.queue_selected);
    try std.testing.expect(summary.queue_selected_valid);

    core.setStatusBits(virtio_core.status_driver_ok);
    summary = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.driver_ready, summary.stage);

    core.setStatusBits(virtio_core.status_device_needs_reset);
    summary = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.device_needs_reset, summary.stage);

    core.setStatusBits(virtio_core.status_failed);
    summary = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.device_failed, summary.stage);
    try std.testing.expect(summary.failed);
}

test "phase10 virtio core reset replay clears interrupt debt and drops driver readiness" {
    var core = try virtio_core.VirtioCoreLab.init(0x1044, 2);
    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(1);
    core.setStatusBits(virtio_core.status_driver_ok);
    core.stageInterrupt(0b0110);

    var model = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.driver_ready, model.stage);
    try std.testing.expect(model.driver_ready);

    const queue = core.resetForReplay();
    try std.testing.expectEqual(@as(u16, 2), queue.queue_count);
    try std.testing.expectEqual(@as(?u16, null), queue.selected_queue);
    try std.testing.expect(!queue.selected_queue_valid);
    try std.testing.expectEqual(@as(u8, 1), queue.config_generation);

    const status = core.statusSummary();
    try std.testing.expectEqual(@as(u8, 0), status.status);
    try std.testing.expect(!status.features_negotiated);
    try std.testing.expect(!status.driver_ready);
    try std.testing.expect(!status.needs_reset);
    try std.testing.expectEqual(@as(?u16, null), status.selected_queue);

    const ack = core.ackInterrupt(0xff);
    try std.testing.expectEqual(@as(u8, 0), ack.pending_before);
    try std.testing.expectEqual(@as(u8, 0), ack.cleared_bits);
    try std.testing.expectEqual(@as(u8, 0), ack.pending_after);
    try std.testing.expect(ack.all_acknowledged);

    model = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.unattached, model.stage);
    try std.testing.expectEqual(@as(?virtio_core.DriverLifecycleBlocker, .acknowledge_missing), model.blocker);
}
