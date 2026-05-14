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

    pub const CleanupSummary = struct {
        cleanup: hvc_console.CleanupHandoffSummary,
        drops_tty_port_reference: bool,
        hangup_cleanup_boundary: bool,
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

        return .{
            .cleanup = cleanup,
            .drops_tty_port_reference = cleanup.port_reference_drop_timing,
            .hangup_cleanup_boundary = request.hangup_seen,
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

    try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, console.summarizeCleanupHandoff(.{
        .final_close = false,
        .hangup_seen = false,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    }));
}
