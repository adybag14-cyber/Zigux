const std = @import("std");
const dw_wdt = @import("dw_wdt");

test "phase11 dw_wdt registration order summary keeps timeout-programming path explicit before registration" {
    var watchdog = try dw_wdt.DwWdtLab.initCustomTops(1_000, false, [_]u32{
        20_000, 4_000,  8_000,  12_000,
        16_000, 24_000, 28_000, 32_000,
        36_000, 40_000, 44_000, 48_000,
        52_000, 56_000, 60_000, 64_000,
    });

    const summary = try watchdog.registrationOrderSummary(.{
        .nowayout = true,
        .requested_timeout_sec = 11,
        .stop_on_reboot = true,
    }, true, false, true, false, false);

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", summary.anchor);
    try std.testing.expectEqualStrings("watchdog_register_device", summary.registration_call);
    try std.testing.expectEqualStrings("platform_set_drvdata", summary.drvdata_anchor);
    try std.testing.expectEqual(dw_wdt.TimerClockPath.shared_clk_fallback, summary.timer_clock_path);
    try std.testing.expect(summary.apb_clock_optional);
    try std.testing.expect(!summary.apb_clock_present);
    try std.testing.expect(!summary.reset_control_available);
    try std.testing.expect(!summary.irq_registration_ready);
    try std.testing.expect(summary.drvdata_ready);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.default_selection, summary.timeout_origin);
    try std.testing.expect(summary.timeout_programmed_before_register);
    try std.testing.expect(!summary.imported_running_state_before_register);
    try std.testing.expect(!summary.watchdog_info_supports_pretimeout);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, summary.restart_priority);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(!summary.reset_deassert_precedes_timeout_init);
    try std.testing.expect(summary.timeout_init_precedes_drvdata);
    try std.testing.expect(summary.drvdata_precedes_restart_priority);
    try std.testing.expect(summary.restart_priority_precedes_stop_on_reboot);
    try std.testing.expect(summary.stop_on_reboot_precedes_register_device);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt registration order summary keeps imported running state and pretimeout readiness explicit" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const summary = try watchdog.registrationOrderSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, true, true, true, true, true);

    try std.testing.expectEqual(dw_wdt.TimerClockPath.dedicated_tclk, summary.timer_clock_path);
    try std.testing.expect(summary.apb_clock_optional);
    try std.testing.expect(summary.apb_clock_present);
    try std.testing.expect(summary.reset_control_available);
    try std.testing.expect(summary.irq_registration_ready);
    try std.testing.expect(summary.drvdata_ready);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.imported_running_state, summary.timeout_origin);
    try std.testing.expect(!summary.timeout_programmed_before_register);
    try std.testing.expect(summary.imported_running_state_before_register);
    try std.testing.expect(summary.watchdog_info_supports_pretimeout);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, summary.restart_priority);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.reset_deassert_precedes_timeout_init);
    try std.testing.expect(summary.timeout_init_precedes_drvdata);
    try std.testing.expect(summary.drvdata_precedes_restart_priority);
    try std.testing.expect(summary.restart_priority_precedes_stop_on_reboot);
    try std.testing.expect(summary.stop_on_reboot_precedes_register_device);
}
