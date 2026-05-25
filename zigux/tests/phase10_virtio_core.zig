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

test "phase10 virtio core attribute replay keeps status_show and features_show bitstrings explicit" {
    var core = try virtio_core.VirtioCoreLab.init(0x1041, 4);
    core.setDeviceFeatures(0x0000_0000_0000_1037);
    core.setDriverFeatures(0x0000_0000_0000_1013);
    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    const negotiated = core.driverValidationNarrow(0x0000_0000_0000_1011);
    core.setStatusBits(virtio_core.status_driver_ok);

    try std.testing.expectEqual(@as(u64, 0x0000_0000_0000_1011), negotiated);

    const feature_summary = core.featureBitSummary();
    try std.testing.expect(feature_summary.features_negotiated);
    try std.testing.expectEqual(@as(u64, 0x0000_0000_0000_1037), feature_summary.device_features);
    try std.testing.expectEqual(@as(u64, 0x0000_0000_0000_1013), feature_summary.driver_features);
    try std.testing.expectEqual(@as(u64, 0x0000_0000_0000_1011), feature_summary.negotiated_features);

    var status_buffer: [11]u8 = undefined;
    var device_buffer: [19]u8 = undefined;
    var driver_buffer: [19]u8 = undefined;
    var negotiated_buffer: [19]u8 = undefined;

    try std.testing.expectEqualStrings("0x0000000f\n", try core.statusShow(&status_buffer));
    try std.testing.expectEqualStrings("0x0000000000001037\n", try core.deviceFeaturesShow(&device_buffer));
    try std.testing.expectEqualStrings("0x0000000000001013\n", try core.driverFeaturesShow(&driver_buffer));
    try std.testing.expectEqualStrings("0x0000000000001011\n", try core.negotiatedFeaturesShow(&negotiated_buffer));
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
    try std.testing.expect(!summary.queue_registration_ready);

    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(1);
    summary = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.queue_registration_ready, summary.stage);
    try std.testing.expect(summary.queue_selected);
    try std.testing.expect(summary.queue_selected_valid);
    try std.testing.expect(summary.queue_registration_ready);

    core.setStatusBits(virtio_core.status_driver_ok);
    summary = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.driver_ready, summary.stage);
    try std.testing.expect(summary.queue_registration_ready);
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
    try std.testing.expect(model.queue_registration_ready);

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

    const feature_summary = core.featureBitSummary();
    try std.testing.expectEqual(@as(u64, 0), feature_summary.driver_features);
    try std.testing.expectEqual(@as(u64, 0), feature_summary.negotiated_features);

    const ack = core.ackInterrupt(0xff);
    try std.testing.expectEqual(@as(u8, 0), ack.pending_before);
    try std.testing.expectEqual(@as(u8, 0), ack.cleared_bits);
    try std.testing.expectEqual(@as(u8, 0), ack.pending_after);
    try std.testing.expect(ack.all_acknowledged);

    model = core.driverModelSummary();
    try std.testing.expectEqual(virtio_core.DriverModelStage.unattached, model.stage);
    try std.testing.expectEqual(@as(?virtio_core.DriverLifecycleBlocker, .acknowledge_missing), model.blocker);
    try std.testing.expect(!model.queue_registration_ready);
}

test "phase10 virtio core driver id replay keeps exact wildcard and unmatched rules reviewable" {
    var core = try virtio_core.VirtioCoreLab.init(0x1052, 2);

    var summary = core.driverIdMatchSummary(&.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
        .{ .device_id = 0x1052, .vendor_id = virtio_core.default_vendor_id },
        .{ .device_id = virtio_core.any_id, .vendor_id = virtio_core.any_id },
    });
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(@as(?usize, 1), summary.matched_rule_index);
    try std.testing.expect(!summary.matched_device_any);
    try std.testing.expect(!summary.matched_vendor_any);

    core.setVendorId(0x1AF5);
    summary = core.driverIdMatchSummary(&.{
        .{ .device_id = virtio_core.any_id, .vendor_id = 0x1AF5 },
    });
    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(@as(?usize, 0), summary.matched_rule_index);
    try std.testing.expect(summary.matched_device_any);
    try std.testing.expect(!summary.matched_vendor_any);

    summary = core.driverIdMatchSummary(&.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
    });
    try std.testing.expect(!summary.matched);
    try std.testing.expectEqual(@as(?usize, null), summary.matched_rule_index);
    try std.testing.expect(!summary.matched_device_any);
    try std.testing.expect(!summary.matched_vendor_any);
}
