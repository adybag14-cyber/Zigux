const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio_wdt timeout property checkpoint keeps hw_margin ordering explicit for toggle mode" {
    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    const platform_checkpoint = toggle_watchdog.platformDrvdataCheckpointSummary();
    const probe = toggle_watchdog.probeSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", platform_checkpoint.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, platform_checkpoint.hw_algo);
    try std.testing.expectEqual(@as(u32, 250), platform_checkpoint.hw_margin_ms);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, platform_checkpoint.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.in, platform_checkpoint.descriptor_flags);
    try std.testing.expect(platform_checkpoint.platform_drvdata_precedes_timeout_property);
    try std.testing.expect(platform_checkpoint.platform_drvdata_precedes_watchdog_drvdata_handoff);
    try std.testing.expect(platform_checkpoint.invalid_hw_algo_blocks_later_handoffs);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", probe.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, probe.hw_algo);
    try std.testing.expectEqual(@as(u32, 250), probe.hw_margin_ms);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, probe.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, probe.start_mode);
    try std.testing.expect(probe.timeout_init_requested);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_min), probe.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_default), probe.default_timeout_sec);
    try std.testing.expectEqual(@as(u32, 250), probe.max_hw_heartbeat_ms);
}

test "phase11 gpio_wdt timeout property checkpoint keeps always-running pre-registration bookkeeping explicit for level mode" {
    var level_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, true);
    const platform_checkpoint = level_watchdog.platformDrvdataCheckpointSummary();
    const probe = level_watchdog.probeSummary(true);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", platform_checkpoint.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, platform_checkpoint.hw_algo);
    try std.testing.expectEqual(@as(u32, 500), platform_checkpoint.hw_margin_ms);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, platform_checkpoint.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.out_low, platform_checkpoint.descriptor_flags);
    try std.testing.expect(platform_checkpoint.platform_drvdata_precedes_timeout_property);
    try std.testing.expect(platform_checkpoint.platform_drvdata_precedes_watchdog_drvdata_handoff);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", probe.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, probe.hw_algo);
    try std.testing.expectEqual(@as(u32, 500), probe.hw_margin_ms);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, probe.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, probe.start_mode);
    try std.testing.expect(probe.starts_during_probe);
    try std.testing.expect(probe.pre_registration_running);
    try std.testing.expect(!probe.pre_registration_line_state);
    try std.testing.expect(probe.pre_registration_line_is_output);
    try std.testing.expect(probe.timeout_init_requested);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_min), probe.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_default), probe.default_timeout_sec);
    try std.testing.expectEqual(@as(u32, 500), probe.max_hw_heartbeat_ms);
}
