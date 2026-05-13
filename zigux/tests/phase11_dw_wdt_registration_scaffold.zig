const std = @import("std");

const dw_wdt = @import("dw_wdt");

test "platform handoff stays blocked when drvdata publication is missing" {
    const summary = dw_wdt.platformHandoffSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = false,
        .timeout_programmed = true,
        .imported_running = false,
    });

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", summary.anchor);
    try std.testing.expectEqual(
        dw_wdt.RegistrationScaffoldState.blocked_missing_drvdata,
        summary.state,
    );
    try std.testing.expect(summary.timer_clock_available);
    try std.testing.expect(!summary.timeout_programming_requested);
    try std.testing.expect(!summary.registration_ready);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "platform handoff keeps timeout-programming registration state explicit when resources are ready" {
    const summary = dw_wdt.platformHandoffSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = false,
        .drvdata_published = true,
        .timeout_programmed = true,
        .imported_running = false,
    });

    try std.testing.expectEqual(dw_wdt.TimerClockPath.named_tclk, summary.timer_clock_path);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.programmed_top_window, summary.probe_timeout_origin);
    try std.testing.expect(summary.apb_clock_present);
    try std.testing.expect(summary.reset_control_available);
    try std.testing.expect(summary.timeout_programming_requested);
    try std.testing.expect(summary.registration_ready);
    try std.testing.expect(summary.stop_on_reboot_requested);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, summary.restart_priority_value);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "registration order summary keeps blocked registration explicit when drvdata is missing" {
    const summary = dw_wdt.registrationOrderSummary(.{
        .drvdata_published = false,
        .timeout_programmed = true,
        .imported_running = true,
    });

    try std.testing.expectEqual(
        dw_wdt.RegistrationScaffoldState.blocked_missing_drvdata,
        summary.state,
    );
    try std.testing.expect(!summary.publishes_drvdata_before_register);
    try std.testing.expect(!summary.imports_running_state_before_register);
    try std.testing.expect(!summary.programs_timeout_before_register);
    try std.testing.expect(!summary.registration_requested);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "platform registration scaffold summary keeps ready imported-state probe anchors explicit" {
    const summary = dw_wdt.platformRegistrationScaffoldSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = true,
        .has_pclk = false,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = true,
    });

    try std.testing.expectEqual(
        dw_wdt.RegistrationScaffoldState.import_running_state_then_register,
        summary.state,
    );
    try std.testing.expectEqual(
        dw_wdt.TimerClockPath.unnamed_shared_fallback,
        summary.timer_clock_path,
    );
    try std.testing.expectEqual(
        dw_wdt.ProbeTimeoutOrigin.imported_running_counter,
        summary.probe_timeout_origin,
    );
    try std.testing.expect(summary.registration_requested);
    try std.testing.expect(summary.stop_on_reboot_requested);
    try std.testing.expect(summary.reset_release_ready);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "platform registration scaffold summary keeps blocked timeout-programming branch explicit" {
    const summary = dw_wdt.platformRegistrationScaffoldSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = false,
        .has_pretimeout_irq = false,
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = false,
    });

    try std.testing.expectEqual(
        dw_wdt.RegistrationScaffoldState.blocked_on_live_mmio,
        summary.state,
    );
    try std.testing.expectEqual(
        dw_wdt.ProbeTimeoutOrigin.blocked_on_live_mmio,
        summary.probe_timeout_origin,
    );
    try std.testing.expect(!summary.registration_requested);
    try std.testing.expect(!summary.stop_on_reboot_requested);
    try std.testing.expect(!summary.reset_release_ready);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(summary.blocked_on_live_mmio);
}
