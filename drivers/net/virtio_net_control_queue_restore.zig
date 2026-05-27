const std = @import("std");

pub const ControlQueueRestoreBlocker = enum {
    none,
    queue_absent_after_restore,
    queue_enable,
    command_replay,
};

pub const ControlQueueRestoreRequest = struct {
    reset_generation: u32,
    receive_queue_pairs_after_restore: u16,
    control_queue_present_before_reset: bool = true,
    control_queue_present_after_restore: bool,
    control_queue_enabled_after_restore: bool,
    control_commands_before_reset: u16 = 0,
    control_commands_replayed_after_restore: u16 = 0,
};

pub const ControlQueueRestoreSummary = struct {
    anchor: []const u8,
    reset_generation: u32,
    receive_queue_pairs_after_restore: u16,
    control_queue_present_before_reset: bool,
    control_queue_present_after_restore: bool,
    control_queue_enabled_after_restore: bool,
    control_commands_before_reset: u16,
    control_commands_replayed_after_restore: u16,
    missing_control_commands_after_restore: u16,
    requires_control_queue_restore: bool,
    queue_present_after_restore: bool,
    queue_enabled_after_restore_ready: bool,
    commands_replayed: bool,
    blocker: ControlQueueRestoreBlocker,
    control_queue_restored: bool,
};

pub fn summarizeControlQueueRestore(
    request: ControlQueueRestoreRequest,
) !ControlQueueRestoreSummary {
    if (request.receive_queue_pairs_after_restore == 0) {
        return error.ReceiveQueuePairsMissing;
    }
    if (request.control_commands_replayed_after_restore > request.control_commands_before_reset) {
        return error.ControlCommandReplayOverflow;
    }

    const requires_control_queue_restore = request.control_queue_present_before_reset;
    const queue_present_after_restore =
        !requires_control_queue_restore or request.control_queue_present_after_restore;
    const queue_enabled_after_restore_ready =
        !requires_control_queue_restore or request.control_queue_enabled_after_restore;
    const missing_control_commands_after_restore =
        request.control_commands_before_reset - request.control_commands_replayed_after_restore;
    const commands_replayed =
        !requires_control_queue_restore or missing_control_commands_after_restore == 0;

    const blocker: ControlQueueRestoreBlocker = blk: {
        if (!queue_present_after_restore) break :blk .queue_absent_after_restore;
        if (!queue_enabled_after_restore_ready) break :blk .queue_enable;
        if (!commands_replayed) break :blk .command_replay;
        break :blk .none;
    };

    return .{
        .anchor = "drivers/net/virtio_net.c",
        .reset_generation = request.reset_generation,
        .receive_queue_pairs_after_restore = request.receive_queue_pairs_after_restore,
        .control_queue_present_before_reset = request.control_queue_present_before_reset,
        .control_queue_present_after_restore = request.control_queue_present_after_restore,
        .control_queue_enabled_after_restore = request.control_queue_enabled_after_restore,
        .control_commands_before_reset = request.control_commands_before_reset,
        .control_commands_replayed_after_restore = request.control_commands_replayed_after_restore,
        .missing_control_commands_after_restore = missing_control_commands_after_restore,
        .requires_control_queue_restore = requires_control_queue_restore,
        .queue_present_after_restore = queue_present_after_restore,
        .queue_enabled_after_restore_ready = queue_enabled_after_restore_ready,
        .commands_replayed = commands_replayed,
        .blocker = blocker,
        .control_queue_restored = blocker == .none,
    };
}

test "control queue restore rejects missing receive queue pairs" {
    try std.testing.expectError(error.ReceiveQueuePairsMissing, summarizeControlQueueRestore(.{
        .reset_generation = 1,
        .receive_queue_pairs_after_restore = 0,
        .control_queue_present_after_restore = true,
        .control_queue_enabled_after_restore = true,
    }));
}

test "control queue restore rejects replay counts above the pre-reset command budget" {
    try std.testing.expectError(error.ControlCommandReplayOverflow, summarizeControlQueueRestore(.{
        .reset_generation = 1,
        .receive_queue_pairs_after_restore = 1,
        .control_queue_present_after_restore = true,
        .control_queue_enabled_after_restore = true,
        .control_commands_before_reset = 2,
        .control_commands_replayed_after_restore = 3,
    }));
}

test "control queue restore keeps queue presence explicit before later replay work" {
    const summary = try summarizeControlQueueRestore(.{
        .reset_generation = 2,
        .receive_queue_pairs_after_restore = 2,
        .control_queue_present_before_reset = true,
        .control_queue_present_after_restore = false,
        .control_queue_enabled_after_restore = false,
        .control_commands_before_reset = 2,
        .control_commands_replayed_after_restore = 0,
    });

    try std.testing.expectEqual(
        ControlQueueRestoreBlocker.queue_absent_after_restore,
        summary.blocker,
    );
    try std.testing.expect(summary.requires_control_queue_restore);
    try std.testing.expect(!summary.queue_present_after_restore);
    try std.testing.expect(!summary.control_queue_restored);
}

test "control queue restore keeps queue enable explicit after presence returns" {
    const summary = try summarizeControlQueueRestore(.{
        .reset_generation = 3,
        .receive_queue_pairs_after_restore = 2,
        .control_queue_present_before_reset = true,
        .control_queue_present_after_restore = true,
        .control_queue_enabled_after_restore = false,
        .control_commands_before_reset = 1,
        .control_commands_replayed_after_restore = 0,
    });

    try std.testing.expectEqual(ControlQueueRestoreBlocker.queue_enable, summary.blocker);
    try std.testing.expect(summary.queue_present_after_restore);
    try std.testing.expect(!summary.queue_enabled_after_restore_ready);
    try std.testing.expectEqual(@as(u16, 1), summary.missing_control_commands_after_restore);
    try std.testing.expect(!summary.control_queue_restored);
}

test "control queue restore keeps command replay explicit once the queue is live" {
    const summary = try summarizeControlQueueRestore(.{
        .reset_generation = 4,
        .receive_queue_pairs_after_restore = 4,
        .control_queue_present_before_reset = true,
        .control_queue_present_after_restore = true,
        .control_queue_enabled_after_restore = true,
        .control_commands_before_reset = 3,
        .control_commands_replayed_after_restore = 2,
    });

    try std.testing.expectEqual(ControlQueueRestoreBlocker.command_replay, summary.blocker);
    try std.testing.expect(summary.queue_present_after_restore);
    try std.testing.expect(summary.queue_enabled_after_restore_ready);
    try std.testing.expectEqual(@as(u16, 1), summary.missing_control_commands_after_restore);
    try std.testing.expect(!summary.commands_replayed);
    try std.testing.expect(!summary.control_queue_restored);
}

test "control queue restore skips the gate when no control queue was present before reset" {
    const summary = try summarizeControlQueueRestore(.{
        .reset_generation = 5,
        .receive_queue_pairs_after_restore = 1,
        .control_queue_present_before_reset = false,
        .control_queue_present_after_restore = false,
        .control_queue_enabled_after_restore = false,
    });

    try std.testing.expect(!summary.requires_control_queue_restore);
    try std.testing.expectEqual(ControlQueueRestoreBlocker.none, summary.blocker);
    try std.testing.expect(summary.control_queue_restored);
}

test "control queue restore clears once presence enablement and command replay all align" {
    const summary = try summarizeControlQueueRestore(.{
        .reset_generation = 6,
        .receive_queue_pairs_after_restore = 4,
        .control_queue_present_before_reset = true,
        .control_queue_present_after_restore = true,
        .control_queue_enabled_after_restore = true,
        .control_commands_before_reset = 3,
        .control_commands_replayed_after_restore = 3,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(ControlQueueRestoreBlocker.none, summary.blocker);
    try std.testing.expect(summary.control_queue_restored);
    try std.testing.expect(summary.commands_replayed);
    try std.testing.expectEqual(@as(u16, 0), summary.missing_control_commands_after_restore);
}
