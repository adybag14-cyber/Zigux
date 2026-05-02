const std = @import("std");
const dw_wdt = @import("dw_wdt");

test "phase11 dw_wdt suspend-resume summary preserves running IRQ state and pretimeout bookkeeping" {
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

test "phase11 dw_wdt suspend-resume summary keeps idle reset-mode state bounded without optional apb clock" {
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
