const std = @import("std");
const dw_wdt = @import("dw_wdt");

test "phase11 dw_wdt exposes the bounded descriptor and fixed-top limits" {
    const descriptor = dw_wdt.DwWdtLab.descriptor();
    try std.testing.expectEqualStrings("dw_wdt_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_simple_driver_starter);
    try std.testing.expect(!descriptor.touches_platform_registration);
    try std.testing.expect(!descriptor.touches_live_mmio);
    try std.testing.expect(!descriptor.touches_irq_registration);

    try std.testing.expectError(error.InvalidClockRate, dw_wdt.DwWdtLab.initFixedTops(0, false));

    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const config = watchdog.configSnapshot();
    try std.testing.expectEqual(dw_wdt.ResponseMode.reset, config.response_mode);
    try std.testing.expectEqual(@as(u32, 32), config.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), config.pretimeout_sec);
    try std.testing.expectEqual(@as(u32, 1), config.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, 32_768_000), config.max_hw_heartbeat_ms);
    try std.testing.expect(!config.can_stop);
}

test "phase11 dw_wdt exposes the fixed-top timeout matrix in ascending order" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(32_768, false);
    const windows = watchdog.timeoutWindows();

    try std.testing.expectEqual(@as(usize, dw_wdt.num_tops), windows.len);
    try std.testing.expectEqual(@as(u32, 0), windows[0].top_val);
    try std.testing.expectEqual(@as(u32, 2), windows[0].sec);
    try std.testing.expectEqual(@as(u32, 15), windows[15].top_val);
    try std.testing.expectEqual(@as(u32, 65_536), windows[15].sec);

    for (windows[1..], 1..) |window, idx| {
        const previous = windows[idx - 1];
        try std.testing.expect(window.sec >= previous.sec);
        if (window.sec == previous.sec) {
            try std.testing.expect(window.msec >= previous.msec);
        }
    }
}

test "phase11 dw_wdt probe summary reports fixed versus custom top sourcing" {
    const custom_tops = [_]u32{
        20_000, 4_000,  8_000,  12_000,
        16_000, 24_000, 28_000, 32_000,
        36_000, 40_000, 44_000, 48_000,
        52_000, 56_000, 60_000, 64_000,
    };

    var watchdog = try dw_wdt.DwWdtLab.initCustomTops(1_000, true, custom_tops);
    const windows = watchdog.timeoutWindows();
    try std.testing.expectEqual(@as(u32, 1), windows[0].top_val);
    try std.testing.expectEqual(@as(u32, 4), windows[0].sec);
    try std.testing.expectEqual(@as(u32, 15), windows[15].top_val);
    try std.testing.expectEqual(@as(u32, 64), windows[15].sec);

    const probe = try watchdog.probeSummary(.{
        .nowayout = true,
        .requested_timeout_sec = 11,
    });
    try std.testing.expectEqual(dw_wdt.TopSource.custom, probe.top_source);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.default_selection, probe.timeout_origin);
    try std.testing.expect(!probe.already_running);
    try std.testing.expect(!probe.hardware_running);
    try std.testing.expect(probe.nowayout);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, probe.restart_priority);
    try std.testing.expect(probe.stop_on_reboot);
    try std.testing.expect(probe.can_stop);
    try std.testing.expectEqual(@as(u32, 12), probe.timeout_sec);
}

test "phase11 dw_wdt start and ping select the nearest fixed top in reset mode" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const config = try watchdog.setTimeout(9);
    try std.testing.expectEqual(@as(u32, 16), config.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), config.pretimeout_sec);

    var runtime = try watchdog.start();
    try std.testing.expect(runtime.running);
    try std.testing.expectEqual(dw_wdt.ResponseMode.reset, runtime.response_mode);
    try std.testing.expectEqual(
        dw_wdt.control_reg_wdt_en_mask,
        runtime.registers.control & dw_wdt.control_reg_wdt_en_mask,
    );
    try std.testing.expectEqual(@as(u32, 0x44), runtime.registers.timeout_range);
    try std.testing.expectEqual(dw_wdt.counter_restart_kick_value, runtime.registers.restart);

    runtime = try watchdog.ping();
    try std.testing.expect(runtime.running);
    try std.testing.expectEqual(dw_wdt.counter_restart_kick_value, runtime.registers.restart);
}

test "phase11 dw_wdt irq mode keeps pretimeout bookkeeping and counts the second stage only after the interrupt" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = try watchdog.setResponseMode(.irq);
    const config = try watchdog.setTimeout(9);
    try std.testing.expectEqual(dw_wdt.ResponseMode.irq, config.response_mode);
    try std.testing.expectEqual(@as(u32, 16), config.timeout_sec);
    try std.testing.expectEqual(@as(u32, 8), config.pretimeout_sec);

    _ = try watchdog.start();
    _ = watchdog.setCurrentCount(3 * 65_536);
    var runtime = watchdog.runtimeSnapshot();
    try std.testing.expectEqual(@as(u32, 11), runtime.time_left_sec);

    _ = watchdog.setInterruptPending(true);
    runtime = watchdog.runtimeSnapshot();
    try std.testing.expect(runtime.interrupt_pending);
    try std.testing.expectEqual(@as(u32, 3), runtime.time_left_sec);
}

test "phase11 dw_wdt loadRegisters re-derives imported running state from hardware bits" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    const runtime = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.hardware_running);
    try std.testing.expectEqual(dw_wdt.ResponseMode.irq, runtime.response_mode);
    try std.testing.expectEqual(@as(u32, 16), runtime.timeout_sec);
    try std.testing.expectEqual(@as(u32, 8), runtime.pretimeout_sec);
    try std.testing.expectEqual(@as(u32, 10), runtime.time_left_sec);
}

test "phase11 dw_wdt probe summary records imported running state and restart bookkeeping" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const probe = try watchdog.probeSummary(.{
        .nowayout = false,
        .restart_priority = dw_wdt.default_restart_priority,
    });
    try std.testing.expectEqual(dw_wdt.TopSource.fixed, probe.top_source);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.imported_running_state, probe.timeout_origin);
    try std.testing.expect(probe.already_running);
    try std.testing.expect(probe.hardware_running);
    try std.testing.expectEqual(dw_wdt.ResponseMode.irq, probe.response_mode);
    try std.testing.expectEqual(@as(u32, 16), probe.timeout_sec);
    try std.testing.expectEqual(@as(u32, 8), probe.pretimeout_sec);
    try std.testing.expect(!probe.nowayout);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, probe.restart_priority);
    try std.testing.expect(probe.stop_on_reboot);
    try std.testing.expect(!probe.can_stop);
}

test "phase11 dw_wdt registration handoff keeps watchdog info, parent, and timeout bookkeeping reviewable" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const handoff = try watchdog.registrationHandoffSummary(false, .{
        .nowayout = true,
        .requested_timeout_sec = 9,
    });
    try std.testing.expectEqual(dw_wdt.WatchdogInfoSelection.basic, handoff.watchdog_info_selection);
    try std.testing.expect(!handoff.watchdog_info_supports_pretimeout);
    try std.testing.expectEqual(dw_wdt.TopSource.fixed, handoff.top_source);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.default_selection, handoff.timeout_origin);
    try std.testing.expectEqual(@as(u32, 16), handoff.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), handoff.pretimeout_sec);
    try std.testing.expect(handoff.nowayout);
    try std.testing.expect(handoff.nowayout_applied);
    try std.testing.expect(handoff.parent_attached);
    try std.testing.expect(handoff.watchdog_drvdata_set);
    try std.testing.expect(handoff.timeout_init_requested);
    try std.testing.expect(!handoff.marks_hw_running);
    try std.testing.expect(handoff.programs_timeout_before_registration);
    try std.testing.expect(handoff.stop_on_reboot);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, handoff.restart_priority);
    try std.testing.expect(handoff.register_device_requested);
}

test "phase11 dw_wdt registration handoff imports running state before registration when hardware is already active" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const handoff = try watchdog.registrationHandoffSummary(true, .{
        .nowayout = false,
    });
    try std.testing.expectEqual(dw_wdt.WatchdogInfoSelection.pretimeout, handoff.watchdog_info_selection);
    try std.testing.expect(handoff.watchdog_info_supports_pretimeout);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.imported_running_state, handoff.timeout_origin);
    try std.testing.expectEqual(@as(u32, 16), handoff.timeout_sec);
    try std.testing.expectEqual(@as(u32, 8), handoff.pretimeout_sec);
    try std.testing.expect(!handoff.nowayout);
    try std.testing.expect(!handoff.nowayout_applied);
    try std.testing.expect(handoff.parent_attached);
    try std.testing.expect(handoff.watchdog_drvdata_set);
    try std.testing.expect(handoff.timeout_init_requested);
    try std.testing.expect(handoff.marks_hw_running);
    try std.testing.expect(!handoff.programs_timeout_before_registration);
    try std.testing.expect(handoff.stop_on_reboot);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, handoff.restart_priority);
    try std.testing.expect(handoff.register_device_requested);
}

test "phase11 dw_wdt platform resource preflight keeps clock choice and optional resources reviewable" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    const preflight = watchdog.platformResourcePreflightSummary(.{
        .timer_clock_selection = .named_tclk,
        .has_apb_clock = true,
        .has_pretimeout_irq = true,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", preflight.anchor);
    try std.testing.expectEqual(dw_wdt.TimerClockSelection.named_tclk, preflight.timer_clock_selection);
    try std.testing.expectEqual(@as(u32, 65_536), preflight.timer_clock_rate_hz);
    try std.testing.expect(preflight.timer_clock_ready);
    try std.testing.expect(preflight.apb_clock_optional);
    try std.testing.expect(preflight.apb_clock_present);
    try std.testing.expect(preflight.reset_control_optional);
    try std.testing.expect(preflight.reset_control_shared);
    try std.testing.expect(preflight.reset_control_available);
    try std.testing.expect(preflight.pretimeout_irq_optional);
    try std.testing.expect(preflight.pretimeout_irq_present);
    try std.testing.expect(preflight.pretimeout_irq_shared_rising);
}

test "phase11 dw_wdt platform resource preflight records fallback timer clock and absent optional resources" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(32_768, false);
    const preflight = watchdog.platformResourcePreflightSummary(.{
        .timer_clock_selection = .unnamed_default,
        .has_apb_clock = false,
        .has_pretimeout_irq = false,
    });
    try std.testing.expectEqual(dw_wdt.TimerClockSelection.unnamed_default, preflight.timer_clock_selection);
    try std.testing.expectEqual(@as(u32, 32_768), preflight.timer_clock_rate_hz);
    try std.testing.expect(preflight.timer_clock_ready);
    try std.testing.expect(preflight.apb_clock_optional);
    try std.testing.expect(!preflight.apb_clock_present);
    try std.testing.expect(preflight.reset_control_optional);
    try std.testing.expect(preflight.reset_control_shared);
    try std.testing.expect(!preflight.reset_control_available);
    try std.testing.expect(preflight.pretimeout_irq_optional);
    try std.testing.expect(!preflight.pretimeout_irq_present);
    try std.testing.expect(!preflight.pretimeout_irq_shared_rising);
}

test "phase11 dw_wdt live resource order keeps tclk, optional pclk, reset, irq, and registration sequencing explicit" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    const order = try watchdog.liveResourceOrderSummary(
        .{
            .requested_timeout_sec = 9,
        },
        .{
            .timer_clock_selection = .named_tclk,
            .has_apb_clock = true,
            .has_pretimeout_irq = true,
        },
    );
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", order.anchor);
    try std.testing.expectEqual(dw_wdt.TimerClockSelection.named_tclk, order.timer_clock_selection);
    try std.testing.expect(order.acquires_timer_clock_first);
    try std.testing.expect(order.acquires_optional_apb_after_timer);
    try std.testing.expect(order.deasserts_shared_reset_before_registration);
    try std.testing.expect(order.requests_optional_pretimeout_irq_before_registration);
    try std.testing.expect(order.programs_timeout_before_registration);
    try std.testing.expect(order.registers_watchdog_after_resources_ready);
    try std.testing.expect(order.install_restart_handler_after_registration);
}

test "phase11 dw_wdt live resource order preserves imported running-state registration sequencing" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const order = try watchdog.liveResourceOrderSummary(
        .{
            .nowayout = false,
        },
        .{
            .timer_clock_selection = .unnamed_default,
            .has_apb_clock = false,
            .has_pretimeout_irq = false,
        },
    );
    try std.testing.expectEqual(dw_wdt.TimerClockSelection.unnamed_default, order.timer_clock_selection);
    try std.testing.expect(order.acquires_timer_clock_first);
    try std.testing.expect(!order.acquires_optional_apb_after_timer);
    try std.testing.expect(!order.deasserts_shared_reset_before_registration);
    try std.testing.expect(!order.requests_optional_pretimeout_irq_before_registration);
    try std.testing.expect(!order.programs_timeout_before_registration);
    try std.testing.expect(order.registers_watchdog_after_resources_ready);
    try std.testing.expect(order.install_restart_handler_after_registration);
}

test "phase11 dw_wdt timeout topology summary keeps fixed, custom, and fallback TOP sourcing explicit" {
    const fixed_summary = try dw_wdt.DwWdtLab.timeoutTopologySummary(65_536, false, .{
        .component_uses_fixed_top = true,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", fixed_summary.anchor);
    try std.testing.expectEqual(dw_wdt.TimeoutTopologySelection.fixed_component, fixed_summary.selection);
    try std.testing.expectEqual(dw_wdt.TopSource.fixed, fixed_summary.top_source);
    try std.testing.expect(!fixed_summary.custom_tops_requested);
    try std.testing.expect(!fixed_summary.custom_tops_applied);
    try std.testing.expect(!fixed_summary.fell_back_to_fixed_tops);
    try std.testing.expectEqual(@as(u32, 1), fixed_summary.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, 32_768_000), fixed_summary.max_hw_heartbeat_ms);

    const custom_tops = [_]u32{
        20_000, 4_000,  8_000,  12_000,
        16_000, 24_000, 28_000, 32_000,
        36_000, 40_000, 44_000, 48_000,
        52_000, 56_000, 60_000, 64_000,
    };
    const custom_summary = try dw_wdt.DwWdtLab.timeoutTopologySummary(1_000, true, .{
        .component_uses_fixed_top = false,
        .custom_tops = custom_tops,
    });
    try std.testing.expectEqual(dw_wdt.TimeoutTopologySelection.custom_component, custom_summary.selection);
    try std.testing.expectEqual(dw_wdt.TopSource.custom, custom_summary.top_source);
    try std.testing.expect(custom_summary.custom_tops_requested);
    try std.testing.expect(custom_summary.custom_tops_applied);
    try std.testing.expect(!custom_summary.fell_back_to_fixed_tops);
    try std.testing.expectEqual(@as(u32, 4), custom_summary.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, 64_000), custom_summary.max_hw_heartbeat_ms);

    const fallback_summary = try dw_wdt.DwWdtLab.timeoutTopologySummary(32_768, false, .{
        .component_uses_fixed_top = false,
    });
    try std.testing.expectEqual(dw_wdt.TimeoutTopologySelection.fixed_fallback, fallback_summary.selection);
    try std.testing.expectEqual(dw_wdt.TopSource.fixed, fallback_summary.top_source);
    try std.testing.expect(!fallback_summary.custom_tops_requested);
    try std.testing.expect(!fallback_summary.custom_tops_applied);
    try std.testing.expect(fallback_summary.fell_back_to_fixed_tops);
    try std.testing.expectEqual(@as(u32, 2), fallback_summary.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, 65_536_000), fallback_summary.max_hw_heartbeat_ms);
}

test "phase11 dw_wdt timeout topology still rejects a custom array with no valid timeout window" {
    const zero_tops = [_]u32{0} ** dw_wdt.num_tops;
    try std.testing.expectError(error.NoValidTop, dw_wdt.DwWdtLab.timeoutTopologySummary(1_000, false, .{
        .component_uses_fixed_top = false,
        .custom_tops = zero_tops,
    }));
}

test "phase11 dw_wdt remove handoff keeps unregister and reset-control teardown parity explicit" {
    var unstoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const unstoppable_summary = try unstoppable.summarizeRemoveHandoff(.{
        .watchdog_running_before_remove = true,
        .remove_interrupt_pending = true,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", unstoppable_summary.anchor);
    try std.testing.expect(!unstoppable_summary.reset_control_available);
    try std.testing.expect(unstoppable_summary.debugfs_clear_requested);
    try std.testing.expect(unstoppable_summary.unregister_device_requested);
    try std.testing.expect(unstoppable_summary.remove_path_running_before_remove);
    try std.testing.expect(unstoppable_summary.remove_path_running_after_remove);
    try std.testing.expect(unstoppable_summary.remove_path_hardware_running_after_remove);
    try std.testing.expect(!unstoppable_summary.remove_clears_enable_bit);
    try std.testing.expect(!unstoppable_summary.remove_clears_interrupt_status);
    try std.testing.expect(!unstoppable_summary.remove_asserts_reset_control);
    try std.testing.expect(unstoppable_summary.remove_preserves_running_marker_without_reset);
    try std.testing.expect(unstoppable_summary.remove_preserves_pending_interrupt_without_reset);

    var stoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    const stoppable_summary = try stoppable.summarizeRemoveHandoff(.{
        .watchdog_running_before_remove = true,
        .remove_interrupt_pending = true,
    });
    try std.testing.expect(stoppable_summary.reset_control_available);
    try std.testing.expect(stoppable_summary.debugfs_clear_requested);
    try std.testing.expect(stoppable_summary.unregister_device_requested);
    try std.testing.expect(stoppable_summary.remove_path_running_before_remove);
    try std.testing.expect(!stoppable_summary.remove_path_running_after_remove);
    try std.testing.expect(!stoppable_summary.remove_path_hardware_running_after_remove);
    try std.testing.expect(stoppable_summary.remove_clears_enable_bit);
    try std.testing.expect(stoppable_summary.remove_clears_interrupt_status);
    try std.testing.expect(stoppable_summary.remove_asserts_reset_control);
    try std.testing.expect(!stoppable_summary.remove_preserves_running_marker_without_reset);
    try std.testing.expect(!stoppable_summary.remove_preserves_pending_interrupt_without_reset);

    var quiet_running_stoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    const quiet_running_stoppable_summary = try quiet_running_stoppable.summarizeRemoveHandoff(.{
        .watchdog_running_before_remove = true,
        .remove_interrupt_pending = false,
    });
    try std.testing.expect(quiet_running_stoppable_summary.reset_control_available);
    try std.testing.expect(quiet_running_stoppable_summary.debugfs_clear_requested);
    try std.testing.expect(quiet_running_stoppable_summary.unregister_device_requested);
    try std.testing.expect(quiet_running_stoppable_summary.remove_path_running_before_remove);
    try std.testing.expect(!quiet_running_stoppable_summary.remove_path_running_after_remove);
    try std.testing.expect(!quiet_running_stoppable_summary.remove_path_hardware_running_after_remove);
    try std.testing.expect(quiet_running_stoppable_summary.remove_clears_enable_bit);
    try std.testing.expect(!quiet_running_stoppable_summary.remove_clears_interrupt_status);
    try std.testing.expect(quiet_running_stoppable_summary.remove_asserts_reset_control);
    try std.testing.expect(!quiet_running_stoppable_summary.remove_preserves_running_marker_without_reset);
    try std.testing.expect(!quiet_running_stoppable_summary.remove_preserves_pending_interrupt_without_reset);

    var quiet_unstoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const quiet_unstoppable_summary = try quiet_unstoppable.summarizeRemoveHandoff(.{
        .watchdog_running_before_remove = false,
        .remove_interrupt_pending = false,
    });
    try std.testing.expect(!quiet_unstoppable_summary.remove_path_running_before_remove);
    try std.testing.expect(!quiet_unstoppable_summary.remove_path_running_after_remove);
    try std.testing.expect(!quiet_unstoppable_summary.remove_path_hardware_running_after_remove);
    try std.testing.expect(!quiet_unstoppable_summary.remove_clears_enable_bit);
    try std.testing.expect(!quiet_unstoppable_summary.remove_clears_interrupt_status);
    try std.testing.expect(!quiet_unstoppable_summary.remove_asserts_reset_control);
    try std.testing.expect(!quiet_unstoppable_summary.remove_preserves_running_marker_without_reset);
    try std.testing.expect(!quiet_unstoppable_summary.remove_preserves_pending_interrupt_without_reset);

    var pending_idle_unstoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const pending_idle_unstoppable_summary = try pending_idle_unstoppable.summarizeRemoveHandoff(.{
        .watchdog_running_before_remove = false,
        .remove_interrupt_pending = true,
    });
    try std.testing.expect(!pending_idle_unstoppable_summary.remove_path_running_before_remove);
    try std.testing.expect(!pending_idle_unstoppable_summary.remove_path_running_after_remove);
    try std.testing.expect(!pending_idle_unstoppable_summary.remove_path_hardware_running_after_remove);
    try std.testing.expect(!pending_idle_unstoppable_summary.remove_clears_enable_bit);
    try std.testing.expect(!pending_idle_unstoppable_summary.remove_clears_interrupt_status);
    try std.testing.expect(!pending_idle_unstoppable_summary.remove_asserts_reset_control);
    try std.testing.expect(!pending_idle_unstoppable_summary.remove_preserves_running_marker_without_reset);
    try std.testing.expect(pending_idle_unstoppable_summary.remove_preserves_pending_interrupt_without_reset);

    var pending_idle_stoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    const pending_idle_stoppable_summary = try pending_idle_stoppable.summarizeRemoveHandoff(.{
        .watchdog_running_before_remove = false,
        .remove_interrupt_pending = true,
    });
    try std.testing.expect(pending_idle_stoppable_summary.reset_control_available);
    try std.testing.expect(pending_idle_stoppable_summary.debugfs_clear_requested);
    try std.testing.expect(pending_idle_stoppable_summary.unregister_device_requested);
    try std.testing.expect(!pending_idle_stoppable_summary.remove_path_running_before_remove);
    try std.testing.expect(!pending_idle_stoppable_summary.remove_path_running_after_remove);
    try std.testing.expect(!pending_idle_stoppable_summary.remove_path_hardware_running_after_remove);
    try std.testing.expect(!pending_idle_stoppable_summary.remove_clears_enable_bit);
    try std.testing.expect(pending_idle_stoppable_summary.remove_clears_interrupt_status);
    try std.testing.expect(pending_idle_stoppable_summary.remove_asserts_reset_control);
    try std.testing.expect(!pending_idle_stoppable_summary.remove_preserves_running_marker_without_reset);
    try std.testing.expect(!pending_idle_stoppable_summary.remove_preserves_pending_interrupt_without_reset);
}

test "phase11 dw_wdt stop and restart stay bounded to reset-control and non-stoppable semantics" {
    var unstoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    _ = try unstoppable.start();
    var runtime = unstoppable.stop();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.hardware_running);
    const unstoppable_summary = try unstoppable.summarizeTeardownLifecycle(.{
        .restart_watchdog_running = true,
        .stop_interrupt_pending = true,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", unstoppable_summary.anchor);
    try std.testing.expect(!unstoppable_summary.can_stop);
    try std.testing.expect(unstoppable_summary.stop_path_running_before_stop);
    try std.testing.expect(unstoppable_summary.stop_path_running_after_stop);
    try std.testing.expect(unstoppable_summary.stop_path_hardware_running_after_stop);
    try std.testing.expect(!unstoppable_summary.stop_clears_enable_bit);
    try std.testing.expect(!unstoppable_summary.stop_clears_interrupt_status);
    try std.testing.expect(unstoppable_summary.stop_preserves_pending_interrupt_without_reset);
    try std.testing.expect(!unstoppable_summary.stop_uses_reset_pulse);
    try std.testing.expect(unstoppable_summary.stop_preserves_running_marker_without_reset);
    try std.testing.expect(unstoppable_summary.restart_path_running_before_restart);
    try std.testing.expect(unstoppable_summary.restart_path_running_after_restart);
    try std.testing.expect(unstoppable_summary.restart_path_hardware_running_after_restart);
    try std.testing.expect(unstoppable_summary.restart_forces_reset_mode);
    try std.testing.expect(unstoppable_summary.restart_clears_pretimeout);
    try std.testing.expect(unstoppable_summary.restart_clears_timeout_range);
    try std.testing.expect(unstoppable_summary.restart_kicks_running_watchdog);
    try std.testing.expect(!unstoppable_summary.restart_enables_stopped_watchdog);

    var stoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = try stoppable.start();
    runtime = stoppable.stop();
    try std.testing.expect(!runtime.running);
    try std.testing.expect(!runtime.hardware_running);
    const stoppable_summary = try stoppable.summarizeTeardownLifecycle(.{
        .restart_watchdog_running = false,
        .stop_interrupt_pending = true,
    });
    try std.testing.expect(stoppable_summary.can_stop);
    try std.testing.expect(stoppable_summary.stop_path_running_before_stop);
    try std.testing.expect(!stoppable_summary.stop_path_running_after_stop);
    try std.testing.expect(!stoppable_summary.stop_path_hardware_running_after_stop);
    try std.testing.expect(stoppable_summary.stop_clears_enable_bit);
    try std.testing.expect(stoppable_summary.stop_clears_interrupt_status);
    try std.testing.expect(!stoppable_summary.stop_preserves_pending_interrupt_without_reset);
    try std.testing.expect(stoppable_summary.stop_uses_reset_pulse);
    try std.testing.expect(!stoppable_summary.stop_preserves_running_marker_without_reset);
    try std.testing.expect(!stoppable_summary.restart_path_running_before_restart);
    try std.testing.expect(stoppable_summary.restart_path_running_after_restart);
    try std.testing.expect(stoppable_summary.restart_path_hardware_running_after_restart);
    try std.testing.expect(stoppable_summary.restart_forces_reset_mode);
    try std.testing.expect(stoppable_summary.restart_clears_pretimeout);
    try std.testing.expect(stoppable_summary.restart_clears_timeout_range);
    try std.testing.expect(!stoppable_summary.restart_kicks_running_watchdog);
    try std.testing.expect(stoppable_summary.restart_enables_stopped_watchdog);

    var quiet_unstoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const quiet_unstoppable_summary = try quiet_unstoppable.summarizeTeardownLifecycle(.{
        .restart_watchdog_running = true,
        .stop_interrupt_pending = false,
    });
    try std.testing.expect(!quiet_unstoppable_summary.stop_clears_interrupt_status);
    try std.testing.expect(!quiet_unstoppable_summary.stop_preserves_pending_interrupt_without_reset);

    var quiet_stoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    const quiet_stoppable_summary = try quiet_stoppable.summarizeTeardownLifecycle(.{
        .restart_watchdog_running = true,
        .stop_interrupt_pending = false,
    });
    try std.testing.expect(quiet_stoppable_summary.can_stop);
    try std.testing.expect(quiet_stoppable_summary.stop_path_running_before_stop);
    try std.testing.expect(!quiet_stoppable_summary.stop_path_running_after_stop);
    try std.testing.expect(!quiet_stoppable_summary.stop_path_hardware_running_after_stop);
    try std.testing.expect(!quiet_stoppable_summary.stop_clears_interrupt_status);
    try std.testing.expect(quiet_stoppable_summary.stop_uses_reset_pulse);
    try std.testing.expect(!quiet_stoppable_summary.stop_preserves_pending_interrupt_without_reset);
    try std.testing.expect(!quiet_stoppable_summary.stop_preserves_running_marker_without_reset);
    try std.testing.expect(quiet_stoppable_summary.restart_path_running_before_restart);
    try std.testing.expect(quiet_stoppable_summary.restart_path_running_after_restart);
    try std.testing.expect(quiet_stoppable_summary.restart_path_hardware_running_after_restart);
    try std.testing.expect(quiet_stoppable_summary.restart_kicks_running_watchdog);
    try std.testing.expect(!quiet_stoppable_summary.restart_enables_stopped_watchdog);

    var restart_lab = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    runtime = restart_lab.armRestart();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.restart_armed);
    try std.testing.expectEqual(dw_wdt.ResponseMode.reset, runtime.response_mode);
    try std.testing.expectEqual(@as(u32, 0), runtime.registers.timeout_range);

    runtime = restart_lab.loadRegisters(.{});
    try std.testing.expect(!runtime.running);
    try std.testing.expect(!runtime.hardware_running);
}

test "phase11 dw_wdt suspend and resume preserve irq-mode state across optional apb clock handoff" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    const summary = try watchdog.summarizeSuspendResume(.{
        .watchdog_running_before_suspend = true,
        .interrupt_pending_before_suspend = true,
        .response_mode_before_suspend = .irq,
        .requested_timeout_sec = 9,
        .timer_clock_selection = .named_tclk,
        .has_apb_clock = true,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", summary.anchor);
    try std.testing.expectEqual(dw_wdt.TimerClockSelection.named_tclk, summary.timer_clock_selection);
    try std.testing.expect(summary.apb_clock_present);
    try std.testing.expect(summary.suspend_path_running_before_suspend);
    try std.testing.expect(summary.suspend_path_interrupt_pending_before_suspend);
    try std.testing.expect(summary.suspend_saves_control_register);
    try std.testing.expect(summary.suspend_saves_timeout_register);
    try std.testing.expect(summary.suspend_disables_timer_clock);
    try std.testing.expect(summary.suspend_disables_optional_apb_before_timer);
    try std.testing.expect(summary.resume_enables_timer_clock_first);
    try std.testing.expect(summary.resume_enables_optional_apb_after_timer);
    try std.testing.expect(summary.resume_restores_timeout_before_control);
    try std.testing.expect(summary.resume_replays_restart_kick);
    try std.testing.expect(summary.resume_path_running_after_resume);
    try std.testing.expect(summary.resume_path_hardware_running_after_resume);
    try std.testing.expect(summary.resume_interrupt_pending_after_resume);
    try std.testing.expect(summary.resume_preserves_running_state);
    try std.testing.expect(summary.resume_preserves_interrupt_pending);
    try std.testing.expect(summary.resume_preserves_response_mode);
    try std.testing.expect(summary.resume_preserves_timeout_programming);
}

test "phase11 dw_wdt suspend and resume keep an idle watchdog quiescent without optional apb clock" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(32_768, false);
    const summary = try watchdog.summarizeSuspendResume(.{
        .watchdog_running_before_suspend = false,
        .interrupt_pending_before_suspend = false,
        .response_mode_before_suspend = .reset,
        .requested_timeout_sec = 9,
        .timer_clock_selection = .unnamed_default,
        .has_apb_clock = false,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", summary.anchor);
    try std.testing.expectEqual(dw_wdt.TimerClockSelection.unnamed_default, summary.timer_clock_selection);
    try std.testing.expect(!summary.apb_clock_present);
    try std.testing.expect(!summary.suspend_path_running_before_suspend);
    try std.testing.expect(!summary.suspend_path_interrupt_pending_before_suspend);
    try std.testing.expect(summary.suspend_saves_control_register);
    try std.testing.expect(summary.suspend_saves_timeout_register);
    try std.testing.expect(summary.suspend_disables_timer_clock);
    try std.testing.expect(!summary.suspend_disables_optional_apb_before_timer);
    try std.testing.expect(summary.resume_enables_timer_clock_first);
    try std.testing.expect(!summary.resume_enables_optional_apb_after_timer);
    try std.testing.expect(summary.resume_restores_timeout_before_control);
    try std.testing.expect(summary.resume_replays_restart_kick);
    try std.testing.expect(!summary.resume_path_running_after_resume);
    try std.testing.expect(!summary.resume_path_hardware_running_after_resume);
    try std.testing.expect(!summary.resume_interrupt_pending_after_resume);
    try std.testing.expect(summary.resume_preserves_running_state);
    try std.testing.expect(summary.resume_preserves_interrupt_pending);
    try std.testing.expect(summary.resume_preserves_response_mode);
    try std.testing.expect(summary.resume_preserves_timeout_programming);
}
