const std = @import("std");
const bcm2835_wdt = @import("../../drivers/watchdog/bcm2835_wdt.zig");

test "phase11 bcm2835_wdt registration outcome summary only reaches poweroff ownership after watchdog registration succeeds" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    const claimed = watchdog.registrationOutcomeSummary(true, true, false);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", claimed.anchor);
    try std.testing.expect(claimed.register_device_requested);
    try std.testing.expect(claimed.register_device_succeeded);
    try std.testing.expect(!claimed.register_device_failed);
    try std.testing.expect(!claimed.probe_returns_error);
    try std.testing.expect(claimed.system_power_controller);
    try std.testing.expect(!claimed.poweroff_handler_present);
    try std.testing.expect(claimed.poweroff_handler_claimed);
    try std.testing.expect(!claimed.poweroff_handler_conflict);
    try std.testing.expect(!claimed.poweroff_handler_claim_blocked_by_registration_failure);

    const conflict = watchdog.registrationOutcomeSummary(true, true, true);
    try std.testing.expect(conflict.register_device_requested);
    try std.testing.expect(conflict.register_device_succeeded);
    try std.testing.expect(!conflict.register_device_failed);
    try std.testing.expect(!conflict.probe_returns_error);
    try std.testing.expect(conflict.system_power_controller);
    try std.testing.expect(conflict.poweroff_handler_present);
    try std.testing.expect(!conflict.poweroff_handler_claimed);
    try std.testing.expect(conflict.poweroff_handler_conflict);
    try std.testing.expect(!conflict.poweroff_handler_claim_blocked_by_registration_failure);

    const failed_without_handler = watchdog.registrationOutcomeSummary(true, false, false);
    try std.testing.expect(failed_without_handler.register_device_requested);
    try std.testing.expect(!failed_without_handler.register_device_succeeded);
    try std.testing.expect(failed_without_handler.register_device_failed);
    try std.testing.expect(failed_without_handler.probe_returns_error);
    try std.testing.expect(failed_without_handler.system_power_controller);
    try std.testing.expect(!failed_without_handler.poweroff_handler_present);
    try std.testing.expect(!failed_without_handler.poweroff_handler_claimed);
    try std.testing.expect(!failed_without_handler.poweroff_handler_conflict);
    try std.testing.expect(failed_without_handler.poweroff_handler_claim_blocked_by_registration_failure);

    const failed_with_handler = watchdog.registrationOutcomeSummary(true, false, true);
    try std.testing.expect(failed_with_handler.register_device_requested);
    try std.testing.expect(!failed_with_handler.register_device_succeeded);
    try std.testing.expect(failed_with_handler.register_device_failed);
    try std.testing.expect(failed_with_handler.probe_returns_error);
    try std.testing.expect(failed_with_handler.system_power_controller);
    try std.testing.expect(failed_with_handler.poweroff_handler_present);
    try std.testing.expect(!failed_with_handler.poweroff_handler_claimed);
    try std.testing.expect(!failed_with_handler.poweroff_handler_conflict);
    try std.testing.expect(failed_with_handler.poweroff_handler_claim_blocked_by_registration_failure);

    const non_controller_failure = watchdog.registrationOutcomeSummary(false, false, false);
    try std.testing.expect(non_controller_failure.register_device_requested);
    try std.testing.expect(!non_controller_failure.register_device_succeeded);
    try std.testing.expect(non_controller_failure.register_device_failed);
    try std.testing.expect(non_controller_failure.probe_returns_error);
    try std.testing.expect(!non_controller_failure.system_power_controller);
    try std.testing.expect(!non_controller_failure.poweroff_handler_present);
    try std.testing.expect(!non_controller_failure.poweroff_handler_claimed);
    try std.testing.expect(!non_controller_failure.poweroff_handler_conflict);
    try std.testing.expect(!non_controller_failure.poweroff_handler_claim_blocked_by_registration_failure);
}
