const std = @import("std");

pub const default_anchor = "drivers/net/virtio_net.c";

pub const QueueResumeCheckpoint = enum {
    after_transmit_queue_restore,
    after_receive_refill,
    after_control_queue_restore,
};

pub const QueueResumeScope = enum {
    data_queues_only,
    data_and_refill,
    data_and_control,
    data_control_and_probe_replay,
};

pub const QueueResumeDisposition = enum {
    resume_after_transmit_restore,
    resume_after_receive_refill,
    resume_after_control_restore,
};

pub const QueueResumeRequest = struct {
    effective_queue_pairs: u16,
    receive_queue_count: u16,
    transmit_queue_count: u16,
    first_control_queue_index: ?u16 = null,
    total_queue_count: u16,
    rss_enabled: bool = false,
    requires_receive_queue_restore: bool = true,
    requires_transmit_queue_restore: bool = true,
    requires_control_queue_restore: bool = false,
    requires_receive_buffer_refill: bool = false,
    requires_mergeable_buffer_refill: bool = false,
    requires_post_reset_probe_replay: bool = false,
    post_reset_probe_replay_checkpoint: QueueResumeCheckpoint = .after_transmit_queue_restore,
    requires_receive_mode_sync: bool = false,
    requires_hash_report_restore: bool = false,
    requires_mac_table_sync: bool = false,
    requires_vlan_filter_sync: bool = false,
    requires_rss_config_sync: bool = false,
};

pub const QueueResumeSummary = struct {
    anchor: []const u8,
    effective_queue_pairs: u16,
    total_queue_count: u16,
    control_queue_index: ?u16,
    checkpoint: QueueResumeCheckpoint,
    scope: QueueResumeScope,
    disposition: QueueResumeDisposition,
    requires_receive_queue_restore: bool,
    requires_transmit_queue_restore: bool,
    requires_control_queue_restore: bool,
    requires_receive_buffer_refill: bool,
    requires_mergeable_buffer_refill: bool,
    requires_fresh_probe_snapshot: bool,
    restores_receive_mode: bool,
    restores_hash_report: bool,
    restores_mac_table: bool,
    restores_vlan_filters: bool,
    restores_rss_config: bool,
    throughput_guard_active: bool,
};

pub fn summarizeQueueResume(request: QueueResumeRequest) !QueueResumeSummary {
    if (request.effective_queue_pairs == 0) return error.InvalidQueuePairs;
    if (request.receive_queue_count == 0 and request.transmit_queue_count == 0) {
        return error.InvalidQueueCounts;
    }
    if (request.receive_queue_count != request.effective_queue_pairs or
        request.transmit_queue_count != request.effective_queue_pairs)
    {
        return error.QueueCountMismatch;
    }

    const data_queue_count = try checkedAddU16(
        request.receive_queue_count,
        request.transmit_queue_count,
    );
    const control_queue_count: u16 = if (request.first_control_queue_index == null) 0 else 1;
    if (request.first_control_queue_index) |control_queue_index| {
        if (control_queue_index != data_queue_count) {
            return error.ControlQueueIndexMismatch;
        }
    }
    const expected_total_queue_count = try checkedAddU16(
        data_queue_count,
        control_queue_count,
    );
    if (request.total_queue_count != expected_total_queue_count) {
        return error.TotalQueueCountMismatch;
    }
    if (request.requires_control_queue_restore and request.first_control_queue_index == null) {
        return error.ControlQueueIndexRequired;
    }

    const requires_control_state_restore = request.requires_receive_mode_sync or
        request.requires_hash_report_restore or
        request.requires_mac_table_sync or
        request.requires_vlan_filter_sync or
        request.requires_rss_config_sync;
    if (requires_control_state_restore and !request.requires_control_queue_restore) {
        return error.ControlStateRestoreRequiresControlQueue;
    }
    if (!request.rss_enabled and request.requires_rss_config_sync) {
        return error.RssConfigSyncWithoutRss;
    }
    if (request.requires_mergeable_buffer_refill and !request.requires_receive_buffer_refill) {
        return error.MergeableRefillRequiresReceiveRefill;
    }
    if (!request.requires_post_reset_probe_replay and request.requires_mergeable_buffer_refill) {
        return error.MergeableRefillRequiresReplay;
    }
    if (request.requires_post_reset_probe_replay) {
        switch (request.post_reset_probe_replay_checkpoint) {
            .after_transmit_queue_restore => return error.ProbeReplayCheckpointTooEarly,
            .after_receive_refill => {
                if (!request.requires_receive_buffer_refill) {
                    return error.ReceiveRefillCheckpointWithoutRefill;
                }
            },
            .after_control_queue_restore => {},
        }
    }

    const checkpoint: QueueResumeCheckpoint = if (request.requires_post_reset_probe_replay)
        request.post_reset_probe_replay_checkpoint
    else if (request.requires_control_queue_restore)
        .after_control_queue_restore
    else if (request.requires_receive_buffer_refill)
        .after_receive_refill
    else
        .after_transmit_queue_restore;

    const scope: QueueResumeScope = switch (checkpoint) {
        .after_transmit_queue_restore => .data_queues_only,
        .after_receive_refill => .data_and_refill,
        .after_control_queue_restore => if (request.requires_post_reset_probe_replay or
            request.requires_rss_config_sync or request.rss_enabled)
            .data_control_and_probe_replay
        else
            .data_and_control,
    };

    const disposition: QueueResumeDisposition = switch (checkpoint) {
        .after_transmit_queue_restore => .resume_after_transmit_restore,
        .after_receive_refill => .resume_after_receive_refill,
        .after_control_queue_restore => .resume_after_control_restore,
    };

    return .{
        .anchor = default_anchor,
        .effective_queue_pairs = request.effective_queue_pairs,
        .total_queue_count = request.total_queue_count,
        .control_queue_index = request.first_control_queue_index,
        .checkpoint = checkpoint,
        .scope = scope,
        .disposition = disposition,
        .requires_receive_queue_restore = request.requires_receive_queue_restore,
        .requires_transmit_queue_restore = request.requires_transmit_queue_restore,
        .requires_control_queue_restore = request.requires_control_queue_restore,
        .requires_receive_buffer_refill = request.requires_receive_buffer_refill,
        .requires_mergeable_buffer_refill = request.requires_mergeable_buffer_refill,
        .requires_fresh_probe_snapshot = request.requires_post_reset_probe_replay,
        .restores_receive_mode = request.requires_receive_mode_sync,
        .restores_hash_report = request.requires_hash_report_restore,
        .restores_mac_table = request.requires_mac_table_sync,
        .restores_vlan_filters = request.requires_vlan_filter_sync,
        .restores_rss_config = request.requires_rss_config_sync,
        .throughput_guard_active = checkpoint != .after_transmit_queue_restore or
            request.requires_post_reset_probe_replay,
    };
}

test "summarizeQueueResume keeps plain data-queue restore resumable after transmit restore" {
    const summary = try summarizeQueueResume(.{
        .effective_queue_pairs = 1,
        .receive_queue_count = 1,
        .transmit_queue_count = 1,
        .total_queue_count = 2,
        .requires_control_queue_restore = false,
        .requires_receive_buffer_refill = false,
        .requires_post_reset_probe_replay = false,
    });

    try std.testing.expectEqualStrings(default_anchor, summary.anchor);
    try std.testing.expectEqual(QueueResumeCheckpoint.after_transmit_queue_restore, summary.checkpoint);
    try std.testing.expectEqual(QueueResumeScope.data_queues_only, summary.scope);
    try std.testing.expectEqual(QueueResumeDisposition.resume_after_transmit_restore, summary.disposition);
    try std.testing.expect(!summary.requires_control_queue_restore);
    try std.testing.expect(!summary.requires_fresh_probe_snapshot);
    try std.testing.expect(!summary.throughput_guard_active);
}

test "summarizeQueueResume keeps mergeable refill gated before probe replay" {
    const summary = try summarizeQueueResume(.{
        .effective_queue_pairs = 1,
        .receive_queue_count = 1,
        .transmit_queue_count = 1,
        .total_queue_count = 2,
        .requires_receive_buffer_refill = true,
        .requires_mergeable_buffer_refill = true,
        .requires_post_reset_probe_replay = true,
        .post_reset_probe_replay_checkpoint = .after_receive_refill,
    });

    try std.testing.expectEqual(QueueResumeCheckpoint.after_receive_refill, summary.checkpoint);
    try std.testing.expectEqual(QueueResumeScope.data_and_refill, summary.scope);
    try std.testing.expectEqual(QueueResumeDisposition.resume_after_receive_refill, summary.disposition);
    try std.testing.expect(summary.requires_receive_buffer_refill);
    try std.testing.expect(summary.requires_mergeable_buffer_refill);
    try std.testing.expect(summary.requires_fresh_probe_snapshot);
    try std.testing.expect(summary.throughput_guard_active);
}

test "summarizeQueueResume keeps control-only restore gating throughput before resume" {
    const summary = try summarizeQueueResume(.{
        .effective_queue_pairs = 2,
        .receive_queue_count = 2,
        .transmit_queue_count = 2,
        .first_control_queue_index = 4,
        .total_queue_count = 5,
        .requires_control_queue_restore = true,
        .requires_receive_mode_sync = true,
        .requires_hash_report_restore = true,
    });

    try std.testing.expectEqual(QueueResumeCheckpoint.after_control_queue_restore, summary.checkpoint);
    try std.testing.expectEqual(QueueResumeScope.data_and_control, summary.scope);
    try std.testing.expectEqual(QueueResumeDisposition.resume_after_control_restore, summary.disposition);
    try std.testing.expect(summary.requires_control_queue_restore);
    try std.testing.expect(summary.restores_receive_mode);
    try std.testing.expect(summary.restores_hash_report);
    try std.testing.expect(!summary.requires_fresh_probe_snapshot);
    try std.testing.expect(summary.throughput_guard_active);
}

test "summarizeQueueResume keeps control and rss replay visible before resume" {
    const summary = try summarizeQueueResume(.{
        .effective_queue_pairs = 4,
        .receive_queue_count = 4,
        .transmit_queue_count = 4,
        .first_control_queue_index = 8,
        .total_queue_count = 9,
        .rss_enabled = true,
        .requires_control_queue_restore = true,
        .requires_post_reset_probe_replay = true,
        .post_reset_probe_replay_checkpoint = .after_control_queue_restore,
        .requires_receive_mode_sync = true,
        .requires_hash_report_restore = true,
        .requires_mac_table_sync = true,
        .requires_vlan_filter_sync = true,
        .requires_rss_config_sync = true,
    });

    try std.testing.expectEqual(QueueResumeCheckpoint.after_control_queue_restore, summary.checkpoint);
    try std.testing.expectEqual(QueueResumeScope.data_control_and_probe_replay, summary.scope);
    try std.testing.expectEqual(QueueResumeDisposition.resume_after_control_restore, summary.disposition);
    try std.testing.expectEqual(@as(?u16, 8), summary.control_queue_index);
    try std.testing.expect(summary.requires_control_queue_restore);
    try std.testing.expect(summary.restores_receive_mode);
    try std.testing.expect(summary.restores_hash_report);
    try std.testing.expect(summary.restores_mac_table);
    try std.testing.expect(summary.restores_vlan_filters);
    try std.testing.expect(summary.restores_rss_config);
    try std.testing.expect(summary.requires_fresh_probe_snapshot);
    try std.testing.expect(summary.throughput_guard_active);
}

test "summarizeQueueResume rejects queue counts that drift away from the negotiated pairs" {
    try std.testing.expectError(error.QueueCountMismatch, summarizeQueueResume(.{
        .effective_queue_pairs = 2,
        .receive_queue_count = 1,
        .transmit_queue_count = 2,
        .total_queue_count = 3,
    }));
}

test "summarizeQueueResume rejects control queue placement that does not start after the data queues" {
    try std.testing.expectError(error.ControlQueueIndexMismatch, summarizeQueueResume(.{
        .effective_queue_pairs = 2,
        .receive_queue_count = 2,
        .transmit_queue_count = 2,
        .first_control_queue_index = 5,
        .total_queue_count = 5,
        .requires_control_queue_restore = true,
    }));
}

test "summarizeQueueResume rejects control restore without an index" {
    try std.testing.expectError(error.ControlQueueIndexRequired, summarizeQueueResume(.{
        .effective_queue_pairs = 2,
        .receive_queue_count = 2,
        .transmit_queue_count = 2,
        .total_queue_count = 4,
        .requires_control_queue_restore = true,
    }));
}

test "summarizeQueueResume rejects control-state sync without control restore" {
    try std.testing.expectError(error.ControlStateRestoreRequiresControlQueue, summarizeQueueResume(.{
        .effective_queue_pairs = 2,
        .receive_queue_count = 2,
        .transmit_queue_count = 2,
        .total_queue_count = 4,
        .requires_receive_mode_sync = true,
    }));
}

test "summarizeQueueResume rejects rss config replay without rss negotiation" {
    try std.testing.expectError(error.RssConfigSyncWithoutRss, summarizeQueueResume(.{
        .effective_queue_pairs = 2,
        .receive_queue_count = 2,
        .transmit_queue_count = 2,
        .first_control_queue_index = 4,
        .total_queue_count = 5,
        .requires_control_queue_restore = true,
        .requires_rss_config_sync = true,
    }));
}

fn checkedAddU16(lhs: u16, rhs: u16) !u16 {
    const value = @as(u32, lhs) + rhs;
    return std.math.cast(u16, value) orelse error.QueueCountOverflow;
}
