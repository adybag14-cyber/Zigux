const std = @import("std");
const dw_wdt = @import("dw_wdt.zig");

test "dw_wdt platform handoff keeps registration scaffolding explicit when irq wiring is ready" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const handoff = try watchdog.platformHandoffSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, true, true, true);

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", handoff.anchor);
    try std.testing.expectEqualStrings("watchdog_register_device", handoff.registration_call);
    try std.testing.expectEqualStrings("platform_device.dev", handoff.parent_anchor);
    try std.testing.expectEqualStrings("platform_set_drvdata", handoff.drvdata_anchor);
    try std.testing.expectEqual(dw_wdt.TopSource.fixed, handoff.top_source);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.imported_running_state, handoff.timeout_origin);
    try std.testing.expectEqual(@as(u32, 65_536), handoff.rate_hz);
    try std.testing.expect(handoff.reset_control_available);
    try std.testing.expect(handoff.irq_registration_ready);
    try std.testing.expect(handoff.drvdata_ready);
    try std.testing.expect(!handoff.nowayout);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, handoff.restart_priority);
    try std.testing.expect(handoff.stop_on_reboot);
    try std.testing.expect(handoff.can_stop);
    try std.testing.expectEqual(@as(u32, 16), handoff.timeout_sec);
    try std.testing.expectEqual(@as(u32, 8), handoff.pretimeout_sec);
    try std.testing.expect(handoff.imported_running_state);
    try std.testing.expect(!handoff.needs_timeout_programming);
}

test "dw_wdt platform handoff flattens imported pretimeout when irq wiring is absent" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const handoff = try watchdog.platformHandoffSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, true, false, true);

    try std.testing.expectEqual(dw_wdt.TopSource.fixed, handoff.top_source);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.imported_running_state, handoff.timeout_origin);
    try std.testing.expect(handoff.reset_control_available);
    try std.testing.expect(!handoff.irq_registration_ready);
    try std.testing.expect(handoff.drvdata_ready);
    try std.testing.expect(!handoff.nowayout);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, handoff.restart_priority);
    try std.testing.expect(handoff.stop_on_reboot);
    try std.testing.expect(handoff.can_stop);
    try std.testing.expectEqual(@as(u32, 16), handoff.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), handoff.pretimeout_sec);
    try std.testing.expect(handoff.imported_running_state);
    try std.testing.expect(!handoff.needs_timeout_programming);
}

test "dw_wdt platform handoff stays blocked-but-reviewable when drvdata or irq wiring is absent" {
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

    try std.testing.expectEqual(dw_wdt.TopSource.custom, handoff.top_source);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.default_selection, handoff.timeout_origin);
    try std.testing.expectEqual(@as(u32, 1_000), handoff.rate_hz);
    try std.testing.expect(!handoff.reset_control_available);
    try std.testing.expect(!handoff.irq_registration_ready);
    try std.testing.expect(!handoff.drvdata_ready);
    try std.testing.expect(handoff.nowayout);
    try std.testing.expect(handoff.stop_on_reboot);
    try std.testing.expect(!handoff.can_stop);
    try std.testing.expectEqual(@as(u32, 12), handoff.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), handoff.pretimeout_sec);
    try std.testing.expect(!handoff.imported_running_state);
    try std.testing.expect(handoff.needs_timeout_programming);
}

test "dw_wdt verify keeps custom timeout matrix ordering and nearest-top selection explicit" {
    const custom_tops = [_]u32{
        20_000, 4_000,  8_000,  12_000,
        16_000, 24_000, 28_000, 32_000,
        36_000, 40_000, 44_000, 48_000,
        52_000, 56_000, 60_000, 64_000,
    };

    var watchdog = try dw_wdt.DwWdtLab.initCustomTops(1_000, false, custom_tops);
    const windows = watchdog.timeoutWindows();
    try std.testing.expectEqual(@as(usize, dw_wdt.num_tops), windows.len);
    try std.testing.expectEqual(@as(u32, 1), windows[0].top_val);
    try std.testing.expectEqual(@as(u32, 4), windows[0].sec);
    try std.testing.expectEqual(@as(u32, 15), windows[15].top_val);
    try std.testing.expectEqual(@as(u32, 64), windows[15].sec);

    for (windows[1..], 1..) |window, idx| {
        const previous = windows[idx - 1];
        try std.testing.expect(window.sec >= previous.sec);
        if (window.sec == previous.sec) {
            try std.testing.expect(window.msec >= previous.msec);
        }
    }

    const probe = try watchdog.probeSummary(.{
        .requested_timeout_sec = 11,
    });
    try std.testing.expectEqual(dw_wdt.TopSource.custom, probe.top_source);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.default_selection, probe.timeout_origin);
    try std.testing.expectEqual(@as(u32, 12), probe.timeout_sec);
    try std.testing.expect(probe.stop_on_reboot);
    try std.testing.expect(!probe.hardware_running);
}

test "dw_wdt verify keeps teardown split between reset-controlled and unstoppable hardware" {
    var stoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = try stoppable.setResponseMode(.irq);
    _ = try stoppable.setTimeout(9);
    _ = try stoppable.start();
    _ = stoppable.setCurrentCount(3 * 65_536);
    _ = stoppable.setInterruptPending(true);

    const stopped_remove = stoppable.removeSummary();
    try std.testing.expect(stopped_remove.reset_control_available);
    try std.testing.expect(stopped_remove.reset_assert_requested);
    try std.testing.expect(stopped_remove.hardware_running_before_remove);
    try std.testing.expect(!stopped_remove.hardware_running_after_remove);
    try std.testing.expect(!stopped_remove.running_after_remove);
    try std.testing.expect(!stopped_remove.interrupt_pending_after_remove);
    try std.testing.expect(!stopped_remove.remove_leaves_hardware_running);

    var unstoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    _ = try unstoppable.setResponseMode(.irq);
    _ = try unstoppable.setTimeout(9);
    _ = try unstoppable.start();
    _ = unstoppable.setCurrentCount(3 * 65_536);
    _ = unstoppable.setInterruptPending(true);

    const running_remove = unstoppable.removeSummary();
    try std.testing.expect(!running_remove.reset_control_available);
    try std.testing.expect(!running_remove.reset_assert_requested);
    try std.testing.expect(running_remove.hardware_running_before_remove);
    try std.testing.expect(running_remove.hardware_running_after_remove);
    try std.testing.expect(running_remove.running_after_remove);
    try std.testing.expect(running_remove.interrupt_pending_after_remove);
    try std.testing.expect(running_remove.remove_leaves_hardware_running);
}

test "dw_wdt verify keeps idle remove-time no-reset path from fabricating continued heartbeat" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);

    const idle_remove = watchdog.removeSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", idle_remove.anchor);
    try std.testing.expect(idle_remove.debugfs_clear_requested);
    try std.testing.expect(idle_remove.unregister_device_requested);
    try std.testing.expect(!idle_remove.reset_control_available);
    try std.testing.expect(!idle_remove.reset_assert_requested);
    try std.testing.expect(!idle_remove.hardware_running_before_remove);
    try std.testing.expect(!idle_remove.hardware_running_after_remove);
    try std.testing.expect(!idle_remove.running_after_remove);
    try std.testing.expect(!idle_remove.interrupt_pending_after_remove);
    try std.testing.expect(!idle_remove.remove_leaves_hardware_running);
}

test "dw_wdt verify keeps idle remove-time reset path from fabricating stale heartbeat" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);

    const idle_remove = watchdog.removeSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", idle_remove.anchor);
    try std.testing.expect(idle_remove.debugfs_clear_requested);
    try std.testing.expect(idle_remove.unregister_device_requested);
    try std.testing.expect(idle_remove.reset_control_available);
    try std.testing.expect(idle_remove.reset_assert_requested);
    try std.testing.expect(!idle_remove.hardware_running_before_remove);
    try std.testing.expect(!idle_remove.hardware_running_after_remove);
    try std.testing.expect(!idle_remove.running_after_remove);
    try std.testing.expect(!idle_remove.interrupt_pending_after_remove);
    try std.testing.expect(!idle_remove.remove_leaves_hardware_running);
}

test "dw_wdt verify keeps irq-mode teardown summaries aligned with stop failure semantics" {
    var unstoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    _ = try unstoppable.setResponseMode(.irq);
    _ = try unstoppable.setTimeout(9);
    _ = try unstoppable.start();
    _ = unstoppable.setCurrentCount(3 * 65_536);
    _ = unstoppable.setInterruptPending(true);

    const unstoppable_teardown = try unstoppable.teardownSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", unstoppable_teardown.anchor);
    try std.testing.expect(!unstoppable_teardown.can_stop);
    try std.testing.expect(unstoppable_teardown.running_before_teardown);
    try std.testing.expectEqual(@as(u32, 16), unstoppable_teardown.timeout_sec);
    try std.testing.expectEqual(dw_wdt.ResponseMode.irq, unstoppable_teardown.response_mode);
    try std.testing.expectEqual(dw_wdt.TeardownOutcome.continued_heartbeat, unstoppable_teardown.outcome);
    try std.testing.expect(unstoppable_teardown.stop_invoked);
    try std.testing.expect(!unstoppable_teardown.enable_bit_cleared);
    try std.testing.expect(!unstoppable_teardown.interrupt_cleared);
    try std.testing.expect(unstoppable_teardown.running_after_teardown);
    try std.testing.expect(unstoppable_teardown.hardware_running_after_teardown);
    var unstoppable_runtime = unstoppable.runtimeSnapshot();
    try std.testing.expectEqual(@as(u32, 8), unstoppable_runtime.pretimeout_sec);
    try std.testing.expectEqual(@as(u32, 3), unstoppable_runtime.time_left_sec);
    try std.testing.expectEqual(@as(u32, 3 * 65_536), unstoppable_runtime.registers.current_count);
    try std.testing.expect(unstoppable_runtime.interrupt_pending);
    unstoppable_runtime = try unstoppable.ping();
    try std.testing.expectEqual(dw_wdt.counter_restart_kick_value, unstoppable_runtime.registers.restart);
    try std.testing.expectEqual(@as(u32, 3 * 65_536), unstoppable_runtime.registers.current_count);
    try std.testing.expect(unstoppable_runtime.interrupt_pending);

    var stoppable = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = try stoppable.setResponseMode(.irq);
    _ = try stoppable.setTimeout(9);
    _ = try stoppable.start();
    _ = stoppable.setCurrentCount(3 * 65_536);
    _ = stoppable.setInterruptPending(true);

    const stoppable_teardown = try stoppable.teardownSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", stoppable_teardown.anchor);
    try std.testing.expect(stoppable_teardown.can_stop);
    try std.testing.expect(stoppable_teardown.running_before_teardown);
    try std.testing.expectEqual(@as(u32, 16), stoppable_teardown.timeout_sec);
    try std.testing.expectEqual(dw_wdt.ResponseMode.irq, stoppable_teardown.response_mode);
    try std.testing.expectEqual(dw_wdt.TeardownOutcome.reset_control_stop, stoppable_teardown.outcome);
    try std.testing.expect(stoppable_teardown.stop_invoked);
    try std.testing.expect(stoppable_teardown.enable_bit_cleared);
    try std.testing.expect(stoppable_teardown.interrupt_cleared);
    try std.testing.expect(!stoppable_teardown.running_after_teardown);
    try std.testing.expect(!stoppable_teardown.hardware_running_after_teardown);
    const stoppable_runtime = stoppable.runtimeSnapshot();
    try std.testing.expectEqual(@as(u32, 8), stoppable_runtime.pretimeout_sec);
    try std.testing.expectEqual(@as(u32, 0), stoppable_runtime.time_left_sec);
    try std.testing.expectEqual(@as(u32, 0), stoppable_runtime.registers.current_count);
    try std.testing.expect(!stoppable_runtime.interrupt_pending);
    try std.testing.expectError(error.WatchdogNotRunning, stoppable.ping());
}
