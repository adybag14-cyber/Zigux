const std = @import("std");
const bcm2835_wdt = @import("bcm2835_wdt");

test "phase11 bcm2835 watchdog replay keeps timeout helpers explicit" {
    try std.testing.expectEqual(@as(u32, 15), bcm2835_wdt.maxTimeoutSeconds());
    try std.testing.expectEqual(@as(u32, 15_999), bcm2835_wdt.maxHeartbeatMilliseconds());
    try std.testing.expectEqual(@as(u32, 12 << bcm2835_wdt.watchdog_tick_shift), try bcm2835_wdt.secondsToWatchdogTicks(12));
    try std.testing.expectEqual(@as(u32, 10), bcm2835_wdt.watchdogTicksToSeconds(10 << bcm2835_wdt.watchdog_tick_shift));
    try std.testing.expectError(error.TimeoutTooSmall, bcm2835_wdt.secondsToWatchdogTicks(0));
    try std.testing.expectError(error.TimeoutTooLarge, bcm2835_wdt.secondsToWatchdogTicks(16));
}

test "phase11 bcm2835 watchdog replay keeps probe ownership and poweroff conflict distinct" {
    const claimed = try bcm2835_wdt.summarizeProbe(.{
        .heartbeat_sec = 8,
        .nowayout = true,
        .bootloader_running = true,
        .system_power_controller = true,
        .poweroff_handler_present = false,
    });
    try std.testing.expectEqualStrings(bcm2835_wdt.anchor_path, claimed.anchor);
    try std.testing.expect(claimed.bootloader_running);
    try std.testing.expect(claimed.sets_hw_running_bit);
    try std.testing.expect(claimed.poweroff_handler_claimed);
    try std.testing.expect(!claimed.poweroff_handler_conflict);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", claimed.registration_call);

    const conflicting = try bcm2835_wdt.summarizeProbe(.{
        .heartbeat_sec = 8,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = true,
    });
    try std.testing.expect(!conflicting.poweroff_handler_claimed);
    try std.testing.expect(conflicting.poweroff_handler_conflict);
    try std.testing.expect(!conflicting.sets_hw_running_bit);
}

test "phase11 bcm2835 watchdog replay keeps platform handoff readiness and poweroff claim blocking explicit" {
    const ready = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = true,
        .bootloader_running = true,
        .system_power_controller = true,
        .poweroff_handler_present = false,
        .parent_attached = true,
        .pm_base_present = true,
    });
    try std.testing.expectEqualStrings(bcm2835_wdt.anchor_path, ready.anchor);
    try std.testing.expect(ready.parent_attached);
    try std.testing.expect(ready.parent_supplies_pm_base);
    try std.testing.expect(ready.pm_base_required);
    try std.testing.expect(ready.pm_base_handoff_ready);
    try std.testing.expect(ready.timeout_init_requested);
    try std.testing.expect(ready.register_device_requested);
    try std.testing.expect(ready.stop_on_reboot_requested);
    try std.testing.expect(ready.poweroff_handler_claimed);
    try std.testing.expect(!ready.poweroff_handler_conflict);
    try std.testing.expect(ready.blocked_on_live_platform_registration);

    const blocked = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = true,
        .parent_attached = true,
        .pm_base_present = false,
    });
    try std.testing.expect(blocked.parent_attached);
    try std.testing.expect(!blocked.parent_supplies_pm_base);
    try std.testing.expect(blocked.pm_base_required);
    try std.testing.expect(!blocked.pm_base_handoff_ready);
    try std.testing.expect(blocked.timeout_init_requested);
    try std.testing.expect(!blocked.register_device_requested);
    try std.testing.expect(blocked.stop_on_reboot_requested);
    try std.testing.expect(!blocked.poweroff_handler_claimed);
    try std.testing.expect(blocked.poweroff_handler_conflict);
    try std.testing.expect(blocked.blocked_on_live_platform_registration);

    const claim_pending = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = false,
        .parent_attached = true,
        .pm_base_present = false,
    });
    try std.testing.expect(claim_pending.parent_attached);
    try std.testing.expect(!claim_pending.parent_supplies_pm_base);
    try std.testing.expect(claim_pending.pm_base_required);
    try std.testing.expect(!claim_pending.pm_base_handoff_ready);
    try std.testing.expect(claim_pending.timeout_init_requested);
    try std.testing.expect(!claim_pending.register_device_requested);
    try std.testing.expect(claim_pending.stop_on_reboot_requested);
    try std.testing.expect(claim_pending.poweroff_handler_claimed);
    try std.testing.expect(!claim_pending.poweroff_handler_conflict);
    try std.testing.expect(claim_pending.blocked_on_live_platform_registration);
}

test "phase11 bcm2835 watchdog replay keeps start stop restart and poweroff lifecycle explicit" {
    var watchdog = try bcm2835_wdt.Bcm2835WdtLab.init(5);

    const started = try watchdog.start();
    try std.testing.expectEqualStrings(bcm2835_wdt.anchor_path, started.anchor);
    try std.testing.expect(started.running_after_start);
    try std.testing.expect(started.full_reset_armed);
    try std.testing.expectEqual(@as(u32, 5), watchdog.getTimeleftSeconds());

    const stopped = watchdog.stop();
    try std.testing.expect(stopped.reset_register_written);
    try std.testing.expect(stopped.running_before_stop);
    try std.testing.expect(!stopped.running_after_stop);
    try std.testing.expect(!stopped.full_reset_armed_after_stop);

    try watchdog.importBootloaderRunning();
    try std.testing.expectEqual(@as(u32, 5), watchdog.getTimeleftSeconds());

    const restart_summary = watchdog.restart();
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.restart_timeout_ticks), restart_summary.programmed_ticks);
    try std.testing.expect(restart_summary.full_reset_armed);
    try std.testing.expectEqual(@as(u32, 1), restart_summary.delay_msec);
    try std.testing.expect(restart_summary.running_after_restart);

    const poweroff_summary = watchdog.poweroff(true);
    try std.testing.expect(poweroff_summary.halt_partition_requested);
    try std.testing.expect(poweroff_summary.restart_path_reused);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.restart_timeout_ticks), poweroff_summary.programmed_ticks);
    try std.testing.expect(poweroff_summary.full_reset_armed);
    try std.testing.expect(poweroff_summary.poweroff_handler_claimed);
    try std.testing.expect(poweroff_summary.running_after_poweroff);
}

test "phase11 bcm2835 watchdog replay keeps remove cleanup ownership explicit" {
    var claimed = try bcm2835_wdt.Bcm2835WdtLab.init(5);
    _ = try claimed.start();
    const claimed_remove = claimed.remove(true);
    try std.testing.expect(claimed_remove.unregister_device_requested);
    try std.testing.expect(claimed_remove.poweroff_handler_release_requested);
    try std.testing.expect(claimed_remove.running_before_remove);
    try std.testing.expect(!claimed_remove.running_after_remove);
    try std.testing.expect(!claimed_remove.full_reset_armed_after_remove);
    try std.testing.expect(!claimed_remove.halt_partition_requested_after_remove);
    try std.testing.expectEqual(bcm2835_wdt.RemoveState.running_remove, claimed_remove.state);

    var unclaimed = try bcm2835_wdt.Bcm2835WdtLab.init(5);
    const unclaimed_remove = unclaimed.remove(false);
    try std.testing.expect(unclaimed_remove.unregister_device_requested);
    try std.testing.expect(!unclaimed_remove.poweroff_handler_release_requested);
    try std.testing.expect(!unclaimed_remove.running_before_remove);
    try std.testing.expect(!unclaimed_remove.running_after_remove);
    try std.testing.expectEqual(bcm2835_wdt.RemoveState.inactive_remove, unclaimed_remove.state);
}
