const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi queue planner stays anchored to virtio_scsi.c" {
    const descriptor = virtio_scsi.VirtioScsiQueueLab.descriptor();
    try std.testing.expectEqualStrings("virtio_scsi_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_queue_family_planner);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_scsi_host);
    try std.testing.expect(descriptor.touches_transport_reset);

    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const layout = try lab.planQueueLayout(8, 3);
    try std.testing.expectEqual(@as(u16, 8), layout.request_queues);
    try std.testing.expectEqual(@as(u16, 3), layout.requested_poll_queues);
    try std.testing.expectEqual(@as(u16, 5), layout.default_queues);
    try std.testing.expectEqual(@as(u16, 0), layout.read_queues);
    try std.testing.expectEqual(@as(u16, 3), layout.poll_queues);
    try std.testing.expectEqual(@as(u16, 10), layout.total_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.control_queue_index), layout.control_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), layout.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.request_queue_base), layout.first_request_queue_index);
    try std.testing.expectEqual(@as(?u16, 7), layout.first_poll_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), layout.event_buffer_count);
}

test "phase12 virtio scsi clamps poll queues and classifies request families" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const layout = try lab.planQueueLayout(4, 9);
    try std.testing.expectEqual(@as(u16, 1), layout.default_queues);
    try std.testing.expectEqual(@as(u16, 3), layout.poll_queues);
    try std.testing.expectEqual(@as(?u16, 3), layout.first_poll_queue_index);

    const first = try lab.requestQueue(0);
    try std.testing.expectEqual(@as(u16, 0), first.local_index);
    try std.testing.expectEqual(@as(u16, 2), first.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request, first.kind);

    const second = try lab.requestQueue(1);
    try std.testing.expectEqual(@as(u16, 3), second.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, second.kind);

    const fourth = try lab.requestQueue(3);
    try std.testing.expectEqual(@as(u16, 5), fourth.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, fourth.kind);
}

test "phase12 virtio scsi rejects invalid queue counts and unavailable request lookups" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();

    try std.testing.expectError(error.InvalidRequestQueueCount, lab.planQueueLayout(0, 0));
    try std.testing.expectError(error.QueueLayoutUnavailable, lab.requestQueue(0));
    try std.testing.expectError(
        error.QueueCountOverflow,
        lab.planQueueLayout(std.math.maxInt(u16), 0),
    );

    _ = try lab.planQueueLayout(1, 4);
    try std.testing.expectEqual(@as(u16, 1), lab.last_layout.?.default_queues);
    try std.testing.expectEqual(@as(u16, 0), lab.last_layout.?.poll_queues);
    try std.testing.expectEqual(@as(?u16, null), lab.last_layout.?.first_poll_queue_index);
    try std.testing.expectError(error.RequestQueueIndexOutOfRange, lab.requestQueue(1));
}

test "phase12 virtio scsi freeze blocks queue planning until restore clears layout" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(6, 2);

    const frozen = try lab.freezeForTransportReset();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", frozen.anchor);
    try std.testing.expectEqual(virtio_scsi.RecoveryAction.freeze, frozen.action);
    try std.testing.expect(!frozen.was_frozen);
    try std.testing.expect(frozen.is_frozen);
    try std.testing.expect(!frozen.request_planning_available);
    try std.testing.expect(!frozen.event_recycling_enabled);
    try std.testing.expectEqual(@as(u16, 6), frozen.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), frozen.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), frozen.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 0), frozen.recovery_generation);

    try std.testing.expectError(error.TransportFrozen, lab.planQueueLayout(6, 1));
    try std.testing.expectError(error.TransportFrozen, lab.requestQueue(0));

    const restored = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(virtio_scsi.RecoveryAction.restore, restored.action);
    try std.testing.expect(restored.was_frozen);
    try std.testing.expect(!restored.is_frozen);
    try std.testing.expect(restored.request_planning_available);
    try std.testing.expect(restored.event_recycling_enabled);
    try std.testing.expectEqual(@as(u16, 6), restored.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), restored.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), restored.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 1), restored.recovery_generation);

    try std.testing.expectError(error.QueueLayoutUnavailable, lab.requestQueue(0));

    const replanned = try lab.planQueueLayout(3, 1);
    try std.testing.expectEqual(@as(u16, 2), replanned.default_queues);
    try std.testing.expectEqual(@as(u16, 1), replanned.poll_queues);
}

test "phase12 virtio scsi restore summary mirrors virtscsi_restore ordering" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();

    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRestoreSummary());

    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const summary = try lab.recoveryRestoreSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 6), summary.request_queues);
    try std.testing.expectEqual(@as(u16, 4), summary.default_queues);
    try std.testing.expectEqual(@as(u16, 2), summary.poll_queues);
    try std.testing.expectEqual(@as(u16, 8), summary.total_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.control_queue_index), summary.control_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), summary.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.request_queue_base), summary.first_request_queue_index);
    try std.testing.expectEqual(@as(?u16, 6), summary.first_poll_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), summary.event_buffer_count);
    try std.testing.expect(summary.requires_find_vqs);
    try std.testing.expect(summary.find_vqs_before_device_ready);
    try std.testing.expect(summary.device_ready_before_event_rearm);
    try std.testing.expect(summary.preserves_scsi_host_registration);
    try std.testing.expect(!summary.reruns_host_scan);

    _ = try lab.restoreAfterTransportReset();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRestoreSummary());
}

test "phase12 virtio scsi restore queue rebind summary keeps queue families explicit" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();

    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRestoreQueueRebindSummary());

    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const summary = try lab.recoveryRestoreQueueRebindSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, virtio_scsi.control_queue_index), summary.control_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), summary.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.request_queue_base), summary.first_default_queue_index);
    try std.testing.expectEqual(@as(u16, 5), summary.last_default_queue_index);
    try std.testing.expectEqual(@as(u16, 4), summary.default_queue_count);
    try std.testing.expectEqual(@as(?u16, 6), summary.first_poll_queue_index);
    try std.testing.expectEqual(@as(?u16, 7), summary.last_poll_queue_index);
    try std.testing.expectEqual(@as(u16, 2), summary.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 8), summary.total_queues);
    try std.testing.expect(summary.recreates_control_and_event_queues);
    try std.testing.expect(summary.recreates_request_queues_before_device_ready);
    try std.testing.expect(summary.defers_event_buffers_until_after_device_ready);

    _ = try lab.restoreAfterTransportReset();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRestoreQueueRebindSummary());
}

test "phase12 virtio scsi rollback summary keeps frozen topology gated until replanning" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();

    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRollbackSummary());

    _ = try lab.planQueueLayout(7, 2);
    _ = try lab.freezeForTransportReset();

    const summary = try lab.recoveryRollbackSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 7), summary.request_queues);
    try std.testing.expectEqual(@as(u16, 5), summary.default_queues);
    try std.testing.expectEqual(@as(u16, 2), summary.poll_queues);
    try std.testing.expectEqual(@as(u16, 9), summary.total_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), summary.event_buffer_count);
    try std.testing.expectEqual(@as(u16, 0), summary.recovery_generation);
    try std.testing.expect(summary.blocks_queue_planning_until_restore);
    try std.testing.expect(summary.blocks_request_queue_access_until_restore);
    try std.testing.expect(summary.keeps_frozen_layout_for_restore);
    try std.testing.expect(summary.clears_live_layout_after_restore);
    try std.testing.expect(summary.requires_replan_before_queue_reuse);

    const restored = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(@as(u16, 1), restored.recovery_generation);
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryRollbackSummary());
    try std.testing.expectError(error.QueueLayoutUnavailable, lab.requestQueue(0));

    _ = try lab.planQueueLayout(3, 1);
    _ = try lab.freezeForTransportReset();

    const refreshed = try lab.recoveryRollbackSummary();
    try std.testing.expectEqual(@as(u16, 3), refreshed.request_queues);
    try std.testing.expectEqual(@as(u16, 2), refreshed.default_queues);
    try std.testing.expectEqual(@as(u16, 1), refreshed.poll_queues);
    try std.testing.expectEqual(@as(u16, 5), refreshed.total_queues);
    try std.testing.expectEqual(@as(u16, 1), refreshed.recovery_generation);
}

test "phase12 virtio scsi rejects invalid freeze restore sequencing" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();

    try std.testing.expectError(error.QueueLayoutUnavailable, lab.freezeForTransportReset());
    try std.testing.expectError(error.TransportNotFrozen, lab.restoreAfterTransportReset());

    _ = try lab.planQueueLayout(2, 0);
    _ = try lab.freezeForTransportReset();
    try std.testing.expectError(error.TransportAlreadyFrozen, lab.freezeForTransportReset());
}
