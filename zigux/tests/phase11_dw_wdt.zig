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
