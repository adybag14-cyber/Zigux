const std = @import("std");
const virtio_core = @import("virtio_core");

test "phase10 virtio core keeps reset replay teardown bookkeeping after driver validation narrows queue features" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 11 });
    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(1);
    try device.offerDriverFeature(7);
    try device.offerDriverFeature(11);
    _ = try device.finalizeFeaturesWithDriverValidation(&.{ 1, 11 });
    try device.markDriverReady();
    try device.registerQueueCallback(1, 4, "control_done");
    try device.configureQueueDescriptorShape(1, 1, 2, false);
    device.noteNeedsReset();

    const reset_summary = device.resetReplaySummary();
    try std.testing.expect(reset_summary.driver_ready);
    try std.testing.expectEqual(@as(usize, 1), reset_summary.registered_queue_count);
    try std.testing.expect(reset_summary.will_clear_queue_callbacks);

    try std.testing.expectError(error.ResetRequired, device.offerDriverFeature(7));
    try std.testing.expectError(error.ResetRequired, device.finalizeFeatures());
    try std.testing.expectError(error.ResetRequired, device.markDriverReady());
    try std.testing.expectError(error.ResetRequired, device.unregisterQueueCallback(1));
    try std.testing.expectError(error.ResetRequired, device.disableQueueCallback(1));
    try std.testing.expectError(error.ResetRequired, device.enableQueueCallback(1));
    try std.testing.expectError(error.ResetRequired, device.notifyQueueUsed(1));
    try std.testing.expectError(error.ResetRequired, device.configureQueueDescriptorShape(1, 2, 1, true));

    device.reset();

    const cleared_summary = device.resetReplaySummary();
    try std.testing.expect(!cleared_summary.driver_ready);
    try std.testing.expectEqual(@as(usize, 0), cleared_summary.registered_queue_count);
    try std.testing.expect(!cleared_summary.will_clear_queue_callbacks);
}
