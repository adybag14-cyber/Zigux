const std = @import("std");

const gpio_wdt = @import("gpio_wdt.zig");

test "gpio_wdt registration plan keeps current descriptor and blocker surfaces explicit" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 42, false);
    const summary = driver.registrationPlanSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, summary.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, summary.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.in, summary.descriptor_flags);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, summary.start_mode);
    try std.testing.expect(!summary.reaches_registration_running);
    try std.testing.expect(!summary.reaches_registration_line_state);
    try std.testing.expect(!summary.reaches_registration_line_is_output);
    try std.testing.expect(summary.timeout_init_requested);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expect(summary.parent_attached);
    try std.testing.expect(summary.module_owner_attached);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.blocked_on_live_gpio_lookup);
    try std.testing.expect(summary.blocked_on_platform_registration);
}

test "gpio_wdt register-device summary keeps always-running level registration state reviewable" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 17, true);
    const summary = driver.registerDeviceCallSummary(true);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", summary.register_call);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, summary.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, summary.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.out_low, summary.descriptor_flags);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, summary.start_mode);
    try std.testing.expect(summary.reaches_registration_running);
    try std.testing.expect(!summary.reaches_registration_line_state);
    try std.testing.expect(summary.reaches_registration_line_is_output);
    try std.testing.expect(summary.nowayout_applied);
    try std.testing.expectEqual(@as(u32, 17), summary.max_hw_heartbeat_ms);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.blocked_on_live_gpio_lookup);
    try std.testing.expect(summary.blocked_on_platform_registration);
    try std.testing.expect(summary.blocked_on_reboot_glue);
}

test "gpio_wdt failure summary keeps the current failure-stage and blocker triad explicit" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 42, false);
    const summary = driver.registerDeviceFailureSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", summary.register_call);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", summary.failure_stage);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.blocked_on_live_gpio_lookup);
    try std.testing.expect(summary.blocked_on_platform_registration);
    try std.testing.expect(summary.blocked_on_reboot_glue);
    try std.testing.expect(summary.keeps_runtime_reviewable);
}

test "gpio_wdt teardown summary shows toggle disable path through current teardown review markers" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 9, false);
    try driver.start();
    const summary = driver.summarizeTeardown(false);

    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, summary.stop_disposition);
    try std.testing.expect(summary.request_stop_reviewable);
    try std.testing.expect(summary.register_device_failure_reviewable);
    try std.testing.expect(summary.reboot_glue_checkpoint_reviewable);
    try std.testing.expect(summary.line_state);
    try std.testing.expect(!summary.line_is_output);
    try std.testing.expectEqual(@as(usize, 1), summary.disable_count);
}

test "gpio_wdt teardown summary keeps level hardware output asserted on a normal stop" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 5, false);
    try driver.start();
    const summary = driver.summarizeTeardown(false);

    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, summary.stop_disposition);
    try std.testing.expect(summary.line_state);
    try std.testing.expect(summary.line_is_output);
    try std.testing.expectEqual(@as(usize, 1), summary.disable_count);
}

test "gpio_wdt teardown summary keeps always-running watchdog teardown in kept-running state" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 12, true);
    try driver.start();
    const summary = driver.summarizeTeardown(false);

    try std.testing.expect(summary.always_running);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.kept_running, summary.stop_disposition);
    try std.testing.expect(!summary.line_state);
    try std.testing.expect(summary.line_is_output);
    try std.testing.expectEqual(@as(usize, 0), summary.disable_count);
    try std.testing.expect(summary.request_stop_reviewable);
    try std.testing.expect(summary.register_device_failure_reviewable);
    try std.testing.expect(summary.reboot_glue_checkpoint_reviewable);
}
