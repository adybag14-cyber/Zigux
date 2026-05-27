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

test "gpio_wdt reboot-glue checkpoint keeps drvdata ownership tied to the first register-device request" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 17, true);
    const watchdog_drvdata = driver.watchdogDrvdataCheckpointSummary();
    const reboot_glue = driver.rebootGlueCheckpointSummary();
    const register_call = driver.registerDeviceCallSummary(true);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", reboot_glue.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, reboot_glue.hw_algo);
    try std.testing.expectEqual(@as(u32, 17), reboot_glue.hw_margin_ms);
    try std.testing.expect(reboot_glue.parent_attached);
    try std.testing.expect(reboot_glue.module_owner_attached);
    try std.testing.expectEqualStrings("gpio_wdt_priv", reboot_glue.watchdog_drvdata_owner_identity);
    try std.testing.expect(reboot_glue.stop_on_reboot_requested);
    try std.testing.expect(reboot_glue.watchdog_drvdata_precedes_reboot_glue);
    try std.testing.expect(reboot_glue.reboot_glue_precedes_register_device_request);
    try std.testing.expect(reboot_glue.reboot_glue_reuses_parent_linkage);
    try std.testing.expect(reboot_glue.blocked_on_live_gpio_lookup);
    try std.testing.expect(reboot_glue.blocked_on_platform_registration);
    try std.testing.expect(reboot_glue.blocked_on_host_shutdown_execution);
    try std.testing.expectEqualStrings(watchdog_drvdata.watchdog_drvdata_owner_identity, reboot_glue.watchdog_drvdata_owner_identity);
    try std.testing.expect(register_call.register_device_requested);
    try std.testing.expect(register_call.blocked_on_reboot_glue);
}

test "gpio_wdt teardown summary shows toggle disable path through current teardown review markers" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 9, false);
    _ = try driver.start();
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
    _ = try driver.start();
    const summary = driver.summarizeTeardown(false);

    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, summary.stop_disposition);
    try std.testing.expect(summary.line_state);
    try std.testing.expect(summary.line_is_output);
    try std.testing.expectEqual(@as(usize, 1), summary.disable_count);
}

test "gpio_wdt teardown summary keeps always-running watchdog teardown in kept-running state" {
    var driver = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 12, true);
    _ = try driver.start();
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

test "gpio_wdt remove-handoff summary keeps cleanup blockers and ownership handoff explicit" {
    var stoppable = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 9, false);
    _ = try stoppable.start();
    const handoff = stoppable.summarizeRemoveHandoff(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", handoff.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, handoff.hw_algo);
    try std.testing.expect(!handoff.always_running);
    try std.testing.expect(!handoff.nowayout);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, handoff.stop_disposition);
    try std.testing.expectEqualStrings("gpio_wdt_priv", handoff.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings("gpio_wdt_priv", handoff.watchdog_drvdata_owner_identity);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", handoff.register_device_failure_stage);
    try std.testing.expect(handoff.request_stop_reviewable);
    try std.testing.expect(handoff.register_device_failure_reviewable);
    try std.testing.expect(handoff.reboot_glue_checkpoint_reviewable);
    try std.testing.expect(handoff.blocked_on_platform_cleanup_callback);
    try std.testing.expect(handoff.blocked_on_platform_driver_remove);
    try std.testing.expect(handoff.blocked_on_watchdog_core_unregister);
    try std.testing.expect(handoff.blocked_on_host_shutdown_execution);

    var guarded = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 12, true);
    _ = try guarded.start();
    const guarded_handoff = guarded.summarizeRemoveHandoff(true);

    try std.testing.expect(guarded_handoff.always_running);
    try std.testing.expect(guarded_handoff.nowayout);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, guarded_handoff.stop_disposition);
    try std.testing.expect(guarded_handoff.request_stop_reviewable);
    try std.testing.expect(guarded_handoff.register_device_failure_reviewable);
    try std.testing.expect(guarded_handoff.reboot_glue_checkpoint_reviewable);
    try std.testing.expect(guarded_handoff.blocked_on_platform_cleanup_callback);
    try std.testing.expect(guarded_handoff.blocked_on_platform_driver_remove);
    try std.testing.expect(guarded_handoff.blocked_on_watchdog_core_unregister);
    try std.testing.expect(guarded_handoff.blocked_on_host_shutdown_execution);
}

test "gpio_wdt hardware validation matrix keeps the roadmap branches reviewable" {
    const matrix = try gpio_wdt.GpioWatchdogLab.hardwareValidationMatrixSummary();

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", matrix.anchor);
    try std.testing.expect(matrix.covers_toggle_and_level);
    try std.testing.expect(matrix.covers_register_only_and_prestart);
    try std.testing.expect(matrix.covers_stop_dispositions);
    try std.testing.expect(matrix.covers_failure_and_teardown_blockers);

    const toggle_register_only = matrix.rows[0];
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, toggle_register_only.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, toggle_register_only.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.in, toggle_register_only.descriptor_flags);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, toggle_register_only.start_mode);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, toggle_register_only.stop_disposition);
    try std.testing.expect(!toggle_register_only.ping_uses_pulse);
    try std.testing.expect(toggle_register_only.stop_allowed_by_watchdog_core);

    const level_nowayout = matrix.rows[1];
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, level_nowayout.hw_algo);
    try std.testing.expect(level_nowayout.always_running);
    try std.testing.expect(level_nowayout.nowayout);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, level_nowayout.start_mode);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, level_nowayout.stop_disposition);
    try std.testing.expect(level_nowayout.ping_uses_pulse);
    try std.testing.expect(!level_nowayout.stop_allowed_by_watchdog_core);

    const level_register_only = matrix.rows[2];
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, level_register_only.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, level_register_only.start_mode);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, level_register_only.stop_disposition);
    try std.testing.expect(level_register_only.ping_uses_pulse);
    try std.testing.expect(level_register_only.stop_allowed_by_watchdog_core);

    const toggle_prestart = matrix.rows[3];
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, toggle_prestart.hw_algo);
    try std.testing.expect(toggle_prestart.always_running);
    try std.testing.expect(!toggle_prestart.nowayout);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, toggle_prestart.start_mode);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.kept_running, toggle_prestart.stop_disposition);
    try std.testing.expect(!toggle_prestart.ping_uses_pulse);
    try std.testing.expect(toggle_prestart.stop_allowed_by_watchdog_core);

    inline for (matrix.rows) |row| {
        try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", row.anchor);
        try std.testing.expect(row.blocked_on_live_gpio_lookup);
        try std.testing.expect(row.blocked_on_platform_registration);
        try std.testing.expect(row.blocked_on_reboot_glue);
        try std.testing.expect(row.blocked_on_host_shutdown_execution);
    }
}
