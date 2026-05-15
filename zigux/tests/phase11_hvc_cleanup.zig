const std = @import("std");
const hvc_console = @import("hvc_console");

const console = struct {
    pub const CleanupRequest = struct {
        final_close: bool,
        hangup_seen: bool,
        tty_port_release_handoff: bool,
        cleanup_time_tty_port_ownership: bool,
        port_reference_drop_timing: bool,
    };

    pub const CleanupTrigger = enum {
        final_close_only,
        hangup_only,
        final_close_and_hangup,
    };

    pub const CleanupSummary = struct {
        cleanup: hvc_console.CleanupHandoffSummary,
        drops_tty_port_reference: bool,
        hangup_cleanup_boundary: bool,
        trigger: CleanupTrigger,
    };

    pub fn summarizeCleanupHandoff(request: CleanupRequest) !CleanupSummary {
        if (!request.final_close and !request.hangup_seen) {
            return error.CleanupRequiresFinalCloseOrHangup;
        }

        const cleanup = hvc_console.summarizeCleanupHandoff(.{
            .tty_port_release_handoff = request.tty_port_release_handoff,
            .cleanup_time_tty_port_ownership = request.cleanup_time_tty_port_ownership,
            .port_reference_drop_timing = request.port_reference_drop_timing,
        });
        const trigger: CleanupTrigger = if (request.final_close and request.hangup_seen)
            .final_close_and_hangup
        else if (request.final_close)
            .final_close_only
        else
            .hangup_only;

        return .{
            .cleanup = cleanup,
            .drops_tty_port_reference = cleanup.port_reference_drop_timing,
            .hangup_cleanup_boundary = request.hangup_seen,
            .trigger = trigger,
        };
    }
};

test "phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable" {
    const hangup_cleanup = try console.summarizeCleanupHandoff(.{
        .final_close = false,
        .hangup_seen = true,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });

    try std.testing.expect(hangup_cleanup.cleanup.tty_port_release_handoff);
    try std.testing.expect(hangup_cleanup.cleanup.cleanup_time_tty_port_ownership);
    try std.testing.expect(hangup_cleanup.drops_tty_port_reference);
    try std.testing.expect(hangup_cleanup.hangup_cleanup_boundary);
    try std.testing.expectEqual(console.CleanupTrigger.hangup_only, hangup_cleanup.trigger);

    try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, console.summarizeCleanupHandoff(.{
        .final_close = false,
        .hangup_seen = false,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    }));
}

test "phase11 hvc console keeps final-close cleanup distinct from hangup cleanup" {
    const final_close_cleanup = try console.summarizeCleanupHandoff(.{
        .final_close = true,
        .hangup_seen = false,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = false,
    });

    try std.testing.expect(final_close_cleanup.cleanup.tty_port_release_handoff);
    try std.testing.expect(final_close_cleanup.cleanup.cleanup_time_tty_port_ownership);
    try std.testing.expect(!final_close_cleanup.drops_tty_port_reference);
    try std.testing.expect(!final_close_cleanup.hangup_cleanup_boundary);
    try std.testing.expectEqual(console.CleanupTrigger.final_close_only, final_close_cleanup.trigger);
}

test "phase11 hvc console keeps combined cleanup trigger explicit" {
    const combined_cleanup = try console.summarizeCleanupHandoff(.{
        .final_close = true,
        .hangup_seen = true,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });

    try std.testing.expect(combined_cleanup.cleanup.tty_port_release_handoff);
    try std.testing.expect(combined_cleanup.cleanup.cleanup_time_tty_port_ownership);
    try std.testing.expect(combined_cleanup.drops_tty_port_reference);
    try std.testing.expect(combined_cleanup.hangup_cleanup_boundary);
    try std.testing.expectEqual(
        console.CleanupTrigger.final_close_and_hangup,
        combined_cleanup.trigger,
    );
}
