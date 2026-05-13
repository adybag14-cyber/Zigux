const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi queue planner stays anchored to virtio_scsi.c" {
    const descriptor = virtio_scsi.VirtioScsiQueueLab.descriptor();
    try std.testing.expectEqualStrings("virtio_scsi_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_queue_family_planner);
    try std.testing.expect(descriptor.provides_probe_config_snapshot);
    try std.testing.expect(descriptor.provides_host_limit_summary);
    try std.testing.expect(descriptor.provides_queue_depth_summary);
    try std.testing.expect(descriptor.provides_command_buffer_ownership_summary);
    try std.testing.expect(descriptor.provides_request_submit_sequencing_summary);
    try std.testing.expect(descriptor.provides_completion_handback_summary);
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

test "phase12 virtio scsi recovery queue plan mirrors the frozen topology" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueuePlan());

    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const plan = try lab.recoveryQueuePlan();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", plan.anchor);
    try std.testing.expectEqual(@as(u16, 6), plan.request_queues);
    try std.testing.expectEqual(@as(u16, 4), plan.default_queues);
    try std.testing.expectEqual(@as(u16, 2), plan.poll_queues);
    try std.testing.expectEqual(@as(u16, 8), plan.total_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.control_queue_index), plan.control_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), plan.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.request_queue_base), plan.first_request_queue_index);
    try std.testing.expectEqual(@as(?u16, 6), plan.first_poll_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), plan.event_buffer_count);
    try std.testing.expect(plan.requires_control_queue_restore);
    try std.testing.expect(plan.requires_event_queue_refill);
    try std.testing.expect(plan.requires_request_queue_restore);

    _ = try lab.restoreAfterTransportReset();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueuePlan());
}

test "phase12 virtio scsi recovery io queue map summary mirrors the frozen topology" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryIoQueueMapSummary());

    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const summary = try lab.recoveryIoQueueMapSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 3), summary.nr_maps);
    try std.testing.expectEqual(@as(u16, 4), summary.default_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.read_queue_count);
    try std.testing.expectEqual(@as(u16, 2), summary.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.default_queue_offset);
    try std.testing.expectEqual(@as(u16, 4), summary.read_queue_offset);
    try std.testing.expectEqual(@as(u16, 4), summary.poll_queue_offset);
    try std.testing.expect(summary.requires_blk_mq_map_restore);
    try std.testing.expect(summary.requires_virtio_affinity_restore);
    try std.testing.expect(summary.requires_poll_map_restore);

    _ = try lab.restoreAfterTransportReset();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryIoQueueMapSummary());
}

test "phase12 virtio scsi recovery queue depth summary mirrors the frozen clamp" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueueDepthSummary());
    try std.testing.expectError(error.QueueDepthSummaryUnavailable, blk: {
        _ = try lab.planQueueLayout(4, 1);
        _ = try lab.freezeForTransportReset();
        break :blk lab.recoveryQueueDepthSummary();
    });
    _ = try lab.restoreAfterTransportReset();

    const captured = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 6,
                .requested_poll_queues = 2,
                .cmd_per_lun = 13,
                .max_target = 9,
                .max_lun = 4,
                .max_sectors = 1024,
            },
            .synthetic_can_queue = 7,
        },
        .requested_depth = 12,
    });
    try std.testing.expectEqual(@as(u32, 7), captured.clamped_queue_depth);

    _ = try lab.freezeForTransportReset();
    const summary = try lab.recoveryQueueDepthSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 12), summary.requested_depth);
    try std.testing.expectEqual(@as(u32, 7), summary.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 7), summary.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 7), summary.clamped_queue_depth);
    try std.testing.expect(summary.tracks_queue_depth);
    try std.testing.expect(summary.requires_change_queue_depth_restore);

    _ = try lab.restoreAfterTransportReset();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueueDepthSummary());
}

test "phase12 virtio scsi recovery io queue map summary collapses without poll queues" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(2, 0);
    _ = try lab.freezeForTransportReset();

    const summary = try lab.recoveryIoQueueMapSummary();
    try std.testing.expectEqual(@as(u16, 1), summary.nr_maps);
    try std.testing.expectEqual(@as(u16, 2), summary.default_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.read_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.default_queue_offset);
    try std.testing.expectEqual(@as(u16, 2), summary.read_queue_offset);
    try std.testing.expectEqual(@as(u16, 2), summary.poll_queue_offset);
    try std.testing.expect(summary.requires_blk_mq_map_restore);
    try std.testing.expect(summary.requires_virtio_affinity_restore);
    try std.testing.expect(!summary.requires_poll_map_restore);
}

test "phase12 virtio scsi recovery host scan summary records restore ordering before rescan" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryHostScanSummary());

    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const summary = try lab.recoveryHostScanSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 6), summary.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), summary.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), summary.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 0), summary.recovery_generation);
    try std.testing.expect(summary.requires_control_queue_restore_before_scan);
    try std.testing.expect(summary.requires_event_rearm_before_scan);
    try std.testing.expect(summary.requires_request_queue_restore_before_scan);
    try std.testing.expect(summary.requires_async_scan_resume);

    _ = try lab.restoreAfterTransportReset();
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryHostScanSummary());
}

test "phase12 virtio scsi rejects invalid freeze restore sequencing" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();

    try std.testing.expectError(error.QueueLayoutUnavailable, lab.freezeForTransportReset());
    try std.testing.expectError(error.TransportNotFrozen, lab.restoreAfterTransportReset());

    _ = try lab.planQueueLayout(2, 0);
    _ = try lab.freezeForTransportReset();
    try std.testing.expectError(error.TransportAlreadyFrozen, lab.freezeForTransportReset());
}

test "phase12 virtio scsi freeze blocks derived capture helpers until restore" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.captureProbeSnapshot(.{
        .num_queues = 4,
        .requested_poll_queues = 1,
        .seg_max = 64,
        .cmd_per_lun = 16,
        .max_target = 7,
        .max_lun = 1,
        .max_sectors = 1024,
    });
    _ = try lab.freezeForTransportReset();

    try std.testing.expectError(error.TransportFrozen, lab.captureProbeSnapshot(.{
        .num_queues = 5,
        .requested_poll_queues = 2,
    }));
    try std.testing.expectError(error.TransportFrozen, lab.captureHostLimitSummary(.{
        .probe = .{
            .num_queues = 5,
            .requested_poll_queues = 2,
            .cmd_per_lun = 9,
        },
        .synthetic_can_queue = 7,
    }));
    try std.testing.expectError(error.TransportFrozen, lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 5,
                .requested_poll_queues = 2,
                .cmd_per_lun = 9,
            },
            .synthetic_can_queue = 7,
        },
        .requested_depth = 4,
    }));
    try std.testing.expectError(error.TransportFrozen, lab.captureCommandBufferOwnershipSummary(.{
        .queue_depth = .{
            .host_limit = .{
                .probe = .{
                    .num_queues = 5,
                    .requested_poll_queues = 2,
                    .cmd_per_lun = 9,
                },
                .synthetic_can_queue = 7,
            },
            .requested_depth = 4,
        },
    }));
    try std.testing.expectError(error.TransportFrozen, lab.captureRequestSubmitSequencingSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 5,
                        .requested_poll_queues = 2,
                        .cmd_per_lun = 9,
                    },
                    .synthetic_can_queue = 7,
                },
                .requested_depth = 4,
            },
        },
        .queue_local_index = 1,
    }));
    try std.testing.expectError(error.TransportFrozen, lab.captureCompletionHandbackSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 5,
                        .requested_poll_queues = 2,
                        .cmd_per_lun = 9,
                    },
                    .synthetic_can_queue = 7,
                },
                .requested_depth = 4,
            },
        },
        .queue_local_index = 1,
    }));
    try std.testing.expectError(error.TransportFrozen, lab.captureIoQueueMapSummary(5, 2));

    _ = try lab.restoreAfterTransportReset();

    const recaptured = try lab.captureHostLimitSummary(.{
        .probe = .{
            .num_queues = 5,
            .requested_poll_queues = 2,
            .cmd_per_lun = 9,
            .max_target = 3,
            .max_lun = 2,
            .max_sectors = 1536,
        },
        .synthetic_can_queue = 7,
    });
    try std.testing.expectEqual(@as(u32, 7), recaptured.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 7), recaptured.effective_cmd_per_lun);

    const requeued = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 5,
                .requested_poll_queues = 2,
                .cmd_per_lun = 9,
                .max_target = 3,
                .max_lun = 2,
                .max_sectors = 1536,
            },
            .synthetic_can_queue = 7,
        },
        .requested_depth = 11,
    });
    try std.testing.expectEqual(@as(u32, 7), requeued.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 7), requeued.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 7), requeued.clamped_queue_depth);

    const command_buffers = try lab.captureCommandBufferOwnershipSummary(.{
        .queue_depth = .{
            .host_limit = .{
                .probe = .{
                    .num_queues = 5,
                    .requested_poll_queues = 2,
                    .cmd_per_lun = 9,
                    .max_target = 3,
                    .max_lun = 2,
                    .max_sectors = 1536,
                },
                .synthetic_can_queue = 7,
            },
            .requested_depth = 11,
        },
    });
    try std.testing.expectEqual(@as(u32, 7), command_buffers.clamped_queue_depth);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_command_buffer_bytes), command_buffers.command_bytes_per_request);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_sense_buffer_bytes), command_buffers.sense_bytes_per_request);

    const submit = try lab.captureRequestSubmitSequencingSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 5,
                        .requested_poll_queues = 2,
                        .cmd_per_lun = 9,
                        .max_target = 3,
                        .max_lun = 2,
                        .max_sectors = 1536,
                    },
                    .synthetic_can_queue = 7,
                },
                .requested_depth = 11,
            },
        },
        .queue_local_index = 4,
    });
    try std.testing.expectEqual(@as(u16, 6), submit.queue_global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, submit.queue_kind);
    try std.testing.expect(submit.submission_requires_queue_selection);
    try std.testing.expect(submit.submission_requires_dma_mapping_before_kick);
    try std.testing.expect(submit.submission_requires_kick_after_descriptors_ready);
    try std.testing.expect(submit.stays_pre_runtime_only);

    const remapped = try lab.captureIoQueueMapSummary(5, 2);
    try std.testing.expectEqual(@as(u16, 3), remapped.default_queue_count);
    try std.testing.expectEqual(@as(u16, 2), remapped.poll_queue_count);
}

test "phase12 virtio scsi repeated freeze restore tracks the replanned recovery boundary" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(6, 2);
    _ = try lab.freezeForTransportReset();

    const first_plan = try lab.recoveryQueuePlan();
    try std.testing.expectEqual(@as(u16, 6), first_plan.request_queues);
    try std.testing.expectEqual(@as(u16, 2), first_plan.poll_queues);
    try std.testing.expectEqual(@as(?u16, 6), first_plan.first_poll_queue_index);

    const first_restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(@as(u16, 1), first_restore.recovery_generation);
    try std.testing.expectEqual(@as(u16, 6), first_restore.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), first_restore.remembered_poll_queues);
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueuePlan());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryIoQueueMapSummary());

    const replanned = try lab.planQueueLayout(4, 1);
    try std.testing.expectEqual(@as(u16, 3), replanned.default_queues);
    try std.testing.expectEqual(@as(u16, 1), replanned.poll_queues);
    try std.testing.expectEqual(@as(?u16, 5), replanned.first_poll_queue_index);

    const second_freeze = try lab.freezeForTransportReset();
    try std.testing.expectEqual(@as(u16, 1), second_freeze.recovery_generation);
    try std.testing.expectEqual(@as(u16, 4), second_freeze.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_freeze.remembered_poll_queues);

    const second_plan = try lab.recoveryQueuePlan();
    try std.testing.expectEqual(@as(u16, 4), second_plan.request_queues);
    try std.testing.expectEqual(@as(u16, 3), second_plan.default_queues);
    try std.testing.expectEqual(@as(u16, 1), second_plan.poll_queues);
    try std.testing.expectEqual(@as(u16, 6), second_plan.total_queues);
    try std.testing.expectEqual(@as(?u16, 5), second_plan.first_poll_queue_index);

    const second_map = try lab.recoveryIoQueueMapSummary();
    try std.testing.expectEqual(@as(u16, 3), second_map.default_queue_count);
    try std.testing.expectEqual(@as(u16, 1), second_map.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 3), second_map.read_queue_offset);
    try std.testing.expectEqual(@as(u16, 3), second_map.poll_queue_offset);
    try std.testing.expect(second_map.requires_poll_map_restore);

    const second_restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(@as(u16, 2), second_restore.recovery_generation);
    try std.testing.expectEqual(@as(u16, 4), second_restore.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 1), second_restore.remembered_poll_queues);
}

test "phase12 virtio scsi probe snapshot records config fields and queue layout" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const snapshot = try lab.captureProbeSnapshot(.{
        .num_queues = 8,
        .requested_poll_queues = 3,
        .seg_max = 128,
        .cmd_per_lun = 64,
        .max_target = 31,
        .max_lun = 7,
        .max_sectors = 2048,
    });

    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", snapshot.anchor);
    try std.testing.expectEqual(@as(u16, 8), snapshot.config_num_queues);
    try std.testing.expectEqual(@as(u32, 128), snapshot.config_seg_max);
    try std.testing.expectEqual(@as(u32, 64), snapshot.config_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 31), snapshot.config_max_target);
    try std.testing.expectEqual(@as(u32, 7), snapshot.config_max_lun);
    try std.testing.expectEqual(@as(u32, 2048), snapshot.config_max_sectors);
    try std.testing.expectEqual(@as(u32, 128), snapshot.effective_seg_max);
    try std.testing.expectEqual(@as(u32, 64), snapshot.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 32), snapshot.effective_max_target_count);
    try std.testing.expectEqual(@as(u32, 0x4008), snapshot.effective_max_lun);
    try std.testing.expectEqual(@as(u32, 2048), snapshot.effective_max_sectors);
    try std.testing.expectEqual(@as(u16, 1), snapshot.control_queue_count);
    try std.testing.expectEqual(@as(u16, 1), snapshot.event_queue_count);
    try std.testing.expectEqual(@as(u16, 8), snapshot.request_queue_count);
    try std.testing.expectEqual(@as(u16, 5), snapshot.default_queue_count);
    try std.testing.expectEqual(@as(u16, 3), snapshot.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 10), snapshot.total_queue_count);
    try std.testing.expectEqual(@as(u16, virtio_scsi.request_queue_base), snapshot.first_request_queue_index);
    try std.testing.expectEqual(@as(?u16, 7), snapshot.first_poll_queue_index);
}

test "phase12 virtio scsi probe snapshot applies Linux-style fallback defaults" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const snapshot = try lab.captureProbeSnapshot(.{
        .num_queues = 2,
        .requested_poll_queues = 4,
        .seg_max = 0,
        .cmd_per_lun = 0,
        .max_target = 0,
        .max_lun = 0,
        .max_sectors = 0,
    });

    try std.testing.expectEqual(@as(u32, virtio_scsi.default_seg_max), snapshot.effective_seg_max);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_cmd_per_lun), snapshot.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 1), snapshot.effective_max_target_count);
    try std.testing.expectEqual(@as(u32, virtio_scsi.max_lun_format_one_bias), snapshot.effective_max_lun);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_max_sectors), snapshot.effective_max_sectors);
    try std.testing.expectEqual(@as(u16, 1), snapshot.default_queue_count);
    try std.testing.expectEqual(@as(u16, 1), snapshot.poll_queue_count);
    try std.testing.expectEqual(@as(?u16, 3), snapshot.first_poll_queue_index);
}

test "phase12 virtio scsi host limit summary clamps cmd_per_lun against synthetic can_queue" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureHostLimitSummary(.{
        .probe = .{
            .num_queues = 8,
            .requested_poll_queues = 3,
            .seg_max = 128,
            .cmd_per_lun = 64,
            .max_target = 31,
            .max_lun = 7,
            .max_sectors = 2048,
        },
        .synthetic_can_queue = 12,
    });

    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 64), summary.config_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 12), summary.config_can_queue);
    try std.testing.expectEqual(@as(u32, 12), summary.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 12), summary.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 32), summary.max_target);
    try std.testing.expectEqual(@as(u32, 0x4008), summary.max_lun);
    try std.testing.expectEqual(@as(u32, 2048), summary.max_sectors);
    try std.testing.expectEqual(@as(u16, 8), summary.nr_hw_queues);
}

test "phase12 virtio scsi host limit summary falls back to request queues and defaults" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureHostLimitSummary(.{
        .probe = .{
            .num_queues = 3,
            .requested_poll_queues = 9,
            .seg_max = 0,
            .cmd_per_lun = 0,
            .max_target = 0,
            .max_lun = 0,
            .max_sectors = 0,
        },
        .synthetic_can_queue = 0,
    });

    try std.testing.expectEqual(@as(u32, 0), summary.config_can_queue);
    try std.testing.expectEqual(@as(u32, 0), summary.config_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 3), summary.effective_can_queue);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_cmd_per_lun), summary.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 1), summary.max_target);
    try std.testing.expectEqual(@as(u32, virtio_scsi.max_lun_format_one_bias), summary.max_lun);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_max_sectors), summary.max_sectors);
    try std.testing.expectEqual(@as(u16, 3), summary.nr_hw_queues);
}

test "phase12 virtio scsi queue depth summary clamps requests to cmd_per_lun" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 8,
                .requested_poll_queues = 3,
                .cmd_per_lun = 64,
                .max_target = 31,
                .max_lun = 7,
                .max_sectors = 2048,
            },
            .synthetic_can_queue = 12,
        },
        .requested_depth = 40,
    });

    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 40), summary.requested_depth);
    try std.testing.expectEqual(@as(u32, 12), summary.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 12), summary.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 12), summary.clamped_queue_depth);
    try std.testing.expect(summary.tracks_queue_depth);
    try std.testing.expect(summary.uses_change_queue_depth);
}

test "phase12 virtio scsi queue depth summary preserves smaller requests and defaults" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 3,
                .requested_poll_queues = 9,
                .cmd_per_lun = 0,
                .max_target = 0,
                .max_lun = 0,
                .max_sectors = 0,
            },
            .synthetic_can_queue = 0,
        },
        .requested_depth = 1,
    });

    try std.testing.expectEqual(@as(u32, 1), summary.requested_depth);
    try std.testing.expectEqual(@as(u32, 3), summary.effective_can_queue);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_cmd_per_lun), summary.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 1), summary.clamped_queue_depth);
    try std.testing.expect(summary.tracks_queue_depth);
    try std.testing.expect(summary.uses_change_queue_depth);
}

test "phase12 virtio scsi command buffer ownership summary tracks clamped queue depth and bytes" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureCommandBufferOwnershipSummary(.{
        .queue_depth = .{
            .host_limit = .{
                .probe = .{
                    .num_queues = 8,
                    .requested_poll_queues = 3,
                    .cmd_per_lun = 64,
                    .max_target = 31,
                    .max_lun = 7,
                    .max_sectors = 2048,
                },
                .synthetic_can_queue = 12,
            },
            .requested_depth = 40,
        },
        .command_bytes = 48,
        .sense_bytes = 96,
    });

    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 40), summary.requested_depth);
    try std.testing.expectEqual(@as(u32, 12), summary.clamped_queue_depth);
    try std.testing.expectEqual(@as(u32, 48), summary.command_bytes_per_request);
    try std.testing.expectEqual(@as(u32, 96), summary.sense_bytes_per_request);
    try std.testing.expectEqual(@as(u64, 576), summary.total_command_bytes);
    try std.testing.expectEqual(@as(u64, 1152), summary.total_sense_bytes);
    try std.testing.expect(summary.owns_one_command_buffer_per_request);
    try std.testing.expect(summary.owns_one_sense_buffer_per_request);
    try std.testing.expect(summary.requires_dma_mapping_later);
    try std.testing.expect(summary.preserves_pre_registration_scope);
}

test "phase12 virtio scsi command buffer ownership summary defaults buffer sizes" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureCommandBufferOwnershipSummary(.{
        .queue_depth = .{
            .host_limit = .{
                .probe = .{
                    .num_queues = 3,
                    .requested_poll_queues = 9,
                    .cmd_per_lun = 0,
                    .max_target = 0,
                    .max_lun = 0,
                    .max_sectors = 0,
                },
                .synthetic_can_queue = 0,
            },
            .requested_depth = 1,
        },
    });

    try std.testing.expectEqual(@as(u32, 1), summary.clamped_queue_depth);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_command_buffer_bytes), summary.command_bytes_per_request);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_sense_buffer_bytes), summary.sense_bytes_per_request);
    try std.testing.expectEqual(@as(u64, virtio_scsi.default_command_buffer_bytes), summary.total_command_bytes);
    try std.testing.expectEqual(@as(u64, virtio_scsi.default_sense_buffer_bytes), summary.total_sense_bytes);
}

test "phase12 virtio scsi request submit sequencing summary records queue selection and pre-kick ordering" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureRequestSubmitSequencingSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 8,
                        .requested_poll_queues = 3,
                        .cmd_per_lun = 64,
                        .max_target = 31,
                        .max_lun = 7,
                        .max_sectors = 2048,
                    },
                    .synthetic_can_queue = 12,
                },
                .requested_depth = 40,
            },
            .command_bytes = 48,
            .sense_bytes = 96,
        },
        .queue_local_index = 6,
    });

    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 6), summary.queue_local_index);
    try std.testing.expectEqual(@as(u16, 8), summary.queue_global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, summary.queue_kind);
    try std.testing.expectEqual(@as(u32, 40), summary.requested_depth);
    try std.testing.expectEqual(@as(u32, 12), summary.clamped_queue_depth);
    try std.testing.expectEqual(@as(u32, 48), summary.command_bytes_per_request);
    try std.testing.expectEqual(@as(u32, 96), summary.sense_bytes_per_request);
    try std.testing.expect(summary.submission_uses_preallocated_buffers);
    try std.testing.expect(summary.submission_requires_queue_selection);
    try std.testing.expect(summary.submission_requires_dma_mapping_before_kick);
    try std.testing.expect(summary.submission_requires_kick_after_descriptors_ready);
    try std.testing.expect(summary.submission_blocks_while_transport_frozen);
    try std.testing.expect(summary.stays_pre_runtime_only);
}

test "phase12 virtio scsi request submit sequencing summary respects the frozen transport boundary" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(4, 1);
    _ = try lab.freezeForTransportReset();

    try std.testing.expectError(error.TransportFrozen, lab.captureRequestSubmitSequencingSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 4,
                        .requested_poll_queues = 1,
                        .cmd_per_lun = 4,
                    },
                    .synthetic_can_queue = 3,
                },
                .requested_depth = 2,
            },
        },
        .queue_local_index = 1,
    }));

    _ = try lab.restoreAfterTransportReset();
    const summary = try lab.captureRequestSubmitSequencingSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 4,
                        .requested_poll_queues = 1,
                        .cmd_per_lun = 4,
                    },
                    .synthetic_can_queue = 3,
                },
                .requested_depth = 2,
            },
        },
        .queue_local_index = 1,
    });
    try std.testing.expectEqual(@as(u16, 3), summary.queue_global_index);
    try std.testing.expect(summary.submission_requires_kick_after_descriptors_ready);
}

test "phase12 virtio scsi completion handback summary records used-ring ownership return" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureCompletionHandbackSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 5,
                        .requested_poll_queues = 2,
                        .cmd_per_lun = 9,
                        .max_target = 3,
                        .max_lun = 2,
                        .max_sectors = 1536,
                    },
                    .synthetic_can_queue = 7,
                },
                .requested_depth = 11,
            },
        },
        .queue_local_index = 4,
    });
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 4), summary.queue_local_index);
    try std.testing.expectEqual(@as(u16, 6), summary.queue_global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, summary.queue_kind);
    try std.testing.expectEqual(@as(u32, 11), summary.requested_depth);
    try std.testing.expectEqual(@as(u32, 7), summary.clamped_queue_depth);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_command_buffer_bytes), summary.command_bytes_per_request);
    try std.testing.expectEqual(@as(u32, virtio_scsi.default_sense_buffer_bytes), summary.sense_bytes_per_request);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), summary.event_queue_index);
    try std.testing.expect(summary.completion_uses_preallocated_buffers);
    try std.testing.expect(summary.completion_requires_used_ring_before_handback);
    try std.testing.expect(summary.completion_reads_sense_before_recycle);
    try std.testing.expect(summary.completion_returns_command_buffer_after_handback);
    try std.testing.expect(summary.completion_returns_sense_buffer_after_handback);
    try std.testing.expect(summary.completion_releases_request_slot_before_reuse);
    try std.testing.expect(summary.stays_pre_runtime_only);
}

test "phase12 virtio scsi completion handback summary respects the frozen transport boundary" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.planQueueLayout(4, 1);
    _ = try lab.freezeForTransportReset();

    try std.testing.expectError(error.TransportFrozen, lab.captureCompletionHandbackSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 4,
                        .requested_poll_queues = 1,
                        .cmd_per_lun = 4,
                    },
                    .synthetic_can_queue = 3,
                },
                .requested_depth = 2,
            },
        },
        .queue_local_index = 1,
    }));

    _ = try lab.restoreAfterTransportReset();
    const summary = try lab.captureCompletionHandbackSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 4,
                        .requested_poll_queues = 1,
                        .cmd_per_lun = 4,
                    },
                    .synthetic_can_queue = 3,
                },
                .requested_depth = 2,
            },
        },
        .queue_local_index = 1,
    });
    try std.testing.expectEqual(@as(u16, 3), summary.queue_global_index);
    try std.testing.expect(summary.completion_requires_used_ring_before_handback);
}

test "phase12 virtio scsi io queue map summary mirrors default and poll offsets" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureIoQueueMapSummary(8, 3);

    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 3), summary.nr_maps);
    try std.testing.expectEqual(@as(u16, 5), summary.default_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.read_queue_count);
    try std.testing.expectEqual(@as(u16, 3), summary.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.default_queue_offset);
    try std.testing.expectEqual(@as(u16, 5), summary.read_queue_offset);
    try std.testing.expectEqual(@as(u16, 5), summary.poll_queue_offset);
    try std.testing.expect(summary.default_queues_use_virtio_affinity);
    try std.testing.expect(summary.poll_queues_use_blk_mq_mapping);
}

test "phase12 virtio scsi io queue map summary collapses to one map without polling queues" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const summary = try lab.captureIoQueueMapSummary(2, 0);

    try std.testing.expectEqual(@as(u16, 1), summary.nr_maps);
    try std.testing.expectEqual(@as(u16, 2), summary.default_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.read_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.poll_queue_count);
    try std.testing.expectEqual(@as(u16, 0), summary.default_queue_offset);
    try std.testing.expectEqual(@as(u16, 2), summary.read_queue_offset);
    try std.testing.expectEqual(@as(u16, 2), summary.poll_queue_offset);
    try std.testing.expect(summary.default_queues_use_virtio_affinity);
    try std.testing.expect(!summary.poll_queues_use_blk_mq_mapping);
}
