const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio watchdog keeps nowayout policy summary directly reviewable" {
    const stoppable = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    const stoppable_policy = stoppable.nowayoutPolicySummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", stoppable_policy.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, stoppable_policy.hw_algo);
    try std.testing.expect(!stoppable_policy.always_running);
    try std.testing.expect(!stoppable_policy.nowayout);
    try std.testing.expect(stoppable_policy.stop_allowed_by_watchdog_core);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, stoppable_policy.disposition_if_stop_requested);
    try std.testing.expect(stoppable_policy.driver_stop_invoked);

    const guarded = try gpio_wdt.GpioWatchdogLab.init(.level, 400, true);
    const guarded_policy = guarded.nowayoutPolicySummary(true);
    const keep_running_policy = guarded.nowayoutPolicySummary(false);

    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, guarded_policy.hw_algo);
    try std.testing.expect(guarded_policy.always_running);
    try std.testing.expect(guarded_policy.nowayout);
    try std.testing.expect(!guarded_policy.stop_allowed_by_watchdog_core);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, guarded_policy.disposition_if_stop_requested);
    try std.testing.expect(!guarded_policy.driver_stop_invoked);

    try std.testing.expect(keep_running_policy.always_running);
    try std.testing.expect(!keep_running_policy.nowayout);
    try std.testing.expect(keep_running_policy.stop_allowed_by_watchdog_core);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.kept_running, keep_running_policy.disposition_if_stop_requested);
    try std.testing.expect(keep_running_policy.driver_stop_invoked);
}
