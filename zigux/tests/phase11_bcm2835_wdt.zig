const std = @import("std");
const bcm2835_wdt = @import("bcm2835_wdt");

test "phase11 bcm2835 watchdog starter keeps timeout and restart constants reviewable" {
    try std.testing.expectEqual(@as(u32, 1), bcm2835_wdt.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, 15), bcm2835_wdt.max_timeout_sec);
    try std.testing.expectEqual(@as(i32, 128), bcm2835_wdt.restart_priority);
    try std.testing.expectEqual(@as(u32, 10), bcm2835_wdt.restart_timeout_ticks);
    try std.testing.expectError(error.TimeoutTooSmall, bcm2835_wdt.Bcm2835WdtLab.init(0));
    try std.testing.expectError(error.TimeoutTooLarge, bcm2835_wdt.Bcm2835WdtLab.init(16));
}

test "phase11 bcm2835 watchdog verify keeps PM-base readiness and ownership explicit" {
    const ready = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
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
    try std.testing.expectEqual(@as(i32, bcm2835_wdt.restart_priority), ready.restart_priority_value);
    try std.testing.expect(ready.poweroff_handler_claimed);
    try std.testing.expect(!ready.poweroff_handler_conflict);
    try std.testing.expect(ready.blocked_on_live_platform_registration);

    const blocked = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
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
    try std.testing.expect(!blocked.stop_on_reboot_requested);
    try std.testing.expect(!blocked.poweroff_handler_claimed);
    try std.testing.expect(!blocked.poweroff_handler_conflict);
    try std.testing.expect(blocked.blocked_on_live_platform_registration);
}

test "phase11 bcm2835 watchdog restart proof keeps the dedicated restart path explicit" {
    var running = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    running.start();
    const restarted = running.restart();
    try std.testing.expectEqualStrings(bcm2835_wdt.anchor_path, restarted.anchor);
    try std.testing.expect(restarted.running_before_restart);
    try std.testing.expect(restarted.running_after_restart);
    try std.testing.expect(restarted.full_reset_armed_after_restart);
    try std.testing.expect(!restarted.halt_partition_requested);
    try std.testing.expect(restarted.restart_register_written);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.restart_timeout_ticks), restarted.programmed_ticks);

    var idle = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    const idle_restart = idle.restart();
    try std.testing.expect(!idle_restart.running_before_restart);
    try std.testing.expect(idle_restart.running_after_restart);
    try std.testing.expect(idle_restart.full_reset_armed_after_restart);
    try std.testing.expect(idle_restart.restart_register_written);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.restart_timeout_ticks), idle_restart.programmed_ticks);
}

test "phase11 bcm2835 watchdog verify keeps poweroff ownership distinct" {
    var claimed = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    const claimed_poweroff = claimed.poweroff(true);
    try std.testing.expectEqualStrings(bcm2835_wdt.anchor_path, claimed_poweroff.anchor);
    try std.testing.expect(claimed_poweroff.halt_partition_requested);
    try std.testing.expect(claimed_poweroff.restart_path_reused);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.restart_timeout_ticks), claimed_poweroff.programmed_ticks);
    try std.testing.expect(claimed_poweroff.full_reset_armed);
    try std.testing.expect(claimed_poweroff.running_after_poweroff);

    var unclaimed = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    const unclaimed_poweroff = unclaimed.poweroff(false);
    try std.testing.expect(!unclaimed_poweroff.halt_partition_requested);
    try std.testing.expect(!unclaimed_poweroff.restart_path_reused);
    try std.testing.expectEqual(@as(u32, 0), unclaimed_poweroff.programmed_ticks);
    try std.testing.expect(!unclaimed_poweroff.full_reset_armed);
    try std.testing.expect(!unclaimed_poweroff.running_after_poweroff);

    unclaimed.start();
    const stopped = unclaimed.stop();
    try std.testing.expect(stopped.reset_register_written);
    try std.testing.expect(stopped.running_before_stop);
    try std.testing.expect(!stopped.running_after_stop);
    try std.testing.expect(!stopped.full_reset_armed_after_stop);
}

test "phase11 bcm2835 watchdog direct replay keeps teardown ownership splits explicit" {
    var owned = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    owned.start();
    const owned_teardown = owned.summarizeTeardown(.{
        .nowayout = false,
        .system_power_controller = true,
        .poweroff_owner = .bcm2835,
        .restart_handler_registered = true,
    });
    try std.testing.expect(owned_teardown.running_before_teardown);
    try std.testing.expect(!owned_teardown.running_after_teardown);
    try std.testing.expect(owned_teardown.poweroff_handler_released);
    try std.testing.expect(!owned_teardown.foreign_poweroff_handler_preserved);
    try std.testing.expect(owned_teardown.restart_handler_unregistered);
    try std.testing.expect(owned_teardown.reset_register_written);
    try std.testing.expect(owned_teardown.blocked_on_live_remove_callback);

    var foreign = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    foreign.start();
    const foreign_teardown = foreign.summarizeTeardown(.{
        .nowayout = true,
        .system_power_controller = true,
        .poweroff_owner = .foreign,
        .restart_handler_registered = false,
    });
    try std.testing.expect(foreign_teardown.running_before_teardown);
    try std.testing.expect(foreign_teardown.running_after_teardown);
    try std.testing.expect(!foreign_teardown.poweroff_handler_released);
    try std.testing.expect(foreign_teardown.foreign_poweroff_handler_preserved);
    try std.testing.expect(!foreign_teardown.restart_handler_unregistered);
    try std.testing.expect(!foreign_teardown.reset_register_written);
    try std.testing.expect(foreign_teardown.blocked_on_live_remove_callback);
}
