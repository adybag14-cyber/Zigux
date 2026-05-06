const std = @import("std");
const hvc_console = @import("hvc_console");

test "phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(5);
    _ = console.instantiate(0x55);

    const final_cleanup = try console.summarizeCleanupHandoff(.{});
    try std.testing.expectEqual(@as(usize, 5), final_cleanup.slot_index);
    try std.testing.expectEqual(@as(u32, 0x55), final_cleanup.vtermno);
    try std.testing.expect(final_cleanup.adapter_present);
    try std.testing.expect(!final_cleanup.close_skipped);
    try std.testing.expect(final_cleanup.final_close);
    try std.testing.expect(final_cleanup.tty_port_reference_live);
    try std.testing.expect(final_cleanup.tty_port_put_requested);
    try std.testing.expect(final_cleanup.drops_tty_port_reference);
    try std.testing.expect(final_cleanup.deferred_final_release);

    const hangup_cleanup = try console.summarizeCleanupHandoff(.{
        .hung_up = true,
    });
    try std.testing.expect(hangup_cleanup.close_skipped);
    try std.testing.expect(!hangup_cleanup.final_close);
    try std.testing.expect(hangup_cleanup.tty_port_reference_live);
    try std.testing.expect(hangup_cleanup.tty_port_put_requested);
    try std.testing.expect(hangup_cleanup.drops_tty_port_reference);
    try std.testing.expect(hangup_cleanup.deferred_final_release);

    try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, console.summarizeCleanupHandoff(.{
        .final_close = false,
    }));
    try std.testing.expectError(error.CleanupRequiresTtyPortReference, console.summarizeCleanupHandoff(.{
        .tty_port_reference_live = false,
    }));
    try std.testing.expectError(error.CleanupRequiresTtyPortReference, console.summarizeCleanupHandoff(.{
        .hung_up = true,
        .tty_port_reference_live = false,
    }));

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeCleanupHandoff(.{}));
}