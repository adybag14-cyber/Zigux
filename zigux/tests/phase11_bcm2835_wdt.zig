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

test "phase11 bcm2835_wdt keeps watchdog metadata and ops surface reviewable" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(12);
    const metadata = watchdog.watchdogMetadataSummary();

    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", metadata.anchor);
    try std.testing.expectEqualStrings("Broadcom BCM2835 Watchdog timer", metadata.identity);
    try std.testing.expect(metadata.supports_set_timeout);
    try std.testing.expect(metadata.supports_magic_close);
    try std.testing.expect(metadata.supports_keepalive_ping);
    try std.testing.expect(metadata.start_op_ready);
    try std.testing.expect(metadata.stop_op_ready);
    try std.testing.expect(metadata.get_timeleft_op_ready);
    try std.testing.expect(metadata.restart_op_ready);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.min_timeout_sec), metadata.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.max_timeout_sec), metadata.default_timeout_sec);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.max_timeout_sec), metadata.max_timeout_sec);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.max_hw_heartbeat_ms), metadata.max_hw_heartbeat_ms);
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

    runtime = watchdog.loadRegisters(.{
        .rstc = 0x1234_5608,
        .wdog = 0,
    });
    try std.testing.expect(!runtime.running);

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

    runtime = watchdog.stop();
    try std.testing.expect(!runtime.running);
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password | bcm2835_wdt.pm_rstc_reset,
        runtime.registers.rstc,
    );
    try std.testing.expectEqual(@as(u32, 0), runtime.time_left_sec);
}

test "phase11 bcm2835_wdt keepalive ping rearms the current timeout without losing halt state" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);
    _ = watchdog.loadRegisters(.{
        .rstc = 0x1234_5608,
        .rsts = bcm2835_wdt.pm_rsts_halt,
        .wdog = bcm2835_wdt.secondsToTicks(3),
    });

    const runtime = watchdog.ping();
    try std.testing.expect(runtime.running);
    try std.testing.expect(!runtime.restart_armed);
    try std.testing.expect(runtime.halt_partition_requested);
    try std.testing.expectEqual(@as(u32, 9), runtime.timeout_sec);
    try std.testing.expectEqual(@as(u32, 9), runtime.time_left_sec);
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
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.pm_rsts_halt), runtime.registers.rsts);
}

test "phase11 bcm2835_wdt setTimeout updates the timeout and rearms the watchdog window" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(4);
    _ = watchdog.loadRegisters(.{
        .rstc = 0xabcd_1208,
        .rsts = 0x10,
        .wdog = bcm2835_wdt.secondsToTicks(2),
    });

    const runtime = try watchdog.setTimeout(11);
    try std.testing.expect(runtime.running);
    try std.testing.expectEqual(@as(u32, 11), runtime.timeout_sec);
    try std.testing.expectEqual(@as(u32, 11), runtime.time_left_sec);
    try std.testing.expectEqual(@as(u32, 11), watchdog.configSnapshot().timeout_sec);
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password | bcm2835_wdt.secondsToTicks(11),
        runtime.registers.wdog,
    );
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password |
            (0xabcd_1208 & bcm2835_wdt.pm_rstc_wrcfg_clr) |
            bcm2835_wdt.pm_rstc_wrcfg_full_reset,
        runtime.registers.rstc,
    );
    try std.testing.expectEqual(@as(u32, 0x10), runtime.registers.rsts);
    try std.testing.expect(!runtime.restart_armed);
}

test "phase11 bcm2835_wdt setTimeout keeps the old timeout when validation fails" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(6);
    _ = watchdog.loadRegisters(.{
        .rstc = bcm2835_wdt.pm_rstc_wrcfg_full_reset,
        .wdog = bcm2835_wdt.secondsToTicks(6),
    });

    try std.testing.expectError(error.TimeoutTooLarge, watchdog.setTimeout(16));
    const runtime = watchdog.runtimeSnapshot();
    try std.testing.expect(runtime.running);
    try std.testing.expectEqual(@as(u32, 6), runtime.timeout_sec);
    try std.testing.expectEqual(@as(u32, 6), runtime.time_left_sec);
    try std.testing.expectEqual(
        @as(u32, bcm2835_wdt.secondsToTicks(6)),
        runtime.registers.wdog,
    );
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

test "phase11 bcm2835_wdt registration outcome summary keeps probe failure and poweroff claim blocking reviewable" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    const success = watchdog.registrationOutcomeSummary(true, true, false);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", success.anchor);
    try std.testing.expect(success.register_device_requested);
    try std.testing.expect(success.register_device_succeeded);
    try std.testing.expect(!success.register_device_failed);
    try std.testing.expect(success.system_power_controller);
    try std.testing.expect(!success.poweroff_handler_present);
    try std.testing.expect(success.poweroff_handler_claimed);
    try std.testing.expect(!success.poweroff_handler_conflict);
    try std.testing.expect(!success.poweroff_handler_claim_blocked_by_registration_failure);
    try std.testing.expect(!success.probe_returns_error);

    const conflict = watchdog.registrationOutcomeSummary(true, true, true);
    try std.testing.expect(conflict.register_device_requested);
    try std.testing.expect(conflict.register_device_succeeded);
    try std.testing.expect(!conflict.register_device_failed);
    try std.testing.expect(conflict.system_power_controller);
    try std.testing.expect(conflict.poweroff_handler_present);
    try std.testing.expect(!conflict.poweroff_handler_claimed);
    try std.testing.expect(conflict.poweroff_handler_conflict);
    try std.testing.expect(!conflict.poweroff_handler_claim_blocked_by_registration_failure);
    try std.testing.expect(!conflict.probe_returns_error);

    const failed = watchdog.registrationOutcomeSummary(true, false, false);
    try std.testing.expect(failed.register_device_requested);
    try std.testing.expect(!failed.register_device_succeeded);
    try std.testing.expect(failed.register_device_failed);
    try std.testing.expect(failed.system_power_controller);
    try std.testing.expect(!failed.poweroff_handler_present);
    try std.testing.expect(!failed.poweroff_handler_claimed);
    try std.testing.expect(!failed.poweroff_handler_conflict);
    try std.testing.expect(failed.poweroff_handler_claim_blocked_by_registration_failure);
    try std.testing.expect(failed.probe_returns_error);

    const passive_failure = watchdog.registrationOutcomeSummary(false, false, false);
    try std.testing.expect(passive_failure.register_device_requested);
    try std.testing.expect(!passive_failure.register_device_succeeded);
    try std.testing.expect(passive_failure.register_device_failed);
    try std.testing.expect(!passive_failure.system_power_controller);
    try std.testing.expect(!passive_failure.poweroff_handler_present);
    try std.testing.expect(!passive_failure.poweroff_handler_claimed);
    try std.testing.expect(!passive_failure.poweroff_handler_conflict);
    try std.testing.expect(!passive_failure.poweroff_handler_claim_blocked_by_registration_failure);
    try std.testing.expect(passive_failure.probe_returns_error);
}

test "phase11 bcm2835_wdt platform handoff summary keeps parent and PM-base prerequisites reviewable" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    const ready = watchdog.platformHandoffSummary(true, true, true, true, false);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", ready.anchor);
    try std.testing.expect(ready.bootloader_running);
    try std.testing.expect(ready.nowayout);
    try std.testing.expect(ready.parent_attached);
    try std.testing.expect(ready.parent_supplies_pm_base);
    try std.testing.expect(ready.pm_base_required);
    try std.testing.expect(ready.pm_base_handoff_ready);
    try std.testing.expect(ready.watchdog_drvdata_set);
    try std.testing.expect(ready.watchdog_parent_set);
    try std.testing.expect(ready.timeout_init_requested);
    try std.testing.expect(ready.register_device_requested);
    try std.testing.expect(!ready.register_device_blocked_by_missing_pm_base);
    try std.testing.expect(ready.stop_on_reboot);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.restart_priority), ready.restart_priority);
    try std.testing.expect(ready.system_power_controller);
    try std.testing.expect(!ready.poweroff_handler_present);
    try std.testing.expect(ready.poweroff_handler_claimed);
    try std.testing.expect(!ready.poweroff_handler_conflict);

    const conflict = watchdog.platformHandoffSummary(true, false, true, true, true);
    try std.testing.expect(conflict.bootloader_running);
    try std.testing.expect(!conflict.nowayout);
    try std.testing.expect(conflict.parent_attached);
    try std.testing.expect(conflict.parent_supplies_pm_base);
    try std.testing.expect(conflict.pm_base_required);
    try std.testing.expect(conflict.pm_base_handoff_ready);
    try std.testing.expect(conflict.watchdog_drvdata_set);
    try std.testing.expect(conflict.watchdog_parent_set);
    try std.testing.expect(conflict.timeout_init_requested);
    try std.testing.expect(conflict.register_device_requested);
    try std.testing.expect(!conflict.register_device_blocked_by_missing_pm_base);
    try std.testing.expect(conflict.stop_on_reboot);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.restart_priority), conflict.restart_priority);
    try std.testing.expect(conflict.system_power_controller);
    try std.testing.expect(conflict.poweroff_handler_present);
    try std.testing.expect(!conflict.poweroff_handler_claimed);
    try std.testing.expect(conflict.poweroff_handler_conflict);

    const blocked = watchdog.platformHandoffSummary(false, false, true, false, true);
    try std.testing.expect(!blocked.bootloader_running);
    try std.testing.expect(!blocked.nowayout);
    try std.testing.expect(blocked.parent_attached);
    try std.testing.expect(!blocked.parent_supplies_pm_base);
    try std.testing.expect(blocked.pm_base_required);
    try std.testing.expect(!blocked.pm_base_handoff_ready);
    try std.testing.expect(!blocked.watchdog_drvdata_set);
    try std.testing.expect(blocked.watchdog_parent_set);
    try std.testing.expect(blocked.timeout_init_requested);
    try std.testing.expect(!blocked.register_device_requested);
    try std.testing.expect(blocked.register_device_blocked_by_missing_pm_base);
    try std.testing.expect(blocked.stop_on_reboot);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.restart_priority), blocked.restart_priority);
    try std.testing.expect(blocked.system_power_controller);
    try std.testing.expect(blocked.poweroff_handler_present);
    try std.testing.expect(!blocked.poweroff_handler_claimed);
    try std.testing.expect(blocked.poweroff_handler_conflict);

    const missing_pm_base_without_handler = watchdog.platformHandoffSummary(false, false, true, false, false);
    try std.testing.expect(!missing_pm_base_without_handler.pm_base_handoff_ready);
    try std.testing.expect(!missing_pm_base_without_handler.register_device_requested);
    try std.testing.expect(missing_pm_base_without_handler.register_device_blocked_by_missing_pm_base);
    try std.testing.expect(!missing_pm_base_without_handler.poweroff_handler_present);
    try std.testing.expect(!missing_pm_base_without_handler.poweroff_handler_claimed);
    try std.testing.expect(!missing_pm_base_without_handler.poweroff_handler_conflict);
}

test "phase11 bcm2835_wdt poweroff summary only arms the halt reset when bcm2835 owns the shared callback" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);
    _ = watchdog.loadRegisters(.{
        .rstc = 0x1234_5678,
        .rsts = 0x0000_0004,
    });

    const owned = watchdog.poweroffSummary(true, true, true);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", owned.anchor);
    try std.testing.expect(owned.system_power_controller);
    try std.testing.expect(owned.poweroff_handler_present);
    try std.testing.expect(owned.poweroff_handler_owned_by_driver);
    try std.testing.expect(owned.poweroff_callback_ready);
    try std.testing.expect(owned.poweroff_path_available);
    try std.testing.expect(!owned.blocked_without_system_power_controller);
    try std.testing.expect(!owned.blocked_without_poweroff_handler);
    try std.testing.expect(!owned.blocked_by_poweroff_handler_conflict);
    try std.testing.expect(owned.full_reset_requested);
    try std.testing.expect(owned.restart_armed);
    try std.testing.expect(owned.halt_partition_requested);
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password | bcm2835_wdt.restart_ticks,
        owned.registers.wdog,
    );
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password |
            (0x1234_5678 & bcm2835_wdt.pm_rstc_wrcfg_clr) |
            bcm2835_wdt.pm_rstc_wrcfg_full_reset,
        owned.registers.rstc,
    );
    try std.testing.expectEqual(
        @as(u32, 0x0000_0004 | bcm2835_wdt.pm_password | bcm2835_wdt.pm_rsts_halt),
        owned.registers.rsts,
    );

    var conflict_watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);
    _ = conflict_watchdog.loadRegisters(.{
        .rstc = 0xabcd_1000,
        .rsts = 0x0000_0008,
    });
    const conflict = conflict_watchdog.poweroffSummary(true, true, false);
    try std.testing.expect(conflict.system_power_controller);
    try std.testing.expect(conflict.poweroff_handler_present);
    try std.testing.expect(!conflict.poweroff_handler_owned_by_driver);
    try std.testing.expect(!conflict.poweroff_callback_ready);
    try std.testing.expect(!conflict.poweroff_path_available);
    try std.testing.expect(!conflict.blocked_without_system_power_controller);
    try std.testing.expect(!conflict.blocked_without_poweroff_handler);
    try std.testing.expect(conflict.blocked_by_poweroff_handler_conflict);
    try std.testing.expect(!conflict.full_reset_requested);
    try std.testing.expect(!conflict.restart_armed);
    try std.testing.expect(!conflict.halt_partition_requested);
    try std.testing.expectEqual(@as(u32, 0xabcd_1000), conflict.registers.rstc);
    try std.testing.expectEqual(@as(u32, 0x0000_0008), conflict.registers.rsts);

    var missing_watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);
    _ = missing_watchdog.loadRegisters(.{
        .rstc = 0,
        .rsts = 0x0000_0010,
    });
    const missing = missing_watchdog.poweroffSummary(true, false, false);
    try std.testing.expect(missing.system_power_controller);
    try std.testing.expect(!missing.poweroff_handler_present);
    try std.testing.expect(!missing.poweroff_handler_owned_by_driver);
    try std.testing.expect(!missing.poweroff_callback_ready);
    try std.testing.expect(!missing.poweroff_path_available);
    try std.testing.expect(!missing.blocked_without_system_power_controller);
    try std.testing.expect(missing.blocked_without_poweroff_handler);
    try std.testing.expect(!missing.blocked_by_poweroff_handler_conflict);
    try std.testing.expectEqual(@as(u32, 0x0000_0010), missing.registers.rsts);

    var passive_watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);
    _ = passive_watchdog.loadRegisters(.{
        .rstc = 0,
        .rsts = 0x0000_0020,
    });
    const passive = passive_watchdog.poweroffSummary(false, true, true);
    try std.testing.expect(!passive.system_power_controller);
    try std.testing.expect(passive.poweroff_handler_present);
    try std.testing.expect(passive.poweroff_handler_owned_by_driver);
    try std.testing.expect(!passive.poweroff_callback_ready);
    try std.testing.expect(!passive.poweroff_path_available);
    try std.testing.expect(passive.blocked_without_system_power_controller);
    try std.testing.expect(!passive.blocked_without_poweroff_handler);
    try std.testing.expect(!passive.blocked_by_poweroff_handler_conflict);
    try std.testing.expectEqual(@as(u32, 0x0000_0020), passive.registers.rsts);
}

test "phase11 bcm2835_wdt remove summary only clears the shared poweroff handler when bcm2835 owns it" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    const owned = watchdog.removeSummary(true, true, true);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", owned.anchor);
    try std.testing.expect(owned.system_power_controller);
    try std.testing.expect(owned.poweroff_handler_present);
    try std.testing.expect(owned.poweroff_handler_owned_by_driver);
    try std.testing.expect(owned.remove_callback_ready);
    try std.testing.expect(owned.watchdog_teardown_managed_by_devm);
    try std.testing.expect(owned.remove_callback_scope_limited_to_poweroff_owner);
    try std.testing.expect(owned.clear_poweroff_handler_requested);
    try std.testing.expect(!owned.clear_poweroff_handler_blocked_by_conflict);
    try std.testing.expect(!owned.clear_poweroff_handler_skipped_without_system_power_controller);
    try std.testing.expect(!owned.clear_poweroff_handler_skipped_without_handler);
    try std.testing.expect(!owned.poweroff_handler_left_in_place);

    const conflict = watchdog.removeSummary(true, true, false);
    try std.testing.expect(conflict.system_power_controller);
    try std.testing.expect(conflict.poweroff_handler_present);
    try std.testing.expect(!conflict.poweroff_handler_owned_by_driver);
    try std.testing.expect(conflict.remove_callback_ready);
    try std.testing.expect(conflict.watchdog_teardown_managed_by_devm);
    try std.testing.expect(conflict.remove_callback_scope_limited_to_poweroff_owner);
    try std.testing.expect(!conflict.clear_poweroff_handler_requested);
    try std.testing.expect(conflict.clear_poweroff_handler_blocked_by_conflict);
    try std.testing.expect(!conflict.clear_poweroff_handler_skipped_without_system_power_controller);
    try std.testing.expect(!conflict.clear_poweroff_handler_skipped_without_handler);
    try std.testing.expect(conflict.poweroff_handler_left_in_place);

    const not_controller = watchdog.removeSummary(false, true, true);
    try std.testing.expect(!not_controller.system_power_controller);
    try std.testing.expect(not_controller.poweroff_handler_present);
    try std.testing.expect(not_controller.poweroff_handler_owned_by_driver);
    try std.testing.expect(not_controller.remove_callback_ready);
    try std.testing.expect(not_controller.watchdog_teardown_managed_by_devm);
    try std.testing.expect(not_controller.remove_callback_scope_limited_to_poweroff_owner);
    try std.testing.expect(!not_controller.clear_poweroff_handler_requested);
    try std.testing.expect(!not_controller.clear_poweroff_handler_blocked_by_conflict);
    try std.testing.expect(not_controller.clear_poweroff_handler_skipped_without_system_power_controller);
    try std.testing.expect(!not_controller.clear_poweroff_handler_skipped_without_handler);
    try std.testing.expect(not_controller.poweroff_handler_left_in_place);

    const passive_conflict = watchdog.removeSummary(false, true, false);
    try std.testing.expect(!passive_conflict.system_power_controller);
    try std.testing.expect(passive_conflict.poweroff_handler_present);
    try std.testing.expect(!passive_conflict.poweroff_handler_owned_by_driver);
    try std.testing.expect(passive_conflict.remove_callback_ready);
    try std.testing.expect(passive_conflict.watchdog_teardown_managed_by_devm);
    try std.testing.expect(passive_conflict.remove_callback_scope_limited_to_poweroff_owner);
    try std.testing.expect(!passive_conflict.clear_poweroff_handler_requested);
    try std.testing.expect(!passive_conflict.clear_poweroff_handler_blocked_by_conflict);
    try std.testing.expect(passive_conflict.clear_poweroff_handler_skipped_without_system_power_controller);
    try std.testing.expect(!passive_conflict.clear_poweroff_handler_skipped_without_handler);
    try std.testing.expect(passive_conflict.poweroff_handler_left_in_place);

    const passive_absent = watchdog.removeSummary(false, false, false);
    try std.testing.expect(!passive_absent.system_power_controller);
    try std.testing.expect(!passive_absent.poweroff_handler_present);
    try std.testing.expect(!passive_absent.poweroff_handler_owned_by_driver);
    try std.testing.expect(passive_absent.remove_callback_ready);
    try std.testing.expect(passive_absent.watchdog_teardown_managed_by_devm);
    try std.testing.expect(passive_absent.remove_callback_scope_limited_to_poweroff_owner);
    try std.testing.expect(!passive_absent.clear_poweroff_handler_requested);
    try std.testing.expect(!passive_absent.clear_poweroff_handler_blocked_by_conflict);
    try std.testing.expect(!passive_absent.clear_poweroff_handler_skipped_without_system_power_controller);
    try std.testing.expect(!passive_absent.clear_poweroff_handler_skipped_without_handler);
    try std.testing.expect(!passive_absent.poweroff_handler_left_in_place);

    const absent = watchdog.removeSummary(true, false, false);
    try std.testing.expect(absent.system_power_controller);
    try std.testing.expect(!absent.poweroff_handler_present);
    try std.testing.expect(!absent.poweroff_handler_owned_by_driver);
    try std.testing.expect(absent.remove_callback_ready);
    try std.testing.expect(absent.watchdog_teardown_managed_by_devm);
    try std.testing.expect(absent.remove_callback_scope_limited_to_poweroff_owner);
    try std.testing.expect(!absent.clear_poweroff_handler_requested);
    try std.testing.expect(!absent.clear_poweroff_handler_blocked_by_conflict);
    try std.testing.expect(!absent.clear_poweroff_handler_skipped_without_system_power_controller);
    try std.testing.expect(absent.clear_poweroff_handler_skipped_without_handler);
    try std.testing.expect(!absent.poweroff_handler_left_in_place);
}
