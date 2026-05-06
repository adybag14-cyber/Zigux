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
    try std.testing.expectError(error.WatchdogNotRunning, watchdog.ping());
}

test "phase11 dw_wdt exposes the fixed-top timeout matrix in ascending order" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(32_768, false);
    const windows = watchdog.timeoutWindows();

    try std.testing.expectEqual(@as(usize, dw_wdt.num_tops), windows.len);
    try std.testing.expectEqual(@as(u32, 0), windows[0].top_val);
    try std.testing.expectEqual(@as(u32, 2), windows[0].sec);
    try std.testing.expectEqual(@as(u32, 0), windows[0].msec);
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

test "phase11 dw_wdt registration summary selects the basic info profile before registration" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const registration = try watchdog.registrationSummary(.{
        .nowayout = true,
        .requested_timeout_sec = 9,
        .stop_on_reboot = true,
    }, false);

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", registration.anchor);
    try std.testing.expectEqualStrings("watchdog_register_device", registration.registration_call);
    try std.testing.expectEqualStrings("platform_device.dev", registration.parent_anchor);
    try std.testing.expectEqualStrings("Synopsys DesignWare Watchdog", registration.info.identity);
    try std.testing.expect(registration.info.supports_keepalive_ping);
    try std.testing.expect(registration.info.supports_set_timeout);
    try std.testing.expect(registration.info.supports_magic_close);
    try std.testing.expect(!registration.info.supports_pretimeout);
    try std.testing.expect(registration.ops.start);
    try std.testing.expect(registration.ops.stop);
    try std.testing.expect(registration.ops.ping);
    try std.testing.expect(registration.ops.set_timeout);
    try std.testing.expect(registration.ops.set_pretimeout);
    try std.testing.expect(registration.ops.get_timeleft);
    try std.testing.expect(registration.ops.restart);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.default_selection, registration.timeout_origin);
    try std.testing.expect(registration.needs_timeout_programming);
    try std.testing.expect(!registration.imported_running_state);
    try std.testing.expectEqual(@as(u32, 16), registration.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), registration.pretimeout_sec);
    try std.testing.expect(registration.nowayout);
    try std.testing.expect(registration.stop_on_reboot);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, registration.restart_priority);
    try std.testing.expect(!registration.can_stop);
    try std.testing.expectEqual(@as(u32, 1), registration.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, 32_768_000), registration.max_hw_heartbeat_ms);
}

test "phase11 dw_wdt registration summary preserves pretimeout and imported-running selection" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const registration = try watchdog.registrationSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, true);

    try std.testing.expect(registration.info.supports_pretimeout);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.imported_running_state, registration.timeout_origin);
    try std.testing.expect(registration.imported_running_state);
    try std.testing.expect(!registration.needs_timeout_programming);
    try std.testing.expect(registration.hardware_running);
    try std.testing.expect(registration.can_stop);
    try std.testing.expectEqual(@as(u32, 16), registration.timeout_sec);
    try std.testing.expectEqual(@as(u32, 8), registration.pretimeout_sec);
    try std.testing.expect(!registration.nowayout);
}

test "phase11 dw_wdt registration summary clears imported pretimeout when no irq wiring is present" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const registration = try watchdog.registrationSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, false);

    try std.testing.expect(!registration.info.supports_pretimeout);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.imported_running_state, registration.timeout_origin);
    try std.testing.expect(registration.imported_running_state);
    try std.testing.expect(!registration.needs_timeout_programming);
    try std.testing.expect(registration.hardware_running);
    try std.testing.expect(registration.can_stop);
    try std.testing.expectEqual(@as(u32, 16), registration.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), registration.pretimeout_sec);
    try std.testing.expect(!registration.nowayout);
}

test "phase11 dw_wdt start and ping select the nearest fixed top in reset mode" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const config = try watchdog.setTimeout(9);
    try std.testing.expectEqual(@as(u32, 16), config.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), config.pretimeout_sec);

    var runtime = try watchdog.start();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.hardware_running);
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

test "phase11 dw_wdt running restart keeps reset-mode control and kick semantics explicit" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    _ = try watchdog.start();
    _ = watchdog.setCurrentCount(5 * 65_536);

    const runtime = watchdog.armRestart();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.hardware_running);
    try std.testing.expect(runtime.restart_armed);
    try std.testing.expectEqual(dw_wdt.ResponseMode.reset, runtime.response_mode);
    try std.testing.expectEqual(@as(u32, 0), runtime.pretimeout_sec);
    try std.testing.expectEqual(dw_wdt.counter_restart_kick_value, runtime.registers.restart);
    try std.testing.expectEqual(
        dw_wdt.control_reg_wdt_en_mask,
        runtime.registers.control & (dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask),
    );
    try std.testing.expectEqual(@as(u32, 0), runtime.registers.timeout_range);
    try std.testing.expectEqual(@as(u32, 5 * 65_536), runtime.registers.current_count);
}

test "phase11 dw_wdt stop and restart stay bounded to reset-control and non-stoppable semantics" {
    var unstoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    _ = try unstoppable.start();
    _ = unstoppable.setCurrentCount(5 * 65_536);
    _ = unstoppable.setInterruptPending(true);
    var runtime = unstoppable.stop();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.hardware_running);
    try std.testing.expectEqual(@as(u32, 5 * 65_536), runtime.registers.current_count);
    try std.testing.expect(runtime.interrupt_pending);

    runtime = try unstoppable.ping();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.hardware_running);
    try std.testing.expectEqual(dw_wdt.counter_restart_kick_value, runtime.registers.restart);
    try std.testing.expectEqual(@as(u32, 5 * 65_536), runtime.registers.current_count);
    try std.testing.expect(runtime.interrupt_pending);

    var stoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = try stoppable.start();
    _ = stoppable.setCurrentCount(5 * 65_536);
    _ = stoppable.setInterruptPending(true);
    runtime = stoppable.stop();
    try std.testing.expect(!runtime.running);
    try std.testing.expect(!runtime.hardware_running);
    try std.testing.expectEqual(@as(u32, 0), runtime.registers.current_count);
    try std.testing.expectEqual(@as(u32, 0), runtime.registers.interrupt_status);
    try std.testing.expect(!runtime.interrupt_pending);

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

test "phase11 dw_wdt reset-controlled stop clears irq-mode bookkeeping after staged interrupt state" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = try watchdog.setResponseMode(.irq);
    _ = try watchdog.setTimeout(9);
    _ = try watchdog.start();
    _ = watchdog.setCurrentCount(3 * 65_536);
    _ = watchdog.setInterruptPending(true);

    const runtime = watchdog.stop();
    try std.testing.expectEqual(dw_wdt.ResponseMode.irq, runtime.response_mode);
    try std.testing.expectEqual(@as(u32, 16), runtime.timeout_sec);
    try std.testing.expectEqual(@as(u32, 8), runtime.pretimeout_sec);
    try std.testing.expect(!runtime.running);
    try std.testing.expect(!runtime.hardware_running);
    try std.testing.expectEqual(@as(u32, dw_wdt.control_reg_resp_mode_mask), runtime.registers.control);
    try std.testing.expectEqual(@as(u32, 0x33), runtime.registers.timeout_range);
    try std.testing.expectEqual(@as(u32, 0), runtime.registers.current_count);
    try std.testing.expectEqual(@as(u32, 0), runtime.registers.interrupt_status);
    try std.testing.expect(!runtime.interrupt_pending);
    try std.testing.expectEqual(@as(u32, 0), runtime.time_left_sec);
    try std.testing.expectError(error.WatchdogNotRunning, watchdog.ping());
}

test "phase11 dw_wdt non-stoppable stop preserves irq-mode bookkeeping and follow-up ping semantics" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    _ = try watchdog.setResponseMode(.irq);
    _ = try watchdog.setTimeout(9);
    _ = try watchdog.start();
    _ = watchdog.setCurrentCount(3 * 65_536);
    _ = watchdog.setInterruptPending(true);

    var runtime = watchdog.stop();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.hardware_running);
    try std.testing.expectEqual(dw_wdt.ResponseMode.irq, runtime.response_mode);
    try std.testing.expectEqual(@as(u32, 16), runtime.timeout_sec);
    try std.testing.expectEqual(@as(u32, 8), runtime.pretimeout_sec);
    try std.testing.expectEqual(@as(u32, 3), runtime.time_left_sec);
    try std.testing.expectEqual(@as(u32, 3 * 65_536), runtime.registers.current_count);
    try std.testing.expect(runtime.interrupt_pending);

    runtime = try watchdog.ping();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.hardware_running);
    try std.testing.expectEqual(dw_wdt.ResponseMode.irq, runtime.response_mode);
    try std.testing.expectEqual(@as(u32, 8), runtime.pretimeout_sec);
    try std.testing.expectEqual(dw_wdt.counter_restart_kick_value, runtime.registers.restart);
    try std.testing.expectEqual(@as(u32, 3 * 65_536), runtime.registers.current_count);
    try std.testing.expect(runtime.interrupt_pending);
}
