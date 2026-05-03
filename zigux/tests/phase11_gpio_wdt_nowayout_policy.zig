const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio_wdt nowayout policy summary keeps module parameter bookkeeping explicit" {
    const summary = gpio_wdt.GpioWatchdogLab.nowayoutPolicySummary();
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expectEqualStrings("nowayout", summary.module_param_name);
    try std.testing.expectEqual(gpio_wdt.NowayoutDefaultSource.watchdog_nowayout, summary.default_source);
    try std.testing.expect(summary.module_param_declared);
    try std.testing.expect(summary.module_param_is_bool);
    try std.testing.expect(summary.default_follows_watchdog_nowayout);
    try std.testing.expect(summary.applied_via_watchdog_set_nowayout);
    try std.testing.expect(summary.bounded_to_summary_bookkeeping);
}
