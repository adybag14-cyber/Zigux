const std = @import("std");
const testing = std.testing;
const bcm2835_wdt = @import("bcm2835_wdt.zig");

test "bcm2835 watchdog claimed poweroff handoff reaches ready poweroff and owned teardown" {
    const lab = try bcm2835_wdt.Bcm2835WatchdogLab.init(8);

    const registration = lab.registrationOutcomeSummary(true, false, true);
    try testing.expect(registration.registration_succeeded);
    try testing.expect(registration.poweroff_handler_claimed);
    try testing.expect(registration.poweroff_handler_present_after_probe);
    try testing.expect(registration.poweroff_handler_owned_by_driver);

    const poweroff = lab.poweroffSummary(
        registration.system_power_controller,
        registration.poweroff_handler_present_after_probe,
        registration.poweroff_handler_owned_by_driver,
    );
    try testing.expect(poweroff.poweroff_path_ready);
    try testing.expect(poweroff.halt_partition_requested);
    try testing.expect(poweroff.restart_armed);

    const remove = lab.removeAfterRegistrationSummary(true, false, true);
    try testing.expect(remove.clear_poweroff_handler_requested);
    try testing.expect(!remove.poweroff_handler_left_in_place);
}

test "bcm2835 watchdog conflict and failed registration keep poweroff boundaries explicit" {
    const lab = try bcm2835_wdt.Bcm2835WatchdogLab.init(8);

    const conflict = lab.registrationOutcomeSummary(true, true, true);
    try testing.expect(conflict.registration_succeeded);
    try testing.expect(conflict.poweroff_handler_conflict);
    try testing.expect(conflict.poweroff_handler_present_after_probe);
    try testing.expect(!conflict.poweroff_handler_owned_by_driver);

    const conflict_poweroff = lab.poweroffSummary(
        conflict.system_power_controller,
        conflict.poweroff_handler_present_after_probe,
        conflict.poweroff_handler_owned_by_driver,
    );
    try testing.expect(!conflict_poweroff.poweroff_path_ready);
    try testing.expect(!conflict_poweroff.halt_partition_requested);
    try testing.expect(!conflict_poweroff.restart_armed);

    const conflict_remove = lab.removeAfterRegistrationSummary(true, true, true);
    try testing.expect(!conflict_remove.clear_poweroff_handler_requested);
    try testing.expect(conflict_remove.poweroff_handler_left_in_place);

    const failed = lab.registrationOutcomeSummary(true, false, false);
    try testing.expect(failed.probe_error_returned);
    try testing.expect(!failed.poweroff_handler_present_after_probe);
    try testing.expect(!failed.poweroff_handler_owned_by_driver);

    const failed_poweroff = lab.poweroffSummary(
        failed.system_power_controller,
        failed.poweroff_handler_present_after_probe,
        failed.poweroff_handler_owned_by_driver,
    );
    try testing.expect(!failed_poweroff.poweroff_path_ready);

    const failed_remove = lab.removeAfterRegistrationSummary(true, false, false);
    try testing.expect(!failed_remove.clear_poweroff_handler_requested);
    try testing.expect(!failed_remove.poweroff_handler_left_in_place);
}
