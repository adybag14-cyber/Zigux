const std = @import("std");
const dw_wdt = @import("dw_wdt");

test "platform handoff stays blocked when drvdata publication is missing" {
    var watchdog = try dw_wdt.DwWdtLab.initCustomTops(1_000, false, [_]u32{
        20_000, 4_000,  8_000,  12_000,
        16_000, 24_000, 28_000, 32_000,
        36_000, 40_000, 44_000, 48_000,
        52_000, 56_000, 60_000, 64_000,
    });

    const handoff = try watchdog.platformHandoffSummary(.{
        .nowayout = true,
        .requested_timeout_sec = 11,
        .stop_on_reboot = true,
    }, true, false, false);

    try std.testing.expect(!handoff.registration_ready);
    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.blocked_missing_drvdata, handoff.registration_state);
    try std.testing.expect(!handoff.preserves_pretimeout_irq);
    try std.testing.expect(!handoff.drvdata_ready);
    try std.testing.expect(handoff.needs_timeout_programming);
}

test "platform handoff keeps timeout-programming registration state explicit when resources are ready" {
    var watchdog = try dw_wdt.DwWdtLab.initCustomTops(1_000, false, [_]u32{
        20_000, 4_000,  8_000,  12_000,
        16_000, 24_000, 28_000, 32_000,
        36_000, 40_000, 44_000, 48_000,
        52_000, 56_000, 60_000, 64_000,
    });

    const handoff = try watchdog.platformHandoffSummary(.{
        .nowayout = true,
        .requested_timeout_sec = 11,
        .stop_on_reboot = true,
    }, true, true, true);

    try std.testing.expectEqual(dw_wdt.TopSource.custom, handoff.top_source);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.default_selection, handoff.timeout_origin);
    try std.testing.expect(!handoff.reset_control_available);
    try std.testing.expect(handoff.irq_registration_ready);
    try std.testing.expect(handoff.drvdata_ready);
    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.program_timeout_then_register, handoff.registration_state);
    try std.testing.expect(handoff.registration_ready);
    try std.testing.expect(!handoff.preserves_pretimeout_irq);
    try std.testing.expect(handoff.nowayout);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, handoff.restart_priority);
    try std.testing.expect(handoff.stop_on_reboot);
    try std.testing.expect(!handoff.can_stop);
    try std.testing.expectEqual(@as(u32, 12), handoff.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), handoff.pretimeout_sec);
    try std.testing.expect(!handoff.imported_running_state);
    try std.testing.expect(handoff.needs_timeout_programming);
}

test "registration order summary keeps blocked registration explicit when drvdata is missing" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const summary = try watchdog.registrationOrderSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, true, true, false, true, false);

    try std.testing.expectEqualStrings("watchdog_register_device", summary.registration_call);
    try std.testing.expectEqual(dw_wdt.TimerClockPath.dedicated_tclk, summary.timer_clock_path);
    try std.testing.expect(summary.apb_clock_optional);
    try std.testing.expect(!summary.apb_clock_present);
    try std.testing.expect(summary.reset_control_available);
    try std.testing.expect(summary.irq_registration_ready);
    try std.testing.expect(!summary.drvdata_ready);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.imported_running_state, summary.timeout_origin);
    try std.testing.expect(!summary.timeout_programmed_before_register);
    try std.testing.expect(summary.imported_running_state_before_register);
    try std.testing.expect(summary.watchdog_info_supports_pretimeout);
    try std.testing.expect(!summary.register_device_requested);
    try std.testing.expect(summary.reset_deassert_precedes_timeout_init);
    try std.testing.expect(summary.timeout_init_precedes_drvdata);
    try std.testing.expect(summary.drvdata_precedes_restart_priority);
    try std.testing.expect(summary.restart_priority_precedes_stop_on_reboot);
    try std.testing.expect(summary.stop_on_reboot_precedes_register_device);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(summary.blocked_on_live_mmio);
}

test "platform registration scaffold summary keeps ready imported-state probe anchors explicit" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const summary = try watchdog.platformRegistrationScaffoldSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, true, true, true, true, true);

    try std.testing.expectEqualStrings("module_platform_driver", summary.platform_driver_anchor);
    try std.testing.expectEqualStrings("dw_wdt_drv_probe", summary.probe_anchor);
    try std.testing.expectEqualStrings("dw_wdt_drv_remove", summary.remove_anchor);
    try std.testing.expectEqualStrings("dw_wdt_drv_shutdown", summary.shutdown_anchor);
    try std.testing.expectEqualStrings("watchdog_register_device", summary.registration_call);
    try std.testing.expectEqualStrings("platform_set_drvdata", summary.drvdata_anchor);
    try std.testing.expectEqual(dw_wdt.TimerClockPath.dedicated_tclk, summary.timer_clock_path);
    try std.testing.expect(summary.apb_clock_optional);
    try std.testing.expect(summary.apb_clock_present);
    try std.testing.expect(summary.reset_control_available);
    try std.testing.expect(summary.irq_registration_ready);
    try std.testing.expect(summary.drvdata_ready);
    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.import_running_state_then_register, summary.registration_state);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.imported_running_state, summary.timeout_origin);
    try std.testing.expect(!summary.timeout_programmed_before_register);
    try std.testing.expect(summary.imported_running_state_before_register);
    try std.testing.expect(summary.watchdog_info_supports_pretimeout);
    try std.testing.expect(!summary.nowayout);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, summary.restart_priority);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.probe_path_reviewable);
    try std.testing.expect(summary.remove_path_reviewable);
    try std.testing.expect(summary.shutdown_path_reviewable);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(summary.blocked_on_live_mmio);
}

test "platform registration scaffold summary keeps blocked timeout-programming branch explicit" {
    var watchdog = try dw_wdt.DwWdtLab.initCustomTops(1_000, false, [_]u32{
        20_000, 4_000,  8_000,  12_000,
        16_000, 24_000, 28_000, 32_000,
        36_000, 40_000, 44_000, 48_000,
        52_000, 56_000, 60_000, 64_000,
    });

    const summary = try watchdog.platformRegistrationScaffoldSummary(.{
        .nowayout = true,
        .requested_timeout_sec = 11,
        .stop_on_reboot = true,
    }, true, false, false, false, false);

    try std.testing.expectEqualStrings("module_platform_driver", summary.platform_driver_anchor);
    try std.testing.expectEqual(dw_wdt.TimerClockPath.shared_clk_fallback, summary.timer_clock_path);
    try std.testing.expect(summary.apb_clock_optional);
    try std.testing.expect(!summary.apb_clock_present);
    try std.testing.expect(!summary.reset_control_available);
    try std.testing.expect(!summary.irq_registration_ready);
    try std.testing.expect(!summary.drvdata_ready);
    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.blocked_missing_drvdata, summary.registration_state);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.default_selection, summary.timeout_origin);
    try std.testing.expect(summary.timeout_programmed_before_register);
    try std.testing.expect(!summary.imported_running_state_before_register);
    try std.testing.expect(!summary.watchdog_info_supports_pretimeout);
    try std.testing.expect(summary.nowayout);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, summary.restart_priority);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expect(!summary.register_device_requested);
    try std.testing.expect(summary.probe_path_reviewable);
    try std.testing.expect(summary.remove_path_reviewable);
    try std.testing.expect(summary.shutdown_path_reviewable);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(summary.blocked_on_live_mmio);
}
