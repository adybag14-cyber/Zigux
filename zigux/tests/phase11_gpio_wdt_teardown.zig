const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio_wdt teardown summary records blocked, stopped, and kept-running outcomes" {
    var blocked_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, false);
    const blocked = try blocked_watchdog.teardownSummary(true);
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", blocked.anchor);
    try std.testing.expect(blocked.running_before_teardown);
    try std.testing.expect(blocked.line_is_output_before_teardown);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, blocked.disposition);
    try std.testing.expect(!blocked.stop_allowed_by_watchdog_core);
    try std.testing.expect(!blocked.driver_stop_invoked);
    try std.testing.expect(blocked.running_after_teardown);
    try std.testing.expect(blocked.line_is_output_after_teardown);
    try std.testing.expectEqual(@as(usize, 0), blocked.disable_count);

    var stoppable_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, false);
    const stopped = try stoppable_watchdog.teardownSummary(false);
    try std.testing.expect(stopped.running_before_teardown);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, stopped.disposition);
    try std.testing.expect(stopped.stop_allowed_by_watchdog_core);
    try std.testing.expect(stopped.driver_stop_invoked);
    try std.testing.expect(!stopped.running_after_teardown);
    try std.testing.expect(!stopped.line_is_output_after_teardown);
    try std.testing.expect(stopped.line_state_after_teardown);
    try std.testing.expectEqual(@as(usize, 1), stopped.disable_count);

    var always_running_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 50, true);
    const kept_running = try always_running_watchdog.teardownSummary(false);
    try std.testing.expect(kept_running.running_before_teardown);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.kept_running, kept_running.disposition);
    try std.testing.expect(kept_running.stop_allowed_by_watchdog_core);
    try std.testing.expect(kept_running.driver_stop_invoked);
    try std.testing.expect(kept_running.running_after_teardown);
    try std.testing.expect(kept_running.line_is_output_after_teardown);
    try std.testing.expect(!kept_running.line_state_after_teardown);
    try std.testing.expectEqual(@as(usize, 0), kept_running.disable_count);
}
