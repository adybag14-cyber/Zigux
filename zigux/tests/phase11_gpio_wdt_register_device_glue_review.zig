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

test "phase11 gpio watchdog keeps watchdog-core setup order explicit before the first register-device request" {
    var prestarted = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, true);
    const prestarted_intent = prestarted.registrationIntentCheckpointSummary(true);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", prestarted_intent.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, prestarted_intent.hw_algo);
    try std.testing.expectEqual(@as(u32, 250), prestarted_intent.hw_margin_ms);
    try std.testing.expect(prestarted_intent.always_running);
    try std.testing.expect(prestarted_intent.timeout_init_requested);
    try std.testing.expect(prestarted_intent.nowayout_from_module_param);
    try std.testing.expect(prestarted_intent.stop_on_reboot_requested);
    try std.testing.expect(prestarted_intent.pre_registration_start_requested);
    try std.testing.expect(prestarted_intent.timeout_init_stays_before_nowayout);
    try std.testing.expect(prestarted_intent.nowayout_stays_before_stop_on_reboot);
    try std.testing.expect(prestarted_intent.stop_on_reboot_stays_before_pre_registration_start);
    try std.testing.expect(prestarted_intent.pre_registration_start_stays_before_registration);
    try std.testing.expect(prestarted_intent.blocked_on_live_gpio_lookup);
    try std.testing.expect(prestarted_intent.blocked_on_platform_registration);

    var dormant = try gpio_wdt.GpioWatchdogLab.init(.level, 400, false);
    const dormant_intent = dormant.registrationIntentCheckpointSummary(false);

    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, dormant_intent.hw_algo);
    try std.testing.expectEqual(@as(u32, 400), dormant_intent.hw_margin_ms);
    try std.testing.expect(!dormant_intent.always_running);
    try std.testing.expect(dormant_intent.timeout_init_requested);
    try std.testing.expect(!dormant_intent.nowayout_from_module_param);
    try std.testing.expect(dormant_intent.stop_on_reboot_requested);
    try std.testing.expect(!dormant_intent.pre_registration_start_requested);
    try std.testing.expect(dormant_intent.timeout_init_stays_before_nowayout);
    try std.testing.expect(dormant_intent.nowayout_stays_before_stop_on_reboot);
    try std.testing.expect(dormant_intent.stop_on_reboot_stays_before_pre_registration_start);
    try std.testing.expect(dormant_intent.pre_registration_start_stays_before_registration);
    try std.testing.expect(dormant_intent.blocked_on_live_gpio_lookup);
    try std.testing.expect(dormant_intent.blocked_on_platform_registration);
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

test "phase11 gpio watchdog keeps remove-handoff teardown reviewable without live unregister behavior" {
    var stoppable_stop = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    _ = try stoppable_stop.start();
    const stop_summary = stoppable_stop.requestStop(false);

    var stoppable_teardown = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    _ = try stoppable_teardown.start();
    const failure_summary = stoppable_teardown.registerDeviceFailureSummary(false);
    const teardown = stoppable_teardown.summarizeTeardown(false);

    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, stop_summary.disposition);
    try std.testing.expect(stop_summary.stop_allowed_by_watchdog_core);
    try std.testing.expect(stop_summary.driver_stop_invoked);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", failure_summary.failure_stage);
    try std.testing.expect(teardown.request_stop_reviewable);
    try std.testing.expect(teardown.register_device_failure_reviewable);
    try std.testing.expect(teardown.reboot_glue_checkpoint_reviewable);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, teardown.stop_disposition);
    try std.testing.expect(teardown.line_state);
    try std.testing.expect(!teardown.line_is_output);
    try std.testing.expectEqual(@as(usize, 1), teardown.disable_count);

    var guarded = try gpio_wdt.GpioWatchdogLab.init(.level, 400, true);
    _ = try guarded.start();
    const guarded_stop = guarded.requestStop(true);
    const guarded_teardown = guarded.summarizeTeardown(true);

    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, guarded_stop.disposition);
    try std.testing.expect(!guarded_stop.stop_allowed_by_watchdog_core);
    try std.testing.expect(!guarded_stop.driver_stop_invoked);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, guarded_teardown.stop_disposition);
    try std.testing.expect(guarded_teardown.line_is_output);
    try std.testing.expectEqual(@as(usize, 0), guarded_teardown.disable_count);
    try std.testing.expect(guarded_teardown.request_stop_reviewable);
    try std.testing.expect(guarded_teardown.register_device_failure_reviewable);
    try std.testing.expect(guarded_teardown.reboot_glue_checkpoint_reviewable);
}
