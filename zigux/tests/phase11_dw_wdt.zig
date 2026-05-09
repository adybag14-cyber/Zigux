const std = @import("std");
const dw_wdt = @import("dw_wdt");

test "phase11 dw_wdt platform resource preflight keeps named tclk and optional resources explicit" {
    const summary = dw_wdt.platformResourcePreflightSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = true,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
    });

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", summary.anchor);
    try std.testing.expectEqual(dw_wdt.TimerClockSelection.named_tclk, summary.timer_clock_selection);
    try std.testing.expect(!summary.uses_shared_clock_fallback);
    try std.testing.expect(summary.timer_clock_available);
    try std.testing.expectEqualStrings("devm_clk_get_enabled", summary.timer_clock_get_call);
    try std.testing.expect(summary.apb_clock_optional);
    try std.testing.expect(summary.apb_clock_present);
    try std.testing.expectEqualStrings("devm_clk_get_optional_enabled", summary.apb_clock_get_call);
    try std.testing.expect(summary.reset_control_available);
    try std.testing.expectEqualStrings("devm_reset_control_get_optional_shared", summary.reset_control_get_call);
    try std.testing.expect(summary.pretimeout_irq_optional);
    try std.testing.expect(summary.pretimeout_irq_present);
    try std.testing.expectEqualStrings("platform_get_irq_optional", summary.pretimeout_irq_call);
    try std.testing.expect(!summary.blocked_on_missing_timer_clock);
    try std.testing.expect(summary.keeps_platform_registration_blocked);
}

test "phase11 dw_wdt platform resource preflight keeps shared fallback and blocked no-clock paths explicit" {
    const fallback = dw_wdt.platformResourcePreflightSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = true,
        .has_pclk = false,
        .has_reset_control = false,
        .has_pretimeout_irq = false,
    });

    try std.testing.expectEqual(dw_wdt.TimerClockSelection.unnamed_shared_fallback, fallback.timer_clock_selection);
    try std.testing.expect(fallback.uses_shared_clock_fallback);
    try std.testing.expect(fallback.timer_clock_available);
    try std.testing.expect(fallback.apb_clock_optional);
    try std.testing.expect(!fallback.apb_clock_present);
    try std.testing.expect(!fallback.reset_control_available);
    try std.testing.expect(fallback.pretimeout_irq_optional);
    try std.testing.expect(!fallback.pretimeout_irq_present);
    try std.testing.expect(!fallback.blocked_on_missing_timer_clock);
    try std.testing.expect(fallback.keeps_platform_registration_blocked);

    const blocked = dw_wdt.platformResourcePreflightSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = false,
        .has_pclk = false,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
    });

    try std.testing.expectEqual(dw_wdt.TimerClockSelection.blocked_no_timer_clock, blocked.timer_clock_selection);
    try std.testing.expect(!blocked.uses_shared_clock_fallback);
    try std.testing.expect(!blocked.timer_clock_available);
    try std.testing.expect(blocked.apb_clock_optional);
    try std.testing.expect(!blocked.apb_clock_present);
    try std.testing.expect(blocked.reset_control_available);
    try std.testing.expect(blocked.pretimeout_irq_optional);
    try std.testing.expect(blocked.pretimeout_irq_present);
    try std.testing.expect(blocked.blocked_on_missing_timer_clock);
    try std.testing.expect(blocked.keeps_platform_registration_blocked);
}

test "phase11 dw_wdt keeps irq-mode non-stoppable stop parity explicit in the shared packet" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    _ = try watchdog.setResponseMode(.irq);
    _ = try watchdog.setTimeout(9);
    _ = try watchdog.start();
    _ = watchdog.setCurrentCount(3 * 65_536);
    _ = watchdog.setInterruptPending(true);

    const after_stop = watchdog.stop();
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", after_stop.anchor);
    try std.testing.expect(after_stop.running);
    try std.testing.expect(after_stop.hardware_running);
    try std.testing.expectEqual(dw_wdt.ResponseMode.irq, after_stop.response_mode);
    try std.testing.expectEqual(@as(u32, 16), after_stop.timeout_sec);
    try std.testing.expectEqual(@as(u32, 8), after_stop.pretimeout_sec);
    try std.testing.expect(after_stop.interrupt_pending);
    try std.testing.expectEqual(@as(u32, 3), after_stop.time_left_sec);
    try std.testing.expectEqual(@as(u32, 3 * 65_536), after_stop.registers.current_count);

    const after_ping = try watchdog.ping();
    try std.testing.expect(after_ping.running);
    try std.testing.expect(after_ping.hardware_running);
    try std.testing.expect(after_ping.interrupt_pending);
    try std.testing.expectEqual(@as(u32, 3), after_ping.time_left_sec);
    try std.testing.expectEqual(@as(u32, 3 * 65_536), after_ping.registers.current_count);
    try std.testing.expectEqual(dw_wdt.counter_restart_kick_value, after_ping.registers.restart);
}
