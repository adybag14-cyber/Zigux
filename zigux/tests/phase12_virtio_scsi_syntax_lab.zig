const std = @import("std");

const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi syntax lab keeps current queue-planning exports reachable" {
    const descriptor = virtio_scsi.VirtioScsiQueueLab.descriptor();

    _ = virtio_scsi.ModuleDescriptor;
    _ = virtio_scsi.QueueLayoutSummary;
    _ = virtio_scsi.ProbeRequest;
    _ = virtio_scsi.ProbeSnapshot;
    _ = virtio_scsi.HostLimitRequest;
    _ = virtio_scsi.HostLimitSummary;
    _ = virtio_scsi.QueueDepthRequest;
    _ = virtio_scsi.QueueDepthSummary;
    _ = virtio_scsi.CommandBufferOwnershipRequest;
    _ = virtio_scsi.CommandBufferOwnershipSummary;
    _ = virtio_scsi.ControlPathGovernanceRequest;
    _ = virtio_scsi.ControlPathGovernanceSummary;
    _ = virtio_scsi.RequestSubmitSequencingRequest;
    _ = virtio_scsi.RequestSubmitSequencingSummary;
    _ = virtio_scsi.IoQueueMapSummary;
    _ = virtio_scsi.RecoveryAction;
    _ = virtio_scsi.RecoverySummary;
    _ = virtio_scsi.RecoveryQueuePlan;
    _ = virtio_scsi.RecoveryIoQueueMapSummary;
    _ = virtio_scsi.RecoveryQueueDepthSummary;
    _ = virtio_scsi.RecoveryEventBufferOwnershipSummary;
    _ = virtio_scsi.RecoveryHostScanSummary;
    _ = virtio_scsi.RequestQueueKind;
    _ = virtio_scsi.RequestQueueSummary;
    _ = virtio_scsi.CompletionHandbackSummary;

    try std.testing.expectEqualStrings("virtio_scsi_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_queue_family_planner);
    try std.testing.expect(descriptor.provides_probe_config_snapshot);
    try std.testing.expect(descriptor.provides_host_limit_summary);
    try std.testing.expect(descriptor.provides_queue_depth_summary);
    try std.testing.expect(descriptor.provides_command_buffer_ownership_summary);
    try std.testing.expect(descriptor.provides_control_path_governance_summary);
    try std.testing.expect(descriptor.provides_request_submit_sequencing_summary);
    try std.testing.expect(descriptor.provides_completion_handback_summary);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_scsi_host);
    try std.testing.expect(descriptor.touches_transport_reset);

    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const layout = try lab.planQueueLayout(4, 2);
    try std.testing.expectEqual(@as(u16, 4), layout.request_queues);
    try std.testing.expectEqual(@as(u16, 2), layout.requested_poll_queues);
    try std.testing.expectEqual(@as(u16, 2), layout.default_queues);
    try std.testing.expectEqual(@as(u16, 2), layout.poll_queues);
    try std.testing.expectEqual(@as(u16, 6), layout.total_queues);
    try std.testing.expectEqual(@as(?u16, 4), layout.first_poll_queue_index);

    const probe = try lab.captureProbeSnapshot(.{
        .num_queues = 4,
        .requested_poll_queues = 2,
        .seg_max = 128,
        .cmd_per_lun = 64,
        .max_target = 255,
        .max_lun = 32,
        .max_sectors = 1024,
    });
    try std.testing.expectEqual(@as(u16, 4), probe.config_num_queues);
    try std.testing.expectEqual(@as(u32, 128), probe.config_seg_max);
    try std.testing.expectEqual(@as(u16, 2), probe.default_queue_count);
    try std.testing.expectEqual(@as(u16, 2), probe.poll_queue_count);
    try std.testing.expectEqual(@as(?u16, 4), probe.first_poll_queue_index);

    const host = try lab.captureHostLimitSummary(.{
        .probe = .{
            .num_queues = 4,
            .requested_poll_queues = 2,
            .seg_max = 128,
            .cmd_per_lun = 64,
            .max_target = 255,
            .max_lun = 32,
            .max_sectors = 1024,
        },
        .synthetic_can_queue = 16,
    });
    try std.testing.expectEqualStrings(descriptor.anchor, host.anchor);
    try std.testing.expectEqual(@as(u32, 16), host.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 16), host.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u16, 4), host.nr_hw_queues);

    const depth = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 4,
                .requested_poll_queues = 2,
                .cmd_per_lun = 64,
            },
            .synthetic_can_queue = 16,
        },
        .requested_depth = 10,
    });
    try std.testing.expectEqual(@as(u32, 10), depth.clamped_queue_depth);
    try std.testing.expect(depth.tracks_queue_depth);
    try std.testing.expect(depth.uses_change_queue_depth);

    const command_buffers = try lab.captureCommandBufferOwnershipSummary(.{
        .queue_depth = .{
            .host_limit = .{
                .probe = .{
                    .num_queues = 4,
                    .requested_poll_queues = 2,
                    .cmd_per_lun = 64,
                    .max_target = 255,
                    .max_lun = 32,
                    .max_sectors = 1024,
                },
                .synthetic_can_queue = 16,
            },
            .requested_depth = 10,
        },
        .command_bytes = 48,
        .sense_bytes = 96,
    });
    try std.testing.expectEqualStrings(descriptor.anchor, command_buffers.anchor);
    try std.testing.expectEqual(@as(u32, 10), command_buffers.clamped_queue_depth);
    try std.testing.expectEqual(@as(u32, 48), command_buffers.command_bytes_per_request);
    try std.testing.expectEqual(@as(u32, 96), command_buffers.sense_bytes_per_request);
    try std.testing.expectEqual(@as(u64, 480), command_buffers.total_command_bytes);
    try std.testing.expectEqual(@as(u64, 960), command_buffers.total_sense_bytes);
    try std.testing.expect(command_buffers.owns_one_command_buffer_per_request);
    try std.testing.expect(command_buffers.owns_one_sense_buffer_per_request);
    try std.testing.expect(command_buffers.requires_dma_mapping_later);
    try std.testing.expect(command_buffers.preserves_pre_registration_scope);

    const control_path = try lab.captureControlPathGovernanceSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 4,
                        .requested_poll_queues = 2,
                        .cmd_per_lun = 64,
                        .max_target = 255,
                        .max_lun = 32,
                        .max_sectors = 1024,
                    },
                    .synthetic_can_queue = 16,
                },
                .requested_depth = 10,
            },
            .command_bytes = 48,
            .sense_bytes = 96,
        },
    });
    try std.testing.expectEqual(@as(u16, virtio_scsi.control_queue_index), control_path.control_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), control_path.event_queue_index);
    try std.testing.expect(control_path.control_queue_is_dedicated);
    try std.testing.expect(control_path.control_path_requires_control_queue_before_tmf);
    try std.testing.expect(control_path.control_path_uses_event_queue_for_async_notifications);
    try std.testing.expect(control_path.control_path_requires_dma_mapping_later);
    try std.testing.expect(control_path.control_path_blocks_while_transport_frozen);
    try std.testing.expect(control_path.stays_pre_runtime_only);

    const request_queue = try lab.requestQueue(3);
    try std.testing.expectEqual(@as(u16, 3), request_queue.local_index);
    try std.testing.expectEqual(@as(u16, 5), request_queue.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, request_queue.kind);

    const submit = try lab.captureRequestSubmitSequencingSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 4,
                        .requested_poll_queues = 2,
                        .cmd_per_lun = 64,
                        .max_target = 255,
                        .max_lun = 32,
                        .max_sectors = 1024,
                    },
                    .synthetic_can_queue = 16,
                },
                .requested_depth = 10,
            },
            .command_bytes = 48,
            .sense_bytes = 96,
        },
        .queue_local_index = 3,
    });
    try std.testing.expectEqual(@as(u16, 5), submit.queue_global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, submit.queue_kind);
    try std.testing.expectEqual(@as(u32, 48), submit.command_bytes_per_request);
    try std.testing.expectEqual(@as(u32, 96), submit.sense_bytes_per_request);
    try std.testing.expect(submit.submission_uses_preallocated_buffers);
    try std.testing.expect(submit.submission_requires_queue_selection);
    try std.testing.expect(submit.submission_requires_dma_mapping_before_kick);
    try std.testing.expect(submit.submission_requires_kick_after_descriptors_ready);
    try std.testing.expect(submit.submission_blocks_while_transport_frozen);
    try std.testing.expect(submit.stays_pre_runtime_only);

    const handback = try lab.captureCompletionHandbackSummary(.{
        .ownership = .{
            .queue_depth = .{
                .host_limit = .{
                    .probe = .{
                        .num_queues = 4,
                        .requested_poll_queues = 2,
                        .cmd_per_lun = 64,
                        .max_target = 255,
                        .max_lun = 32,
                        .max_sectors = 1024,
                    },
                    .synthetic_can_queue = 16,
                },
                .requested_depth = 10,
            },
            .command_bytes = 48,
            .sense_bytes = 96,
        },
        .queue_local_index = 3,
    });
    try std.testing.expectEqual(@as(u16, 5), handback.queue_global_index);
    try std.testing.expectEqual(@as(u32, 48), handback.command_bytes_per_request);
    try std.testing.expectEqual(@as(u32, 96), handback.sense_bytes_per_request);
    try std.testing.expect(handback.completion_requires_used_ring_before_handback);
    try std.testing.expect(handback.completion_reads_sense_before_recycle);
    try std.testing.expect(handback.completion_returns_command_buffer_after_handback);
    try std.testing.expect(handback.completion_returns_sense_buffer_after_handback);

    const mapping = try lab.captureIoQueueMapSummary(4, 2);
    try std.testing.expectEqual(@as(u16, 3), mapping.nr_maps);
    try std.testing.expectEqual(@as(u16, 2), mapping.default_queue_count);
    try std.testing.expectEqual(@as(u16, 2), mapping.poll_queue_count);
    try std.testing.expect(mapping.default_queues_use_virtio_affinity);
    try std.testing.expect(mapping.poll_queues_use_blk_mq_mapping);
}

test "phase12 virtio scsi syntax lab keeps transport-reset recovery exports reachable" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 4,
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

    const freeze = try lab.freezeForTransportReset();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", freeze.anchor);
    try std.testing.expectEqual(virtio_scsi.RecoveryAction.freeze, freeze.action);
    try std.testing.expect(!freeze.was_frozen);
    try std.testing.expect(freeze.is_frozen);
    try std.testing.expectEqual(@as(u16, 4), freeze.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), freeze.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), freeze.remembered_event_buffer_count);

    const plan = try lab.recoveryQueuePlan();
    try std.testing.expectEqual(@as(u16, 4), plan.request_queues);
    try std.testing.expectEqual(@as(u16, 2), plan.default_queues);
    try std.testing.expectEqual(@as(u16, 2), plan.poll_queues);
    try std.testing.expectEqual(@as(u16, 6), plan.total_queues);
    try std.testing.expectEqual(@as(?u16, 4), plan.first_poll_queue_index);
    try std.testing.expect(plan.requires_control_queue_restore);
    try std.testing.expect(plan.requires_event_queue_refill);
    try std.testing.expect(plan.requires_request_queue_restore);

    const depth = try lab.recoveryQueueDepthSummary();
    try std.testing.expectEqual(@as(u32, 11), depth.requested_depth);
    try std.testing.expectEqual(@as(u32, 7), depth.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 7), depth.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 7), depth.clamped_queue_depth);
    try std.testing.expect(depth.tracks_queue_depth);
    try std.testing.expect(depth.requires_change_queue_depth_restore);

    const mapping = try lab.recoveryIoQueueMapSummary();
    try std.testing.expectEqual(@as(u16, 3), mapping.nr_maps);
    try std.testing.expectEqual(@as(u16, 2), mapping.default_queue_count);
    try std.testing.expectEqual(@as(u16, 2), mapping.poll_queue_count);
    try std.testing.expect(mapping.requires_blk_mq_map_restore);
    try std.testing.expect(mapping.requires_virtio_affinity_restore);
    try std.testing.expect(mapping.requires_poll_map_restore);

    const ownership = try lab.recoveryEventBufferOwnershipSummary();
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), ownership.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), ownership.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 4), ownership.request_queue_count);
    try std.testing.expectEqual(@as(u16, 2), ownership.poll_queue_count);
    try std.testing.expect(ownership.event_buffers_reserved_for_event_queue);
    try std.testing.expect(!ownership.request_queues_can_borrow_event_buffers);
    try std.testing.expect(ownership.requires_device_ready_before_event_rearm);
    try std.testing.expect(ownership.requires_event_rearm_before_request_queue_reuse);

    const host_scan = try lab.recoveryHostScanSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", host_scan.anchor);
    try std.testing.expectEqual(@as(u16, 4), host_scan.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), host_scan.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), host_scan.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 0), host_scan.recovery_generation);
    try std.testing.expect(host_scan.requires_control_queue_restore_before_scan);
    try std.testing.expect(host_scan.requires_event_rearm_before_scan);
    try std.testing.expect(host_scan.requires_request_queue_restore_before_scan);
    try std.testing.expect(host_scan.requires_async_scan_resume);

    const restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(virtio_scsi.RecoveryAction.restore, restore.action);
    try std.testing.expect(restore.was_frozen);
    try std.testing.expect(!restore.is_frozen);
    try std.testing.expect(restore.request_planning_available);
    try std.testing.expect(restore.event_recycling_enabled);
    try std.testing.expectEqual(@as(u16, 1), restore.recovery_generation);

    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueuePlan());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryIoQueueMapSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueueDepthSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventBufferOwnershipSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryHostScanSummary());
}
