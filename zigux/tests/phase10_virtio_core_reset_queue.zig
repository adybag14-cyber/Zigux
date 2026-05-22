const std = @import("std");
const virtio_core = @import("virtio_core");

test "phase10 virtio core reset queue replay drops ready state until queue and status are replayed" {
    var core = try virtio_core.VirtioCoreLab.init(0x1046, 2);
    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    const before = try core.selectQueue(1);
    core.setStatusBits(virtio_core.status_driver_ok);

    var model = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.driver_ready, model.stage);
    try std.testing.expect(model.driver_ready);

    const after = core.resetForReplay();
    try std.testing.expectEqual(before.queue_count, after.queue_count);
    try std.testing.expectEqual(@as(?u16, null), after.selected_queue);
    try std.testing.expect(!after.selected_queue_valid);
    try std.testing.expectEqual(@as(u8, before.config_generation +% 1), after.config_generation);

    model = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.unattached, model.stage);
    try std.testing.expectEqual(@as(?virtio_core.DriverLifecycleBlocker, .acknowledge_missing), model.blocker);
    try std.testing.expect(!model.driver_ready);

    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(0);
    model = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.queue_registration_ready, model.stage);

    core.setStatusBits(virtio_core.status_driver_ok);
    model = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.driver_ready, model.stage);
    try std.testing.expect(model.driver_ready);
}

test "phase10 virtio core reset queue replay clears reset-required state" {
    var core = try virtio_core.VirtioCoreLab.init(0x1047, 1);
    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(0);
    core.setStatusBits(virtio_core.status_driver_ok | virtio_core.status_device_needs_reset);

    var guard = core.lifecycleGuardSummary();
    try std.testing.expect(guard.needs_reset);
    try std.testing.expectEqual(@as(?virtio_core.DriverLifecycleBlocker, .device_needs_reset), guard.blocker);

    _ = core.resetForReplay();
    guard = core.lifecycleGuardSummary();
    try std.testing.expect(!guard.needs_reset);
    try std.testing.expectEqual(@as(?virtio_core.DriverLifecycleBlocker, .acknowledge_missing), guard.blocker);
}
