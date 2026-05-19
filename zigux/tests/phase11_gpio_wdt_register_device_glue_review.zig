const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio watchdog keeps register-device call glued to reboot boundary" {
    var lab = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    const summary = lab.registerDeviceCallSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", summary.register_call);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, summary.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, summary.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.in, summary.descriptor_flags);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, summary.start_mode);
    try std.testing.expect(!summary.reaches_registration_running);
    try std.testing.expect(!summary.reaches_registration_line_state);
    try std.testing.expect(!summary.reaches_registration_line_is_output);
    try std.testing.expect(!summary.nowayout_applied);
    try std.testing.expectEqual(@as(u32, 250), summary.max_hw_heartbeat_ms);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.blocked_on_live_gpio_lookup);
    try std.testing.expect(summary.blocked_on_platform_registration);
    try std.testing.expect(summary.blocked_on_reboot_glue);
}

test "phase11 gpio watchdog keeps always-running registration call reviewable before reboot glue lands" {
    var lab = try gpio_wdt.GpioWatchdogLab.init(.level, 400, true);
    const summary = lab.registerDeviceCallSummary(true);

    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, summary.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, summary.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.out_low, summary.descriptor_flags);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, summary.start_mode);
    try std.testing.expect(summary.reaches_registration_running);
    try std.testing.expect(!summary.reaches_registration_line_state);
    try std.testing.expect(summary.reaches_registration_line_is_output);
    try std.testing.expect(summary.nowayout_applied);
    try std.testing.expectEqual(@as(u32, 400), summary.max_hw_heartbeat_ms);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.blocked_on_live_gpio_lookup);
    try std.testing.expect(summary.blocked_on_platform_registration);
    try std.testing.expect(summary.blocked_on_reboot_glue);
}

test "phase11 gpio watchdog keeps register-device failure summary tied to the same reboot-glue checkpoint" {
    var lab = try gpio_wdt.GpioWatchdogLab.init(.toggle, gpio_wdt.min_hw_margin_ms, false);
    const summary = lab.registerDeviceFailureSummary(true);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", summary.register_call);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", summary.failure_stage);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.blocked_on_live_gpio_lookup);
    try std.testing.expect(summary.blocked_on_platform_registration);
    try std.testing.expect(summary.blocked_on_reboot_glue);
    try std.testing.expect(summary.keeps_runtime_reviewable);
}
