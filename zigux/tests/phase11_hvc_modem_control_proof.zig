const std = @import("std");
const hvc_console = @import("../../drivers/tty/hvc/hvc_console.zig");

test "phase11 hvc console keeps full modem control callback surfaces reviewable" {
    const summary = hvc_console.summarizeModemControlHandoff(.{
        .tiocmget_available = true,
        .tiocmset_available = true,
        .dtr_rts_available = true,
        .set_mask_requested = true,
        .clear_mask_requested = true,
        .dtr_rts_asserted = true,
    });

    try std.testing.expect(summary.get_surface_visible);
    try std.testing.expect(summary.set_surface_visible);
    try std.testing.expect(summary.dtr_rts_surface_visible);
    try std.testing.expect(summary.set_mask_requested);
    try std.testing.expect(summary.clear_mask_requested);
    try std.testing.expect(summary.dtr_rts_asserted);
    try std.testing.expect(summary.keeps_live_modem_control_execution_out_of_scope);
}

test "phase11 hvc console masks tiocmset requests when hv_ops exposes only tiocmget" {
    const summary = hvc_console.summarizeModemControlHandoff(.{
        .tiocmget_available = true,
        .tiocmset_available = false,
        .dtr_rts_available = false,
        .set_mask_requested = true,
        .clear_mask_requested = true,
        .dtr_rts_asserted = true,
    });

    try std.testing.expect(summary.get_surface_visible);
    try std.testing.expect(!summary.set_surface_visible);
    try std.testing.expect(!summary.dtr_rts_surface_visible);
    try std.testing.expect(!summary.set_mask_requested);
    try std.testing.expect(!summary.clear_mask_requested);
    try std.testing.expect(!summary.dtr_rts_asserted);
    try std.testing.expect(summary.keeps_live_modem_control_execution_out_of_scope);
}

test "phase11 hvc console keeps clear-only requests distinct from DTR assertion visibility" {
    const summary = hvc_console.summarizeModemControlHandoff(.{
        .tiocmget_available = false,
        .tiocmset_available = true,
        .dtr_rts_available = false,
        .set_mask_requested = false,
        .clear_mask_requested = true,
        .dtr_rts_asserted = true,
    });

    try std.testing.expect(!summary.get_surface_visible);
    try std.testing.expect(summary.set_surface_visible);
    try std.testing.expect(!summary.dtr_rts_surface_visible);
    try std.testing.expect(!summary.set_mask_requested);
    try std.testing.expect(summary.clear_mask_requested);
    try std.testing.expect(!summary.dtr_rts_asserted);
}

test "phase11 hvc console keeps hupcl teardown distinct from callback-backed modem control" {
    const teardown = hvc_console.summarizeCloseTeardown(.{
        .tty_detached = true,
        .hupcl = true,
        .notifier_owned = true,
        .resize_work_cancelled = true,
        .wait_until_sent_intent = true,
        .close_wait_ownership = true,
        .port_initialized_before_close = true,
    });
    const modem = hvc_console.summarizeModemControlHandoff(.{
        .tiocmget_available = true,
        .tiocmset_available = true,
        .dtr_rts_available = false,
        .set_mask_requested = true,
        .clear_mask_requested = false,
        .dtr_rts_asserted = true,
    });

    try std.testing.expect(teardown.dtr_rts_shutdown);
    try std.testing.expect(modem.get_surface_visible);
    try std.testing.expect(modem.set_surface_visible);
    try std.testing.expect(!modem.dtr_rts_surface_visible);
    try std.testing.expect(modem.set_mask_requested);
    try std.testing.expect(!modem.clear_mask_requested);
    try std.testing.expect(!modem.dtr_rts_asserted);
}
