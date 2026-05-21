const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio watchdog keeps descriptor lookup ahead of timeout and drvdata checkpoints" {
    const toggle = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    const toggle_descriptor = toggle.descriptorRequestSummary();
    const toggle_timeout = toggle.timeoutPropertyCheckpointSummary();
    const toggle_platform_drvdata = toggle.platformDrvdataCheckpointSummary();
    const toggle_watchdog_drvdata = toggle.watchdogDrvdataCheckpointSummary();

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", toggle_descriptor.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, toggle_descriptor.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, toggle_descriptor.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.in, toggle_descriptor.descriptor_flags);
    try std.testing.expect(toggle_descriptor.descriptor_lookup_required);
    try std.testing.expect(toggle_descriptor.hw_algo_selected_before_lookup);
    try std.testing.expect(toggle_descriptor.lookup_precedes_margin_validation);
    try std.testing.expect(toggle_descriptor.lookup_precedes_always_running_read);
    try std.testing.expect(toggle_descriptor.lookup_precedes_registration_handoff);
    try std.testing.expect(toggle_descriptor.blocked_on_live_gpio_lookup);
    try std.testing.expect(toggle_descriptor.blocked_on_platform_registration);

    try std.testing.expectEqualStrings("hw_margin_ms", toggle_timeout.timeout_property_name);
    try std.testing.expectEqual(@as(u32, 250), toggle_timeout.hw_margin_ms);
    try std.testing.expect(toggle_timeout.timeout_property_required);
    try std.testing.expect(toggle_timeout.descriptor_lookup_precedes_timeout_property);
    try std.testing.expect(toggle_timeout.timeout_property_precedes_always_running_read);
    try std.testing.expect(toggle_timeout.timeout_property_precedes_registration_handoff);
    try std.testing.expect(toggle_timeout.blocked_on_live_gpio_lookup);
    try std.testing.expect(toggle_timeout.blocked_on_platform_registration);

    try std.testing.expect(toggle_platform_drvdata.parent_attached);
    try std.testing.expect(toggle_platform_drvdata.module_owner_attached);
    try std.testing.expectEqualStrings("gpio_wdt_priv", toggle_platform_drvdata.drvdata_owner_identity);
    try std.testing.expect(toggle_platform_drvdata.timeout_property_precedes_drvdata_binding);
    try std.testing.expect(toggle_platform_drvdata.drvdata_binding_precedes_registration_handoff);
    try std.testing.expect(toggle_platform_drvdata.drvdata_binding_reuses_parent_linkage);
    try std.testing.expect(toggle_platform_drvdata.blocked_on_live_gpio_lookup);
    try std.testing.expect(toggle_platform_drvdata.blocked_on_platform_registration);

    try std.testing.expect(toggle_watchdog_drvdata.parent_attached);
    try std.testing.expect(toggle_watchdog_drvdata.module_owner_attached);
    try std.testing.expectEqualStrings("gpio_wdt_priv", toggle_watchdog_drvdata.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings("gpio_wdt_priv", toggle_watchdog_drvdata.watchdog_drvdata_owner_identity);
    try std.testing.expect(toggle_watchdog_drvdata.timeout_property_precedes_platform_drvdata);
    try std.testing.expect(toggle_watchdog_drvdata.platform_drvdata_precedes_watchdog_drvdata);
    try std.testing.expect(toggle_watchdog_drvdata.watchdog_drvdata_precedes_registration_handoff);
    try std.testing.expect(toggle_watchdog_drvdata.watchdog_drvdata_reuses_parent_linkage);
    try std.testing.expect(toggle_watchdog_drvdata.blocked_on_live_gpio_lookup);
    try std.testing.expect(toggle_watchdog_drvdata.blocked_on_platform_registration);
    try std.testing.expect(toggle_watchdog_drvdata.blocked_on_reboot_glue);
}

test "phase11 gpio watchdog keeps descriptor-facing ordering reviewable for always-running level hardware" {
    const level = try gpio_wdt.GpioWatchdogLab.init(.level, 400, true);
    const descriptor = level.descriptorRequestSummary();
    const timeout = level.timeoutPropertyCheckpointSummary();
    const platform_drvdata = level.platformDrvdataCheckpointSummary();
    const watchdog_drvdata = level.watchdogDrvdataCheckpointSummary();
    const handoff = level.registrationHandoffSummary(true);

    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, descriptor.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, descriptor.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.out_low, descriptor.descriptor_flags);
    try std.testing.expect(descriptor.lookup_precedes_margin_validation);
    try std.testing.expect(descriptor.lookup_precedes_always_running_read);
    try std.testing.expect(descriptor.lookup_precedes_registration_handoff);

    try std.testing.expectEqual(@as(u32, 400), timeout.hw_margin_ms);
    try std.testing.expect(timeout.descriptor_lookup_precedes_timeout_property);
    try std.testing.expect(timeout.timeout_property_precedes_always_running_read);
    try std.testing.expect(timeout.timeout_property_precedes_registration_handoff);

    try std.testing.expectEqualStrings("gpio_wdt_priv", platform_drvdata.drvdata_owner_identity);
    try std.testing.expect(platform_drvdata.timeout_property_precedes_drvdata_binding);
    try std.testing.expect(platform_drvdata.drvdata_binding_precedes_registration_handoff);
    try std.testing.expect(platform_drvdata.drvdata_binding_reuses_parent_linkage);

    try std.testing.expectEqualStrings("gpio_wdt_priv", watchdog_drvdata.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings("gpio_wdt_priv", watchdog_drvdata.watchdog_drvdata_owner_identity);
    try std.testing.expect(watchdog_drvdata.timeout_property_precedes_platform_drvdata);
    try std.testing.expect(watchdog_drvdata.platform_drvdata_precedes_watchdog_drvdata);
    try std.testing.expect(watchdog_drvdata.watchdog_drvdata_precedes_registration_handoff);
    try std.testing.expect(watchdog_drvdata.watchdog_drvdata_reuses_parent_linkage);
    try std.testing.expect(watchdog_drvdata.blocked_on_reboot_glue);

    try std.testing.expect(handoff.reaches_registration_running);
    try std.testing.expect(!handoff.reaches_registration_line_state);
    try std.testing.expect(handoff.reaches_registration_line_is_output);
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

test "phase11 gpio watchdog keeps register-device call glued to reboot boundary" {
    const lab = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
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
    const lab = try gpio_wdt.GpioWatchdogLab.init(.level, 400, true);
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

test "phase11 gpio watchdog keeps teardown checkpoint glued to register-device failure and reboot handoff" {
    var stoppable = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    _ = try stoppable.start();
    const stoppable_teardown = stoppable.teardownCheckpointSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", stoppable_teardown.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, stoppable_teardown.hw_algo);
    try std.testing.expect(!stoppable_teardown.always_running);
    try std.testing.expect(!stoppable_teardown.nowayout);
    try std.testing.expectEqualStrings("gpio_wdt_priv", stoppable_teardown.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings("gpio_wdt_priv", stoppable_teardown.watchdog_drvdata_owner_identity);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, stoppable_teardown.stop_disposition);
    try std.testing.expect(stoppable_teardown.stop_allowed_by_watchdog_core);
    try std.testing.expect(stoppable_teardown.driver_stop_invoked);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", stoppable_teardown.register_device_failure_stage);
    try std.testing.expect(stoppable_teardown.watchdog_drvdata_precedes_reboot_glue);
    try std.testing.expect(stoppable_teardown.reboot_glue_precedes_register_device_request);
    try std.testing.expect(stoppable_teardown.teardown_reuses_parent_linkage);
    try std.testing.expect(stoppable_teardown.blocked_on_live_gpio_lookup);
    try std.testing.expect(stoppable_teardown.blocked_on_platform_registration);
    try std.testing.expect(stoppable_teardown.blocked_on_host_shutdown_execution);

    var guarded = try gpio_wdt.GpioWatchdogLab.init(.level, 400, true);
    _ = try guarded.start();
    const guarded_teardown = guarded.teardownCheckpointSummary(true);

    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, guarded_teardown.hw_algo);
    try std.testing.expect(guarded_teardown.always_running);
    try std.testing.expect(guarded_teardown.nowayout);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, guarded_teardown.stop_disposition);
    try std.testing.expect(!guarded_teardown.stop_allowed_by_watchdog_core);
    try std.testing.expect(!guarded_teardown.driver_stop_invoked);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", guarded_teardown.register_device_failure_stage);
    try std.testing.expect(guarded_teardown.watchdog_drvdata_precedes_reboot_glue);
    try std.testing.expect(guarded_teardown.reboot_glue_precedes_register_device_request);
    try std.testing.expect(guarded_teardown.teardown_reuses_parent_linkage);
    try std.testing.expect(guarded_teardown.blocked_on_live_gpio_lookup);
    try std.testing.expect(guarded_teardown.blocked_on_platform_registration);
    try std.testing.expect(guarded_teardown.blocked_on_host_shutdown_execution);
}

test "phase11 gpio watchdog keeps register-device failure summary tied to the same reboot-glue checkpoint" {
    const lab = try gpio_wdt.GpioWatchdogLab.init(.toggle, gpio_wdt.min_hw_margin_ms, false);
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
