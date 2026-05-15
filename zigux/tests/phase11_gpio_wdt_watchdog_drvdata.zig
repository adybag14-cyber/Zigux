const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio_wdt watchdog drvdata checkpoint keeps watchdog_set_drvdata ordering explicit for toggle mode" {
    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, true);
    const checkpoint = toggle_watchdog.watchdogDrvdataCheckpointSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", checkpoint.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, checkpoint.hw_algo);
    try std.testing.expectEqual(@as(u32, 20), checkpoint.hw_margin_ms);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, checkpoint.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.in, checkpoint.descriptor_flags);
    try std.testing.expect(checkpoint.parent_attached);
    try std.testing.expect(checkpoint.platform_drvdata_attached);
    try std.testing.expect(checkpoint.watchdog_drvdata_attachment_required);
    try std.testing.expect(checkpoint.timeout_property_precedes_watchdog_drvdata);
    try std.testing.expect(checkpoint.platform_drvdata_precedes_watchdog_drvdata);
    try std.testing.expect(checkpoint.watchdog_drvdata_precedes_register_device_call);
    try std.testing.expect(checkpoint.watchdog_drvdata_reuses_parent_linkage);
    try std.testing.expectEqualStrings("gpio_wdt_priv", checkpoint.drvdata_owner_identity);
    try std.testing.expect(checkpoint.blocked_on_watchdog_core_registration);
    try std.testing.expect(checkpoint.blocked_on_platform_registration);
}

test "phase11 gpio_wdt watchdog drvdata checkpoint keeps watchdog_set_drvdata ordering explicit for level mode" {
    var level_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const checkpoint = level_watchdog.watchdogDrvdataCheckpointSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", checkpoint.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, checkpoint.hw_algo);
    try std.testing.expectEqual(@as(u32, 500), checkpoint.hw_margin_ms);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, checkpoint.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.out_low, checkpoint.descriptor_flags);
    try std.testing.expect(checkpoint.parent_attached);
    try std.testing.expect(checkpoint.platform_drvdata_attached);
    try std.testing.expect(checkpoint.watchdog_drvdata_attachment_required);
    try std.testing.expect(checkpoint.timeout_property_precedes_watchdog_drvdata);
    try std.testing.expect(checkpoint.platform_drvdata_precedes_watchdog_drvdata);
    try std.testing.expect(checkpoint.watchdog_drvdata_precedes_register_device_call);
    try std.testing.expect(checkpoint.watchdog_drvdata_reuses_parent_linkage);
    try std.testing.expectEqualStrings("gpio_wdt_priv", checkpoint.drvdata_owner_identity);
    try std.testing.expect(checkpoint.blocked_on_watchdog_core_registration);
    try std.testing.expect(checkpoint.blocked_on_platform_registration);
}
