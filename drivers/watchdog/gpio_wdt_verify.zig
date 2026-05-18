const std = @import("std");

const gpio_wdt = @import("gpio_wdt.zig");

test "gpio_wdt registration plan captures deferred watchdog registration" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 42, false);
    const summary = driver.registrationPlanSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expect(summary.requested_line == 42);
    try std.testing.expect(!summary.always_running);
    try std.testing.expect(!summary.nowayout);
    try std.testing.expect(summary.watchdog_info_ready);
    try std.testing.expect(summary.watchdog_ops_ready);
    try std.testing.expect(summary.watchdog_device_ready);
    try std.testing.expect(summary.descriptor_request_ready);
    try std.testing.expect(summary.timeout_init_requested);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expect(!summary.reaches_registration_running);
    try std.testing.expect(!summary.reaches_registration_line_state);
    try std.testing.expect(!summary.reaches_registration_line_is_output);
    try std.testing.expect(!summary.register_device_requested);
    try std.testing.expect(summary.blocked_on_gpio_descriptor);
    try std.testing.expect(summary.blocked_on_platform_registration);
    try std.testing.expect(summary.blocked_on_reboot_glue);
}

test "gpio_wdt registerDevice summary reports running always-on state" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 17, true);
    const summary = driver.registerDeviceCallSummary(true);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expect(summary.requested_line == 17);
    try std.testing.expect(summary.running_at_registration);
    try std.testing.expect(summary.line_state_at_registration);
    try std.testing.expect(summary.line_is_output_at_registration);
    try std.testing.expect(summary.watchdog_drvdata_set);
    try std.testing.expect(summary.min_timeout_sec == 1);
    try std.testing.expect(summary.default_timeout_sec >= summary.min_timeout_sec);
    try std.testing.expect(summary.max_hw_heartbeat_ms > 0);
    try std.testing.expect(summary.nowayout_applied);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(!summary.blocked_on_gpio_descriptor);
    try std.testing.expect(!summary.blocked_on_platform_registration);
    try std.testing.expect(!summary.blocked_on_reboot_glue);
}

test "gpio_wdt failure summary keeps descriptor-first registration blockers explicit" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 42, false);
    const summary = driver.registerDeviceFailureSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expect(summary.requested_line == 42);
    try std.testing.expect(!summary.always_running);
    try std.testing.expect(!summary.nowayout);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.remains_summary_only);
    try std.testing.expect(summary.primary_failure_mode == .descriptor_preflight_pending);
    try std.testing.expect(summary.failure_mode_count == 3);
    try std.testing.expect(summary.descriptor_preflight_pending);
    try std.testing.expect(summary.platform_registration_pending);
    try std.testing.expect(summary.reboot_glue_pending);
    try std.testing.expect(!summary.preserves_registration_running_state);
    try std.testing.expect(!summary.preserves_registration_line_state);
    try std.testing.expect(!summary.preserves_registration_line_is_output);
}

test "gpio_wdt failure summary preserves always-running registration state while blockers remain" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 17, true);
    const summary = driver.registerDeviceFailureSummary(true);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expect(summary.requested_line == 17);
    try std.testing.expect(summary.always_running);
    try std.testing.expect(summary.nowayout);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.remains_summary_only);
    try std.testing.expect(summary.primary_failure_mode == .descriptor_preflight_pending);
    try std.testing.expect(summary.failure_mode_count == 3);
    try std.testing.expect(summary.descriptor_preflight_pending);
    try std.testing.expect(summary.platform_registration_pending);
    try std.testing.expect(summary.reboot_glue_pending);
    try std.testing.expect(summary.preserves_registration_running_state);
    try std.testing.expect(summary.preserves_registration_line_state);
    try std.testing.expect(summary.preserves_registration_line_is_output);
}

test "gpio_wdt teardown summary shows toggle disable path" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 9, false);
    _ = try driver.start();
    const summary = try driver.summarizeTeardown(false);

    try std.testing.expect(summary.running_before_teardown);
    try std.testing.expect(!summary.teardown_skipped_without_running);
    try std.testing.expect(summary.stop_allowed_by_watchdog_core);
    try std.testing.expect(summary.driver_stop_invoked);
    try std.testing.expect(summary.disable_requested);
    try std.testing.expect(summary.disable_performs_eternal_ping);
    try std.testing.expect(summary.disable_returns_toggle_line_to_input);
    try std.testing.expect(!summary.stop_keeps_running_for_always_running);
    try std.testing.expect(!summary.final_running);
    try std.testing.expect(!summary.final_line_is_output);
    try std.testing.expect(summary.disable_count == 1);
}

test "gpio_wdt teardown summary keeps level line output when stopping level hardware" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 5, false);
    _ = try driver.start();
    const summary = try driver.summarizeTeardown(false);

    try std.testing.expect(summary.running_before_teardown);
    try std.testing.expect(!summary.teardown_skipped_without_running);
    try std.testing.expect(summary.stop_allowed_by_watchdog_core);
    try std.testing.expect(summary.driver_stop_invoked);
    try std.testing.expect(summary.disable_requested);
    try std.testing.expect(summary.disable_performs_eternal_ping);
    try std.testing.expect(!summary.disable_returns_toggle_line_to_input);
    try std.testing.expect(summary.disable_keeps_level_line_output);
    try std.testing.expect(!summary.stop_keeps_running_for_always_running);
    try std.testing.expect(!summary.final_running);
    try std.testing.expect(summary.final_line_is_output);
    try std.testing.expect(summary.disable_count == 1);
}

test "gpio_wdt teardown summary keeps idle teardown explicit when nothing is running" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 4, false);
    const summary = try driver.summarizeTeardown(false);

    try std.testing.expect(!summary.running_before_teardown);
    try std.testing.expect(summary.teardown_skipped_without_running);
    try std.testing.expect(!summary.stop_allowed_by_watchdog_core);
    try std.testing.expect(!summary.driver_stop_invoked);
    try std.testing.expect(!summary.disable_requested);
    try std.testing.expect(!summary.disable_performs_eternal_ping);
    try std.testing.expect(!summary.disable_keeps_level_line_output);
    try std.testing.expect(!summary.stop_keeps_running_for_always_running);
    try std.testing.expect(!summary.final_running);
    try std.testing.expect(!summary.final_line_is_output);
    try std.testing.expect(summary.disable_count == 0);
}

test "gpio_wdt teardown summary keeps always-running watchdog alive" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 12, true);
    _ = try driver.start();
    const summary = try driver.summarizeTeardown(false);

    try std.testing.expect(summary.running_before_teardown);
    try std.testing.expect(!summary.teardown_skipped_without_running);
    try std.testing.expect(summary.stop_allowed_by_watchdog_core);
    try std.testing.expect(summary.driver_stop_invoked);
    try std.testing.expect(!summary.disable_requested);
    try std.testing.expect(!summary.disable_performs_eternal_ping);
    try std.testing.expect(!summary.disable_returns_toggle_line_to_input);
    try std.testing.expect(!summary.disable_keeps_level_line_output);
    try std.testing.expect(summary.stop_keeps_running_for_always_running);
    try std.testing.expect(summary.final_running);
    try std.testing.expect(!summary.final_line_state);
    try std.testing.expect(summary.final_line_is_output);
    try std.testing.expect(summary.disable_count == 0);
}
