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
