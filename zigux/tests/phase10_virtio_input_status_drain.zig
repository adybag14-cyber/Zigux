const std = @import("std");
const virtio_input = @import("virtio_input");
const status_drain = @import("virtio_input_status_drain");

test "phase10 virtio input status drain preserves suppressed timestamp counts while draining queued statuses" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-27", 6, null);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    device.setMultitouch(true);

    const suppressed = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 88);
    try std.testing.expect(!suppressed.sent);
    try std.testing.expect(suppressed.suppressed_msc_timestamp);
    try std.testing.expectEqual(@as(usize, 0), suppressed.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), suppressed.suppressed_status_count);

    const queued = try device.sendStatus(0x11, 0x00, 1);
    try std.testing.expect(queued.sent);
    try std.testing.expectEqual(@as(usize, 1), queued.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), queued.suppressed_status_count);

    const drained = try status_drain.summarize(&device, 1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", drained.anchor);
    try std.testing.expectEqual(@as(usize, 1), drained.completed_status_count);
    try std.testing.expectEqual(@as(usize, 1), drained.pending_status_count_before);
    try std.testing.expectEqual(@as(usize, 0), drained.pending_status_count_after);
    try std.testing.expectEqual(@as(usize, 1), drained.suppressed_status_count);
    try std.testing.expect(drained.ready);
}

test "phase10 virtio input status drain rejects completions beyond queued statuses" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-28", 7, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();

    const queued = try device.sendStatus(0x12, 0x01, 2);
    try std.testing.expect(queued.sent);
    try std.testing.expectEqual(@as(usize, 1), queued.queued_status_count);
    try std.testing.expectEqual(@as(usize, 0), queued.suppressed_status_count);

    try std.testing.expectError(
        error.StatusCompletionCountExceedsQueued,
        status_drain.summarize(&device, 2),
    );

    const drained = try status_drain.summarize(&device, 1);
    try std.testing.expectEqual(@as(usize, 1), drained.completed_status_count);
    try std.testing.expectEqual(@as(usize, 1), drained.pending_status_count_before);
    try std.testing.expectEqual(@as(usize, 0), drained.pending_status_count_after);
    try std.testing.expectEqual(@as(usize, 0), drained.suppressed_status_count);
    try std.testing.expect(drained.ready);
}
