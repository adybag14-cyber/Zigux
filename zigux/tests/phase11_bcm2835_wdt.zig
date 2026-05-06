const std = @import("std");
const bcm2835_wdt = @import("bcm2835_wdt");

test "phase11 bcm2835_wdt reports bounded timeout limits and descriptor state" {
    const descriptor = bcm2835_wdt.Bcm2835WatchdogLab.descriptor();
    try std.testing.expectEqualStrings("bcm2835_wdt_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_simple_driver_starter);
    try std.testing.expect(!descriptor.touches_platform_registration);
    try std.testing.expect(!descriptor.touches_poweroff_plumbing);

    try std.testing.expectEqual(@as(u32, 15), bcm2835_wdt.max_timeout_sec);
    try std.testing.expectEqual(@as(u32, 15_999), bcm2835_wdt.max_hw_heartbeat_ms);
    try std.testing.expectEqual(@as(u32, 128), bcm2835_wdt.restart_priority);
    try std.testing.expectError(error.TimeoutTooSmall, bcm2835_wdt.Bcm2835WatchdogLab.init(0));
    try std.testing.expectError(error.TimeoutTooLarge, bcm2835_wdt.Bcm2835WatchdogLab.init(16));

    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(12);
    const config = watchdog.configSnapshot();
    try std.testing.expectEqual(@as(u32, 12), config.timeout_sec);
    try std.testing.expectEqual(@as(u32, 15), config.max_timeout_sec);
    try std.testing.expectEqual(@as(u32, 15_999), config.max_hw_heartbeat_ms);
}

test "phase11 bcm2835_wdt mirrors running-state detection and start or stop register writes" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    var runtime = watchdog.loadRegisters(.{
        .rstc = bcm2835_wdt.pm_rstc_wrcfg_full_reset,
        .wdog = bcm2835_wdt.secondsToTicks(7),
    });
    try std.testing.expect(runtime.running);
    try std.testing.expectEqual(@as(u32, 7), runtime.time_left_sec);
    try std.testing.expect(runtime.full_reset_requested);
    try std.testing.expectEqual(@as(u32, 7), watchdog.getTimeleft());

    runtime = watchdog.loadRegisters(.{
        .rstc = 0x1234_5608,
        .wdog = 0,
    });
    try std.testing.expect(!runtime.running);
    try std.testing.expectEqual(@as(u32, 0), watchdog.getTimeleft());

    runtime = watchdog.start();
    try std.testing.expect(runtime.running);
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password | bcm2835_wdt.secondsToTicks(9),
        runtime.registers.wdog,
    );
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password |
            (0x1234_5608 & bcm2835_wdt.pm_rstc_wrcfg_clr) |
            bcm2835_wdt.pm_rstc_wrcfg_full_reset,
        runtime.registers.rstc,
    );
    try std.testing.expectEqual(@as(u32, 9), runtime.time_left_sec);
    try std.testing.expectEqual(@as(u32, 9), watchdog.getTimeleft());

    runtime = watchdog.stop();
    try std.testing.expect(!runtime.running);
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password | bcm2835_wdt.pm_rstc_reset,
        runtime.registers.rstc,
    );
    try std.testing.expectEqual(@as(u32, 0), runtime.time_left_sec);
    try std.testing.expectEqual(@as(u32, 0), watchdog.getTimeleft());
}

test "phase11 bcm2835_wdt restart path uses the short reset timeout and preserves halt partition state" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(5);
    _ = watchdog.loadRegisters(.{
        .rstc = 0xabcd_1234,
        .rsts = bcm2835_wdt.pm_rsts_halt,
    });

    const runtime = watchdog.armRestart();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.restart_armed);
    try std.testing.expect(runtime.halt_partition_requested);
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password | bcm2835_wdt.restart_ticks,
        runtime.registers.wdog,
    );
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password |
            (0xabcd_1234 & bcm2835_wdt.pm_rstc_wrcfg_clr) |
            bcm2835_wdt.pm_rstc_wrcfg_full_reset,
        runtime.registers.rstc,
    );
    try std.testing.expectEqual(@as(u32, 0), runtime.time_left_sec);
    try std.testing.expectEqual(@as(u32, 0), watchdog.getTimeleft());
}

test "phase11 bcm2835_wdt probe summary keeps probe-time watchdog-core bookkeeping reviewable" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    const running_probe = watchdog.probeSummary(true, true, true);
    try std.testing.expectEqual(@as(u32, 9), running_probe.timeout_sec);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.max_timeout_sec), running_probe.max_timeout_sec);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.max_hw_heartbeat_ms), running_probe.max_hw_heartbeat_ms);
    try std.testing.expect(running_probe.nowayout);
    try std.testing.expect(running_probe.bootloader_running);
    try std.testing.expect(running_probe.framework_marks_hw_running);
    try std.testing.expect(running_probe.framework_ping_expected);
    try std.testing.expect(running_probe.heartbeat_init_requested);
    try std.testing.expect(running_probe.parent_attached);
    try std.testing.expect(running_probe.stop_on_reboot);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.restart_priority), running_probe.restart_priority);
    try std.testing.expect(running_probe.system_power_controller);

    const stopped_probe = watchdog.probeSummary(false, false, false);
    try std.testing.expect(!stopped_probe.nowayout);
    try std.testing.expect(!stopped_probe.bootloader_running);
    try std.testing.expect(!stopped_probe.framework_marks_hw_running);
    try std.testing.expect(!stopped_probe.framework_ping_expected);
    try std.testing.expect(stopped_probe.heartbeat_init_requested);
    try std.testing.expect(stopped_probe.parent_attached);
    try std.testing.expect(stopped_probe.stop_on_reboot);
    try std.testing.expect(!stopped_probe.system_power_controller);
}

test "phase11 bcm2835_wdt registration summary records watchdog registration and poweroff ownership outcomes" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    const claimed = watchdog.registrationSummary(true, true, false);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", claimed.anchor);
    try std.testing.expect(claimed.bootloader_running);
    try std.testing.expect(claimed.framework_marks_hw_running);
    try std.testing.expect(claimed.register_device_requested);
    try std.testing.expect(claimed.stop_on_reboot);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.restart_priority), claimed.restart_priority);
    try std.testing.expect(claimed.system_power_controller);
    try std.testing.expect(!claimed.poweroff_handler_present);
    try std.testing.expect(claimed.poweroff_handler_claimed);
    try std.testing.expect(!claimed.poweroff_handler_conflict);

    const conflict = watchdog.registrationSummary(true, true, true);
    try std.testing.expect(conflict.poweroff_handler_present);
    try std.testing.expect(!conflict.poweroff_handler_claimed);
    try std.testing.expect(conflict.poweroff_handler_conflict);

    const not_controller = watchdog.registrationSummary(false, false, false);
    try std.testing.expect(!not_controller.bootloader_running);
    try std.testing.expect(!not_controller.framework_marks_hw_running);
    try std.testing.expect(not_controller.register_device_requested);
    try std.testing.expect(!not_controller.system_power_controller);
    try std.testing.expect(!not_controller.poweroff_handler_present);
    try std.testing.expect(!not_controller.poweroff_handler_claimed);
    try std.testing.expect(!not_controller.poweroff_handler_conflict);
}

test "phase11 bcm2835_wdt registration outcome keeps poweroff ownership and failure paths explicit" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    const claimed = watchdog.registrationOutcomeSummary(true, false, true);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", claimed.anchor);
    try std.testing.expect(claimed.system_power_controller);
    try std.testing.expect(claimed.registration_succeeded);
    try std.testing.expect(claimed.register_device_requested);
    try std.testing.expect(!claimed.probe_error_returned);
    try std.testing.expect(!claimed.poweroff_handler_present);
    try std.testing.expect(claimed.poweroff_handler_claimed);
    try std.testing.expect(!claimed.poweroff_handler_conflict);
    try std.testing.expect(!claimed.poweroff_handler_left_in_place);

    const failed_claim = watchdog.registrationOutcomeSummary(true, false, false);
    try std.testing.expect(failed_claim.system_power_controller);
    try std.testing.expect(!failed_claim.registration_succeeded);
    try std.testing.expect(failed_claim.register_device_requested);
    try std.testing.expect(failed_claim.probe_error_returned);
    try std.testing.expect(!failed_claim.poweroff_handler_present);
    try std.testing.expect(!failed_claim.poweroff_handler_claimed);
    try std.testing.expect(!failed_claim.poweroff_handler_conflict);
    try std.testing.expect(!failed_claim.poweroff_handler_left_in_place);

    const conflict = watchdog.registrationOutcomeSummary(true, true, true);
    try std.testing.expect(conflict.system_power_controller);
    try std.testing.expect(conflict.registration_succeeded);
    try std.testing.expect(conflict.register_device_requested);
    try std.testing.expect(!conflict.probe_error_returned);
    try std.testing.expect(conflict.poweroff_handler_present);
    try std.testing.expect(!conflict.poweroff_handler_claimed);
    try std.testing.expect(conflict.poweroff_handler_conflict);
    try std.testing.expect(conflict.poweroff_handler_left_in_place);

    const non_controller_failure = watchdog.registrationOutcomeSummary(false, false, false);
    try std.testing.expect(!non_controller_failure.system_power_controller);
    try std.testing.expect(!non_controller_failure.registration_succeeded);
    try std.testing.expect(non_controller_failure.register_device_requested);
    try std.testing.expect(non_controller_failure.probe_error_returned);
    try std.testing.expect(!non_controller_failure.poweroff_handler_present);
    try std.testing.expect(!non_controller_failure.poweroff_handler_claimed);
    try std.testing.expect(!non_controller_failure.poweroff_handler_conflict);
    try std.testing.expect(!non_controller_failure.poweroff_handler_left_in_place);
}

test "phase11 bcm2835_wdt platform handoff summary keeps PM-base and poweroff-claim boundaries explicit" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    const claimed = watchdog.platformHandoffSummary(true, true, false);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", claimed.anchor);
    try std.testing.expect(claimed.system_power_controller);
    try std.testing.expect(claimed.parent_attached);
    try std.testing.expect(claimed.pm_base_available);
    try std.testing.expect(claimed.drvdata_ready);
    try std.testing.expect(claimed.register_device_requested);
    try std.testing.expect(!claimed.poweroff_handler_present);
    try std.testing.expect(claimed.poweroff_handler_claimed);
    try std.testing.expect(!claimed.poweroff_handler_conflict);

    const conflict = watchdog.platformHandoffSummary(true, true, true);
    try std.testing.expect(conflict.system_power_controller);
    try std.testing.expect(conflict.pm_base_available);
    try std.testing.expect(conflict.drvdata_ready);
    try std.testing.expect(conflict.poweroff_handler_present);
    try std.testing.expect(!conflict.poweroff_handler_claimed);
    try std.testing.expect(conflict.poweroff_handler_conflict);

    const blocked = watchdog.platformHandoffSummary(false, false, false);
    try std.testing.expect(!blocked.system_power_controller);
    try std.testing.expect(blocked.parent_attached);
    try std.testing.expect(!blocked.pm_base_available);
    try std.testing.expect(!blocked.drvdata_ready);
    try std.testing.expect(blocked.register_device_requested);
    try std.testing.expect(!blocked.poweroff_handler_present);
    try std.testing.expect(!blocked.poweroff_handler_claimed);
    try std.testing.expect(!blocked.poweroff_handler_conflict);
}

test "phase11 bcm2835_wdt poweroff summary keeps callback ownership and restart arming reviewable" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    const ready = watchdog.poweroffSummary(true, true, true);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", ready.anchor);
    try std.testing.expect(ready.system_power_controller);
    try std.testing.expect(ready.poweroff_handler_present);
    try std.testing.expect(ready.poweroff_handler_owned_by_driver);
    try std.testing.expect(ready.poweroff_path_ready);
    try std.testing.expect(ready.halt_partition_requested);
    try std.testing.expect(ready.restart_armed);

    const conflict = watchdog.poweroffSummary(true, true, false);
    try std.testing.expect(conflict.system_power_controller);
    try std.testing.expect(conflict.poweroff_handler_present);
    try std.testing.expect(!conflict.poweroff_handler_owned_by_driver);
    try std.testing.expect(!conflict.poweroff_path_ready);
    try std.testing.expect(!conflict.halt_partition_requested);
    try std.testing.expect(!conflict.restart_armed);

    const blocked = watchdog.poweroffSummary(false, false, false);
    try std.testing.expect(!blocked.system_power_controller);
    try std.testing.expect(!blocked.poweroff_handler_present);
    try std.testing.expect(!blocked.poweroff_handler_owned_by_driver);
    try std.testing.expect(!blocked.poweroff_path_ready);
    try std.testing.expect(!blocked.halt_partition_requested);
    try std.testing.expect(!blocked.restart_armed);
}

test "phase11 bcm2835_wdt remove summary only clears the shared poweroff handler when bcm2835 owns it" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    const owned = watchdog.removeSummary(true, true, true);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", owned.anchor);
    try std.testing.expect(owned.system_power_controller);
    try std.testing.expect(owned.poweroff_handler_present);
    try std.testing.expect(owned.poweroff_handler_owned_by_driver);
    try std.testing.expect(owned.clear_poweroff_handler_requested);
    try std.testing.expect(!owned.poweroff_handler_left_in_place);

    const conflict = watchdog.removeSummary(true, true, false);
    try std.testing.expect(conflict.system_power_controller);
    try std.testing.expect(conflict.poweroff_handler_present);
    try std.testing.expect(!conflict.poweroff_handler_owned_by_driver);
    try std.testing.expect(!conflict.clear_poweroff_handler_requested);
    try std.testing.expect(conflict.poweroff_handler_left_in_place);

    const not_controller = watchdog.removeSummary(false, true, true);
    try std.testing.expect(!not_controller.system_power_controller);
    try std.testing.expect(not_controller.poweroff_handler_present);
    try std.testing.expect(not_controller.poweroff_handler_owned_by_driver);
    try std.testing.expect(!not_controller.clear_poweroff_handler_requested);
    try std.testing.expect(not_controller.poweroff_handler_left_in_place);

    const absent = watchdog.removeSummary(true, false, false);
    try std.testing.expect(absent.system_power_controller);
    try std.testing.expect(!absent.poweroff_handler_present);
    try std.testing.expect(!absent.poweroff_handler_owned_by_driver);
    try std.testing.expect(!absent.clear_poweroff_handler_requested);
    try std.testing.expect(!absent.poweroff_handler_left_in_place);
}
