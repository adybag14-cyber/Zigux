const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio_wdt platform drvdata checkpoint keeps early platform_set_drvdata ordering explicit" {
    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, true);
    const toggle_checkpoint = toggle_watchdog.platformDrvdataCheckpointSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", toggle_checkpoint.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, toggle_checkpoint.hw_algo);
    try std.testing.expectEqual(@as(u32, 20), toggle_checkpoint.hw_margin_ms);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, toggle_checkpoint.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.in, toggle_checkpoint.descriptor_flags);
    try std.testing.expect(toggle_checkpoint.platform_drvdata_attachment_required);
    try std.testing.expect(toggle_checkpoint.allocation_precedes_platform_drvdata);
    try std.testing.expect(toggle_checkpoint.platform_drvdata_precedes_hw_algo_read);
    try std.testing.expect(toggle_checkpoint.platform_drvdata_precedes_descriptor_lookup);
    try std.testing.expect(toggle_checkpoint.platform_drvdata_precedes_timeout_property);
    try std.testing.expect(toggle_checkpoint.platform_drvdata_precedes_watchdog_drvdata_handoff);
    try std.testing.expect(toggle_checkpoint.invalid_hw_algo_blocks_later_handoffs);
    try std.testing.expect(toggle_checkpoint.blocked_on_live_platform_probe);
    try std.testing.expect(toggle_checkpoint.blocked_on_platform_registration);
}

test "phase11 gpio_wdt platform drvdata checkpoint keeps level-mode descriptor handoff aligned" {
    var level_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const level_checkpoint = level_watchdog.platformDrvdataCheckpointSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", level_checkpoint.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, level_checkpoint.hw_algo);
    try std.testing.expectEqual(@as(u32, 500), level_checkpoint.hw_margin_ms);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, level_checkpoint.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.out_low, level_checkpoint.descriptor_flags);
    try std.testing.expect(level_checkpoint.platform_drvdata_attachment_required);
    try std.testing.expect(level_checkpoint.allocation_precedes_platform_drvdata);
    try std.testing.expect(level_checkpoint.platform_drvdata_precedes_hw_algo_read);
    try std.testing.expect(level_checkpoint.platform_drvdata_precedes_descriptor_lookup);
    try std.testing.expect(level_checkpoint.platform_drvdata_precedes_timeout_property);
    try std.testing.expect(level_checkpoint.platform_drvdata_precedes_watchdog_drvdata_handoff);
    try std.testing.expect(level_checkpoint.invalid_hw_algo_blocks_later_handoffs);
    try std.testing.expect(level_checkpoint.blocked_on_live_platform_probe);
    try std.testing.expect(level_checkpoint.blocked_on_platform_registration);
}
