const std = @import("std");

const bcm2835_wdt = @import("bcm2835_wdt.zig");

test "bcm2835 verify helper keeps timeout gates and PM-base handoff readiness explicit" {
    try std.testing.expectError(error.TimeoutTooSmall, bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 0,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = false,
        .poweroff_handler_present = false,
        .parent_attached = true,
        .pm_base_present = true,
    }));

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
    try std.testing.expectEqual(@as(i32, bcm2835_wdt.restart_priority), ready.restart_priority_value);
    try std.testing.expect(ready.poweroff_handler_claimed);
    try std.testing.expect(!ready.poweroff_handler_conflict);
    try std.testing.expect(ready.blocked_on_live_platform_registration);
}

test "bcm2835 verify helper keeps poweroff ownership conflict and PM-base blockers distinct" {
    const conflict = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = true,
        .parent_attached = true,
        .pm_base_present = true,
    });
    try std.testing.expect(conflict.parent_attached);
    try std.testing.expect(conflict.parent_supplies_pm_base);
    try std.testing.expect(conflict.pm_base_handoff_ready);
    try std.testing.expect(conflict.register_device_requested);
    try std.testing.expect(!conflict.poweroff_handler_claimed);
    try std.testing.expect(conflict.poweroff_handler_conflict);
    try std.testing.expect(conflict.blocked_on_live_platform_registration);

    const blocked = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = false,
        .parent_attached = true,
        .pm_base_present = false,
    });
    try std.testing.expect(blocked.parent_attached);
    try std.testing.expect(!blocked.parent_supplies_pm_base);
    try std.testing.expect(blocked.pm_base_required);
    try std.testing.expect(!blocked.pm_base_handoff_ready);
    try std.testing.expect(!blocked.register_device_requested);
    try std.testing.expect(!blocked.poweroff_handler_claimed);
    try std.testing.expect(!blocked.poweroff_handler_conflict);
    try std.testing.expect(blocked.blocked_on_live_platform_registration);
}

test "bcm2835 verify helper keeps stop and poweroff snapshots reviewable" {
    var running = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    running.start();
    const stopped = running.stop();
    try std.testing.expectEqualStrings(bcm2835_wdt.anchor_path, stopped.anchor);
    try std.testing.expect(stopped.running_before_stop);
    try std.testing.expect(!stopped.running_after_stop);
    try std.testing.expect(!stopped.running_after_poweroff);
    try std.testing.expect(stopped.reset_register_written);
    try std.testing.expect(!stopped.halt_partition_requested);
    try std.testing.expect(!stopped.restart_path_reused);

    var claimed = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    claimed.importBootloaderRunning();
    const claimed_poweroff = claimed.poweroff(true);
    try std.testing.expect(claimed_poweroff.halt_partition_requested);
    try std.testing.expect(claimed_poweroff.restart_path_reused);
    try std.testing.expectEqual(@as(u32, bcm2835_wdt.restart_timeout_ticks), claimed_poweroff.programmed_ticks);
    try std.testing.expect(claimed_poweroff.full_reset_armed);
    try std.testing.expect(claimed_poweroff.running_after_poweroff);

    var unclaimed = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    const unclaimed_poweroff = unclaimed.poweroff(false);
    try std.testing.expect(!unclaimed_poweroff.halt_partition_requested);
    try std.testing.expect(unclaimed_poweroff.restart_path_reused);
    try std.testing.expectEqual(@as(u32, 0), unclaimed_poweroff.programmed_ticks);
    try std.testing.expect(!unclaimed_poweroff.full_reset_armed);
    try std.testing.expect(!unclaimed_poweroff.running_after_poweroff);
}
