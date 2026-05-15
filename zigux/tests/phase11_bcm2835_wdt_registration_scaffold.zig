const std = @import("std");
const bcm2835_wdt = @import("bcm2835_wdt");

test "phase11 bcm2835 registration scaffold keeps ready PM-base handoff explicit" {
    const summary = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = true,
        .bootloader_running = true,
        .system_power_controller = true,
        .poweroff_handler_present = false,
        .parent_attached = true,
        .pm_base_present = true,
    });

    try std.testing.expectEqualStrings(bcm2835_wdt.anchor_path, summary.anchor);
    try std.testing.expect(summary.parent_attached);
    try std.testing.expect(summary.parent_supplies_pm_base);
    try std.testing.expect(summary.pm_base_required);
    try std.testing.expect(summary.pm_base_handoff_ready);
    try std.testing.expect(summary.timeout_init_requested);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.stop_on_reboot_requested);
    try std.testing.expectEqual(@as(i32, bcm2835_wdt.restart_priority), summary.restart_priority_value);
    try std.testing.expect(summary.system_power_controller);
    try std.testing.expect(!summary.poweroff_handler_present);
    try std.testing.expect(summary.poweroff_handler_claimed);
    try std.testing.expect(!summary.poweroff_handler_conflict);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
}

test "phase11 bcm2835 registration scaffold keeps missing parent attachment explicit" {
    const summary = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = false,
        .parent_attached = false,
        .pm_base_present = true,
    });

    try std.testing.expectEqualStrings(bcm2835_wdt.anchor_path, summary.anchor);
    try std.testing.expect(!summary.parent_attached);
    try std.testing.expect(summary.parent_supplies_pm_base);
    try std.testing.expect(summary.pm_base_required);
    try std.testing.expect(!summary.pm_base_handoff_ready);
    try std.testing.expect(summary.timeout_init_requested);
    try std.testing.expect(!summary.register_device_requested);
    try std.testing.expect(summary.stop_on_reboot_requested);
    try std.testing.expect(summary.system_power_controller);
    try std.testing.expect(!summary.poweroff_handler_present);
    try std.testing.expect(summary.poweroff_handler_claimed);
    try std.testing.expect(!summary.poweroff_handler_conflict);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
}

test "phase11 bcm2835 registration scaffold keeps controller-free handoff distinct from poweroff ownership" {
    const summary = try bcm2835_wdt.summarizePlatformHandoff(.{
        .heartbeat_sec = 8,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = false,
        .poweroff_handler_present = true,
        .parent_attached = true,
        .pm_base_present = true,
    });

    try std.testing.expectEqualStrings(bcm2835_wdt.anchor_path, summary.anchor);
    try std.testing.expect(summary.parent_attached);
    try std.testing.expect(summary.parent_supplies_pm_base);
    try std.testing.expect(summary.pm_base_required);
    try std.testing.expect(summary.pm_base_handoff_ready);
    try std.testing.expect(summary.timeout_init_requested);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.stop_on_reboot_requested);
    try std.testing.expect(!summary.system_power_controller);
    try std.testing.expect(summary.poweroff_handler_present);
    try std.testing.expect(!summary.poweroff_handler_claimed);
    try std.testing.expect(!summary.poweroff_handler_conflict);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
}
