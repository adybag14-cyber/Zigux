const std = @import("std");

const testing = std.testing;
const bcm2835_wdt = @import("bcm2835_wdt.zig");

test "phase11 bcm2835 watchdog verify keeps PM-base readiness and ownership explicit" {
    const ready = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = true,
        .bootloader_running = true,
        .system_power_controller = true,
        .poweroff_handler_present = false,
        .parent_attached = true,
        .pm_base_present = true,
    });

    try testing.expectEqualStrings(bcm2835_wdt.anchor_path, ready.anchor);
    try testing.expect(ready.parent_attached);
    try testing.expect(ready.parent_supplies_pm_base);
    try testing.expect(ready.pm_base_required);
    try testing.expect(ready.pm_base_handoff_ready);
    try testing.expect(ready.timeout_init_requested);
    try testing.expect(ready.register_device_requested);
    try testing.expect(ready.stop_on_reboot_requested);
    try testing.expectEqual(@as(i32, bcm2835_wdt.restart_priority), ready.restart_priority_value);
    try testing.expect(ready.poweroff_handler_claimed);
    try testing.expect(!ready.poweroff_handler_conflict);
    try testing.expect(ready.blocked_on_live_platform_registration);

    const blocked = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = true,
        .parent_attached = true,
        .pm_base_present = false,
    });

    try testing.expect(blocked.parent_attached);
    try testing.expect(!blocked.parent_supplies_pm_base);
    try testing.expect(blocked.pm_base_required);
    try testing.expect(!blocked.pm_base_handoff_ready);
    try testing.expect(blocked.timeout_init_requested);
    try testing.expect(!blocked.register_device_requested);
    try testing.expect(blocked.stop_on_reboot_requested);
    try testing.expect(!blocked.poweroff_handler_claimed);
    try testing.expect(blocked.poweroff_handler_conflict);
    try testing.expect(blocked.blocked_on_live_platform_registration);

    const claim_pending = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = false,
        .parent_attached = true,
        .pm_base_present = false,
    });

    try testing.expect(claim_pending.parent_attached);
    try testing.expect(!claim_pending.parent_supplies_pm_base);
    try testing.expect(claim_pending.pm_base_required);
    try testing.expect(!claim_pending.pm_base_handoff_ready);
    try testing.expect(claim_pending.timeout_init_requested);
    try testing.expect(!claim_pending.register_device_requested);
    try testing.expect(claim_pending.stop_on_reboot_requested);
    try testing.expect(claim_pending.poweroff_handler_claimed);
    try testing.expect(!claim_pending.poweroff_handler_conflict);
    try testing.expect(claim_pending.blocked_on_live_platform_registration);

    const conflicting_ready = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = true,
        .parent_attached = true,
        .pm_base_present = true,
    });

    try testing.expect(conflicting_ready.parent_attached);
    try testing.expect(conflicting_ready.parent_supplies_pm_base);
    try testing.expect(conflicting_ready.pm_base_required);
    try testing.expect(conflicting_ready.pm_base_handoff_ready);
    try testing.expect(conflicting_ready.timeout_init_requested);
    try testing.expect(conflicting_ready.register_device_requested);
    try testing.expect(conflicting_ready.stop_on_reboot_requested);
    try testing.expect(!conflicting_ready.poweroff_handler_claimed);
    try testing.expect(conflicting_ready.poweroff_handler_conflict);
    try testing.expect(conflicting_ready.blocked_on_live_platform_registration);
}

test "phase11 bcm2835 watchdog verify keeps poweroff ownership distinct" {
    var claimed = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    try claimed.importBootloaderRunning();
    const claimed_poweroff = claimed.poweroff(true);

    try testing.expectEqualStrings(bcm2835_wdt.anchor_path, claimed_poweroff.anchor);
    try testing.expect(claimed_poweroff.halt_partition_requested);
    try testing.expect(claimed_poweroff.restart_path_reused);
    try testing.expectEqual(@as(u32, bcm2835_wdt.restart_timeout_ticks), claimed_poweroff.programmed_ticks);
    try testing.expect(claimed_poweroff.full_reset_armed);
    try testing.expect(claimed_poweroff.poweroff_handler_claimed);
    try testing.expect(claimed_poweroff.running_after_poweroff);

    var unclaimed = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    const unclaimed_poweroff = unclaimed.poweroff(false);

    try testing.expect(unclaimed_poweroff.halt_partition_requested);
    try testing.expect(unclaimed_poweroff.restart_path_reused);
    try testing.expectEqual(@as(u32, bcm2835_wdt.restart_timeout_ticks), unclaimed_poweroff.programmed_ticks);
    try testing.expect(unclaimed_poweroff.full_reset_armed);
    try testing.expect(!unclaimed_poweroff.poweroff_handler_claimed);
    try testing.expect(unclaimed_poweroff.running_after_poweroff);

    const stopped = unclaimed.stop();
    try testing.expect(stopped.reset_register_written);
    try testing.expect(stopped.running_before_stop);
    try testing.expect(!stopped.running_after_stop);
    try testing.expect(!stopped.full_reset_armed_after_stop);
}
