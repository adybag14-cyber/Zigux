const std = @import("std");
const virtio_net = @import("virtio_net");

const ControlQueuePayloadPlan = struct {
    rss_config_payload_bytes: u16,
    requires_hash_report_payload: bool,
    requires_mergeable_buffer_refill: bool,
    requires_runtime_command_submission: bool,
};

const ControlQueueRecoveryPlan = struct {
    recovery_state: virtio_net.RecoveryState,
    queue_recovery_action: virtio_net.QueueRecoveryAction,
    planned_queue_pairs: u16,
    keeps_runtime_commands_out_of_scope: bool,
};

const RecoveryQueuePlan = struct {
    action: virtio_net.RecoveryAction,
    planned_queue_pairs_available: bool,
    remembered_rss_summary: virtio_net.RssSummary,
    remembered_recovery_state: virtio_net.RecoveryState,
    remembered_queue_recovery_action: virtio_net.QueueRecoveryAction,
    recovery_generation: u16,
};

fn planControlQueuePayloadShape(snapshot: virtio_net.ProbeSnapshot) ControlQueuePayloadPlan {
    const rss_config_payload_bytes: u16 = switch (snapshot.rss_summary) {
        .active => 128,
        .hash_report_only => 64,
        else => 0,
    };

    return .{
        .rss_config_payload_bytes = rss_config_payload_bytes,
        .requires_hash_report_payload = snapshot.uses_hash_report_header or snapshot.has_rss_hash_report,
        .requires_mergeable_buffer_refill = snapshot.mergeable_rx_buffers,
        .requires_runtime_command_submission = false,
    };
}

fn controlQueueRecoveryPlan(snapshot: virtio_net.ProbeSnapshot) ControlQueueRecoveryPlan {
    return .{
        .recovery_state = snapshot.recovery_state,
        .queue_recovery_action = snapshot.queue_recovery_action,
        .planned_queue_pairs = snapshot.planned_queue_pairs,
        .keeps_runtime_commands_out_of_scope = true,
    };
}

fn recoveryQueuePlan(summary: virtio_net.QueueRecoverySummary) RecoveryQueuePlan {
    return .{
        .action = summary.action,
        .planned_queue_pairs_available = summary.planned_queue_pairs_available,
        .remembered_rss_summary = summary.remembered_rss_summary,
        .remembered_recovery_state = summary.remembered_recovery_state,
        .remembered_queue_recovery_action = summary.remembered_queue_recovery_action,
        .recovery_generation = summary.recovery_generation,
    };
}

test "phase12 virtio net syntax lab keeps control queue payload shaping separate from runtime commands" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_hash_report,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_hash_report,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
    });

    const payload_shape = planControlQueuePayloadShape(snapshot);
    const recovery_plan = controlQueueRecoveryPlan(snapshot);

    try std.testing.expectEqual(virtio_net.HeaderShape.hash_report, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, 20), snapshot.hdr_len_bytes);
    try std.testing.expectEqual(virtio_net.RssSummary.hash_report_only, snapshot.rss_summary);
    try std.testing.expect(payload_shape.requires_hash_report_payload);
    try std.testing.expect(payload_shape.requires_mergeable_buffer_refill);
    try std.testing.expect(!payload_shape.requires_runtime_command_submission);
    try std.testing.expectEqual(@as(u16, 64), payload_shape.rss_config_payload_bytes);
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, recovery_plan.recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, recovery_plan.queue_recovery_action);
    try std.testing.expect(recovery_plan.keeps_runtime_commands_out_of_scope);
}

test "phase12 virtio net syntax lab keeps rss payload shaping aligned with tunnel-header recovery" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_rss,
        virtio_net.feature_hash_report,
        virtio_net.feature_version_1,
        virtio_net.feature_any_layout,
        virtio_net.feature_guest_udp_tunnel_gso,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
            virtio_net.feature_hash_report,
            virtio_net.feature_version_1,
            virtio_net.feature_any_layout,
            virtio_net.feature_guest_udp_tunnel_gso,
        },
        .requested_queue_pairs = 4,
        .max_queue_pairs = 4,
    });

    const payload_shape = planControlQueuePayloadShape(snapshot);
    const recovery_plan = controlQueueRecoveryPlan(snapshot);
    const header_scatter = try lab.summarizeHeaderScatterConstraint();
    const freeze_summary = try lab.freezeForRecovery();
    const restore_summary = try lab.restoreAfterRecovery();
    const freeze_plan = recoveryQueuePlan(freeze_summary);
    const restore_plan = recoveryQueuePlan(restore_summary);

    try std.testing.expectEqual(virtio_net.HeaderShape.hash_report_tunnel, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, 24), snapshot.hdr_len_bytes);
    try std.testing.expect(snapshot.uses_hash_report_header);
    try std.testing.expect(snapshot.uses_udp_tunnel_header);
    try std.testing.expectEqual(virtio_net.RssSummary.active, snapshot.rss_summary);
    try std.testing.expectEqual(@as(u16, 128), payload_shape.rss_config_payload_bytes);
    try std.testing.expect(payload_shape.requires_hash_report_payload);
    try std.testing.expect(!payload_shape.requires_mergeable_buffer_refill);
    try std.testing.expect(recovery_plan.keeps_runtime_commands_out_of_scope);
    try std.testing.expectEqual(virtio_net.HeaderScatterSource.version_1, header_scatter.header_scatter_source);
    try std.testing.expect(header_scatter.supports_split_header_sg);
    try std.testing.expectEqual(@as(u16, 24), header_scatter.needed_headroom_bytes);
    try std.testing.expectEqual(virtio_net.RecoveryAction.freeze, freeze_plan.action);
    try std.testing.expect(!freeze_plan.planned_queue_pairs_available);
    try std.testing.expectEqual(virtio_net.RecoveryAction.restore, restore_plan.action);
    try std.testing.expect(restore_plan.planned_queue_pairs_available);
    try std.testing.expectEqual(virtio_net.RssSummary.active, restore_plan.remembered_rss_summary);
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, restore_plan.remembered_recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, restore_plan.remembered_queue_recovery_action);
    try std.testing.expectEqual(@as(u16, 1), restore_plan.recovery_generation);
}

test "phase12 virtio net syntax lab keeps any-layout scatter separate from legacy linear headroom" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_any_layout,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_any_layout,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
    });

    const payload_shape = planControlQueuePayloadShape(snapshot);
    const header_scatter = try lab.summarizeHeaderScatterConstraint();

    try std.testing.expectEqual(virtio_net.HeaderShape.mrg_rxbuf, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, 12), snapshot.hdr_len_bytes);
    try std.testing.expectEqual(virtio_net.HeaderScatterSource.any_layout, header_scatter.header_scatter_source);
    try std.testing.expect(header_scatter.supports_split_header_sg);
    try std.testing.expectEqual(@as(u16, 12), header_scatter.needed_headroom_bytes);
    try std.testing.expectEqual(@as(u16, 0), payload_shape.rss_config_payload_bytes);
    try std.testing.expect(!payload_shape.requires_hash_report_payload);
    try std.testing.expect(payload_shape.requires_mergeable_buffer_refill);
}