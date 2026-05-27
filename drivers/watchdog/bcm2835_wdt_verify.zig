const std = @import("std");

const bcm2835_wdt = @import("bcm2835_wdt.zig");

test "bcm2835 verify helper keeps timeout gates and PM-base handoff readiness explicit" {
    try std.testing.expectError(error.TimeoutTooSmall, bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 0,
        .system_power_controller = false,
        .poweroff_handler_present = false,
        .parent_attached = true,
        .pm_base_present = true,
    }));

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
}

test "bcm2835 verify helper keeps timeout ceiling and non-controller poweroff branch explicit" {
    try std.testing.expectError(error.TimeoutTooLarge, bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = bcm2835_wdt.max_timeout_sec + 1,
        .system_power_controller = false,
        .poweroff_handler_present = false,
        .parent_attached = true,
        .pm_base_present = true,
    }));

    const no_controller = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .system_power_controller = false,
        .poweroff_handler_present = true,
        .parent_attached = true,
        .pm_base_present = true,
    });
    try std.testing.expect(no_controller.parent_attached);
    try std.testing.expect(no_controller.parent_supplies_pm_base);
    try std.testing.expect(no_controller.pm_base_handoff_ready);
    try std.testing.expect(no_controller.register_device_requested);
    try std.testing.expect(!no_controller.poweroff_handler_claimed);
    try std.testing.expect(!no_controller.poweroff_handler_conflict);
    try std.testing.expect(no_controller.blocked_on_live_platform_registration);
}

test "bcm2835 verify helper keeps poweroff ownership conflict and PM-base blockers distinct" {
    const conflict = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
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

test "bcm2835 verify helper keeps detached parent from claiming PM-base ownership" {
    const detached_parent = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .system_power_controller = true,
        .poweroff_handler_present = false,
        .parent_attached = false,
        .pm_base_present = true,
    });

    try std.testing.expect(!detached_parent.parent_attached);
    try std.testing.expect(!detached_parent.parent_supplies_pm_base);
    try std.testing.expect(detached_parent.pm_base_required);
    try std.testing.expect(!detached_parent.pm_base_handoff_ready);
    try std.testing.expect(!detached_parent.register_device_requested);
    try std.testing.expect(!detached_parent.poweroff_handler_claimed);
    try std.testing.expect(!detached_parent.poweroff_handler_conflict);
    try std.testing.expect(detached_parent.blocked_on_live_platform_registration);
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

test "bcm2835 verify helper keeps teardown release and foreign-owner preservation distinct" {
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

test "bcm2835 verify helper keeps non-controller teardown from claiming poweroff release" {
    var detached = try bcm2835_wdt.Bcm2835WdtLab.init(8);
    detached.start();
    const teardown = detached.summarizeTeardown(.{
        .nowayout = false,
        .system_power_controller = false,
        .poweroff_owner = .bcm2835,
        .restart_handler_registered = true,
    });

    try std.testing.expect(teardown.running_before_teardown);
    try std.testing.expect(!teardown.running_after_teardown);
    try std.testing.expect(!teardown.poweroff_handler_released);
    try std.testing.expect(!teardown.foreign_poweroff_handler_preserved);
    try std.testing.expect(teardown.restart_handler_unregistered);
    try std.testing.expect(teardown.reset_register_written);
    try std.testing.expect(teardown.blocked_on_live_remove_callback);
}
