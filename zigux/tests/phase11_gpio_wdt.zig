const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio_wdt descriptor and config summary keep the starter boundary explicit" {
    const descriptor = gpio_wdt.GpioWatchdogLab.descriptor();
    try std.testing.expectEqualStrings("gpio_wdt_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_simple_driver_starter);
    try std.testing.expect(!descriptor.touches_platform_registration);
    try std.testing.expect(!descriptor.touches_live_gpio);

    try std.testing.expectError(
        error.InvalidHardwareAlgorithm,
        gpio_wdt.GpioWatchdogLab.initFromPropertyString("pulse", 50, false),
    );
    try std.testing.expectError(
        error.HeartbeatMarginTooSmall,
        gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 1, false),
    );
    try std.testing.expectError(
        error.HeartbeatMarginTooLarge,
        gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 65_536, true),
    );

    var watchdog = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 250, false);
    const config = watchdog.configSnapshot();
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, config.hw_algo);
    try std.testing.expectEqual(@as(u32, 250), config.hw_margin_ms);
    try std.testing.expect(!config.always_running);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_min), config.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_default), config.default_timeout_sec);
    try std.testing.expectEqual(@as(u32, 250), config.max_hw_heartbeat_ms);
    try std.testing.expectError(error.WatchdogNotRunning, watchdog.ping());
}

test "phase11 gpio_wdt metadata and platform identity summaries stay reviewable" {
    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, true);
    const metadata = toggle_watchdog.watchdogMetadataSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", metadata.anchor);
    try std.testing.expectEqualStrings("GPIO Watchdog", metadata.identity);
    try std.testing.expect(metadata.supports_set_timeout);
    try std.testing.expect(metadata.supports_magic_close);
    try std.testing.expect(metadata.supports_keepalive_ping);
    try std.testing.expect(metadata.start_op_ready);
    try std.testing.expect(metadata.stop_op_ready);
    try std.testing.expect(metadata.ping_op_ready);
    try std.testing.expectEqual(@as(u32, 20), metadata.max_hw_heartbeat_ms);

    const identity = gpio_wdt.GpioWatchdogLab.platformDriverIdentitySummary();
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", identity.anchor);
    try std.testing.expectEqualStrings("gpio-wdt", identity.driver_name);
    try std.testing.expectEqualStrings("linux,wdt-gpio", identity.of_compatible);
    try std.testing.expectEqualStrings("gpio_wdt_probe", identity.probe_callback);
    try std.testing.expectEqual(
        gpio_wdt.PlatformDriverRegistrationMode.module_platform_driver,
        identity.default_registration_mode,
    );
    try std.testing.expect(identity.supports_arch_initcall_override);
    try std.testing.expect(identity.of_match_table_ready);
    try std.testing.expect(identity.platform_probe_ready);
}

test "phase11 gpio_wdt descriptor and drvdata checkpoints keep probe ordering explicit" {
    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, true);
    const toggle_descriptor = toggle_watchdog.descriptorRequestSummary();
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, toggle_descriptor.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, toggle_descriptor.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorLookupMode.input, toggle_descriptor.lookup_mode);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.in, toggle_descriptor.descriptor_flags);
    try std.testing.expect(toggle_descriptor.descriptor_requested_with_null_connection_id);
    try std.testing.expect(toggle_descriptor.descriptor_lookup_is_devm_managed);
    try std.testing.expect(toggle_descriptor.lookup_happens_before_timeout_init);
    try std.testing.expect(toggle_descriptor.lookup_happens_before_register_device);
    try std.testing.expect(toggle_descriptor.blocked_on_live_gpio);

    const toggle_drvdata = toggle_watchdog.platformDrvdataCheckpointSummary();
    try std.testing.expect(toggle_drvdata.platform_drvdata_attachment_required);
    try std.testing.expect(toggle_drvdata.allocation_precedes_platform_drvdata);
    try std.testing.expect(toggle_drvdata.platform_drvdata_precedes_hw_algo_read);
    try std.testing.expect(toggle_drvdata.platform_drvdata_precedes_descriptor_lookup);
    try std.testing.expect(toggle_drvdata.platform_drvdata_precedes_timeout_property);
    try std.testing.expect(toggle_drvdata.platform_drvdata_precedes_watchdog_drvdata_handoff);
    try std.testing.expect(toggle_drvdata.invalid_hw_algo_blocks_later_handoffs);
    try std.testing.expect(toggle_drvdata.blocked_on_live_platform_probe);
    try std.testing.expect(toggle_drvdata.blocked_on_platform_registration);

    var level_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const level_descriptor = level_watchdog.descriptorRequestSummary();
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, level_descriptor.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorLookupMode.output_low, level_descriptor.lookup_mode);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.out_low, level_descriptor.descriptor_flags);
}

test "phase11 gpio_wdt probe summary records startup and timeout bookkeeping" {
    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, true);
    const toggle_probe = toggle_watchdog.probeSummary(true);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, toggle_probe.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, toggle_probe.start_mode);
    try std.testing.expect(toggle_probe.starts_during_probe);
    try std.testing.expect(toggle_probe.pre_registration_running);
    try std.testing.expect(toggle_probe.pre_registration_line_state);
    try std.testing.expect(toggle_probe.pre_registration_line_is_output);
    try std.testing.expect(toggle_probe.parent_attached);
    try std.testing.expect(toggle_probe.stop_on_reboot);
    try std.testing.expect(toggle_probe.timeout_init_requested);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_min), toggle_probe.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_default), toggle_probe.default_timeout_sec);
    try std.testing.expectEqual(@as(u32, 20), toggle_probe.max_hw_heartbeat_ms);

    var level_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const level_probe = level_watchdog.probeSummary(false);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, level_probe.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, level_probe.start_mode);
    try std.testing.expect(!level_probe.starts_during_probe);
    try std.testing.expect(!level_probe.pre_registration_running);
    try std.testing.expect(!level_probe.pre_registration_line_state);
    try std.testing.expect(level_probe.pre_registration_line_is_output);
    try std.testing.expectEqual(@as(u32, 500), level_probe.max_hw_heartbeat_ms);
}

test "phase11 gpio_wdt runtime transitions keep toggle and level behavior reviewable" {
    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, false);

    var toggle_runtime = try toggle_watchdog.start();
    try std.testing.expect(toggle_runtime.running);
    try std.testing.expect(toggle_runtime.line_is_output);
    try std.testing.expect(toggle_runtime.line_state);
    try std.testing.expectEqual(@as(usize, 1), toggle_runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 0), toggle_runtime.pulse_count);
    try std.testing.expect(!toggle_runtime.last_ping_was_pulse);

    toggle_runtime = try toggle_watchdog.ping();
    try std.testing.expect(toggle_runtime.running);
    try std.testing.expect(!toggle_runtime.line_state);
    try std.testing.expectEqual(@as(usize, 2), toggle_runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 0), toggle_runtime.pulse_count);

    toggle_runtime = toggle_watchdog.stop();
    try std.testing.expect(!toggle_runtime.running);
    try std.testing.expect(!toggle_runtime.line_is_output);
    try std.testing.expect(toggle_runtime.line_state);
    try std.testing.expectEqual(@as(usize, 1), toggle_runtime.disable_count);

    var level_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, true);
    var level_runtime = try level_watchdog.start();
    try std.testing.expect(level_runtime.running);
    try std.testing.expect(level_runtime.line_is_output);
    try std.testing.expect(!level_runtime.line_state);
    try std.testing.expectEqual(@as(usize, 1), level_runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 1), level_runtime.pulse_count);
    try std.testing.expect(level_runtime.last_ping_was_pulse);
    try std.testing.expectEqual(@as(u32, gpio_wdt.level_pulse_width_usec), level_runtime.last_pulse_width_usec);

    level_runtime = level_watchdog.stop();
    try std.testing.expect(level_runtime.running);
    try std.testing.expect(level_runtime.line_is_output);
    try std.testing.expect(!level_runtime.line_state);
    try std.testing.expectEqual(@as(usize, 0), level_runtime.disable_count);
}

test "phase11 gpio_wdt nowayout policy stop requests and teardown stay bounded" {
    const nowayout_policy = gpio_wdt.GpioWatchdogLab.nowayoutPolicySummary();
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", nowayout_policy.anchor);
    try std.testing.expectEqualStrings("nowayout", nowayout_policy.module_param_name);
    try std.testing.expectEqual(gpio_wdt.NowayoutDefaultSource.watchdog_nowayout, nowayout_policy.default_source);
    try std.testing.expect(nowayout_policy.module_param_declared);
    try std.testing.expect(nowayout_policy.module_param_is_bool);
    try std.testing.expect(nowayout_policy.default_follows_watchdog_nowayout);
    try std.testing.expect(nowayout_policy.applied_via_watchdog_set_nowayout);
    try std.testing.expect(nowayout_policy.bounded_to_summary_bookkeeping);

    var blocked_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, false);
    _ = try blocked_watchdog.start();
    const blocked = blocked_watchdog.requestStop(true);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, blocked.disposition);
    try std.testing.expect(!blocked.stop_allowed_by_watchdog_core);
    try std.testing.expect(!blocked.driver_stop_invoked);
    try std.testing.expect(blocked.running);
    try std.testing.expectEqual(@as(usize, 0), blocked.disable_count);

    var stoppable_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, false);
    _ = try stoppable_watchdog.start();
    const stopped = stoppable_watchdog.requestStop(false);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, stopped.disposition);
    try std.testing.expect(stopped.stop_allowed_by_watchdog_core);
    try std.testing.expect(stopped.driver_stop_invoked);
    try std.testing.expect(!stopped.running);
    try std.testing.expectEqual(@as(usize, 1), stopped.disable_count);

    var teardown_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    _ = try teardown_watchdog.start();
    const teardown = try teardown_watchdog.summarizeTeardown(false);
    try std.testing.expect(teardown.running_before_teardown);
    try std.testing.expect(!teardown.teardown_skipped_without_running);
    try std.testing.expect(teardown.stop_allowed_by_watchdog_core);
    try std.testing.expect(teardown.driver_stop_invoked);
    try std.testing.expect(teardown.disable_requested);
    try std.testing.expect(teardown.disable_performs_eternal_ping);
    try std.testing.expect(!teardown.disable_returns_toggle_line_to_input);
    try std.testing.expect(teardown.disable_keeps_level_line_output);
    try std.testing.expect(!teardown.final_running);
    try std.testing.expect(teardown.final_line_state);
    try std.testing.expect(teardown.final_line_is_output);
    try std.testing.expectEqual(@as(usize, 1), teardown.disable_count);
}

test "phase11 gpio_wdt registration summaries keep the bounded register-device surface explicit" {
    var prestarted_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, true);
    const prestarted_handoff = prestarted_watchdog.registrationHandoffSummary(true);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, prestarted_handoff.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, prestarted_handoff.start_mode);
    try std.testing.expect(prestarted_handoff.reaches_registration_running);
    try std.testing.expect(prestarted_handoff.reaches_registration_line_state);
    try std.testing.expect(prestarted_handoff.reaches_registration_line_is_output);
    try std.testing.expect(!prestarted_handoff.stop_allowed_by_watchdog_core);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, prestarted_handoff.pre_registration_stop_disposition);
    try std.testing.expect(prestarted_handoff.timeout_init_requested);
    try std.testing.expect(prestarted_handoff.stop_on_reboot);
    try std.testing.expect(prestarted_handoff.parent_attached);

    const prestarted_plan = prestarted_watchdog.registrationPlanSummary(true);
    try std.testing.expectEqual(gpio_wdt.RegistrationSurface.watchdog_device_metadata, prestarted_plan.selected_surface);
    try std.testing.expectEqual(gpio_wdt.ValidationFocus.pre_registration_metadata, prestarted_plan.validation_focus);
    try std.testing.expect(prestarted_plan.watchdog_info_ready);
    try std.testing.expect(prestarted_plan.watchdog_ops_ready);
    try std.testing.expect(prestarted_plan.watchdog_device_ready);
    try std.testing.expect(prestarted_plan.descriptor_request_ready);
    try std.testing.expect(prestarted_plan.timeout_init_requested);
    try std.testing.expect(prestarted_plan.parent_attached);
    try std.testing.expect(prestarted_plan.stop_on_reboot);
    try std.testing.expect(prestarted_plan.reaches_registration_running);
    try std.testing.expect(prestarted_plan.reaches_registration_line_state);
    try std.testing.expect(prestarted_plan.reaches_registration_line_is_output);
    try std.testing.expect(!prestarted_plan.register_device_requested);
    try std.testing.expect(prestarted_plan.blocked_on_gpio_descriptor);
    try std.testing.expect(prestarted_plan.blocked_on_platform_registration);
    try std.testing.expect(prestarted_plan.blocked_on_reboot_glue);

    const prestarted_call = prestarted_watchdog.registerDeviceCallSummary(true);
    try std.testing.expectEqual(gpio_wdt.RegistrationSurface.devm_watchdog_register_device_call, prestarted_call.selected_surface);
    try std.testing.expectEqual(gpio_wdt.ValidationFocus.register_device_call_surface, prestarted_call.validation_focus);
    try std.testing.expect(prestarted_call.watchdog_info_ready);
    try std.testing.expect(prestarted_call.watchdog_ops_ready);
    try std.testing.expect(prestarted_call.watchdog_device_ready);
    try std.testing.expect(prestarted_call.descriptor_request_ready);
    try std.testing.expect(prestarted_call.watchdog_drvdata_set);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_min), prestarted_call.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_default), prestarted_call.default_timeout_sec);
    try std.testing.expectEqual(@as(u32, 20), prestarted_call.max_hw_heartbeat_ms);
    try std.testing.expect(prestarted_call.timeout_init_requested);
    try std.testing.expect(prestarted_call.nowayout_applied);
    try std.testing.expect(prestarted_call.parent_attached);
    try std.testing.expect(prestarted_call.stop_on_reboot);
    try std.testing.expect(prestarted_call.reaches_registration_running);
    try std.testing.expect(prestarted_call.reaches_registration_line_state);
    try std.testing.expect(prestarted_call.reaches_registration_line_is_output);
    try std.testing.expect(prestarted_call.register_device_requested);
    try std.testing.expect(prestarted_call.blocked_on_gpio_descriptor);
    try std.testing.expect(prestarted_call.blocked_on_platform_registration);
    try std.testing.expect(prestarted_call.blocked_on_reboot_glue);

    const failure = prestarted_watchdog.registerDeviceFailureSummary(true);
    try std.testing.expect(failure.register_device_requested);
    try std.testing.expect(failure.remains_summary_only);
    try std.testing.expectEqual(gpio_wdt.RegisterDeviceFailureMode.descriptor_preflight_pending, failure.primary_failure_mode);
    try std.testing.expectEqual(@as(u8, 3), failure.failure_mode_count);
    try std.testing.expect(failure.descriptor_preflight_pending);
    try std.testing.expect(failure.platform_registration_pending);
    try std.testing.expect(failure.reboot_glue_pending);
    try std.testing.expect(failure.preserves_registration_running_state);
    try std.testing.expect(failure.preserves_registration_line_state);
    try std.testing.expect(failure.preserves_registration_line_is_output);
}

test "phase11 gpio_wdt registration enums and dormant summaries stay aligned" {
    const registration_surface_fields = @typeInfo(gpio_wdt.RegistrationSurface).@"enum".fields;
    try std.testing.expectEqual(@as(usize, 2), registration_surface_fields.len);
    try std.testing.expectEqualStrings("watchdog_device_metadata", registration_surface_fields[0].name);
    try std.testing.expectEqualStrings("devm_watchdog_register_device_call", registration_surface_fields[1].name);

    const validation_focus_fields = @typeInfo(gpio_wdt.ValidationFocus).@"enum".fields;
    try std.testing.expectEqual(@as(usize, 2), validation_focus_fields.len);
    try std.testing.expectEqualStrings("pre_registration_metadata", validation_focus_fields[0].name);
    try std.testing.expectEqualStrings("register_device_call_surface", validation_focus_fields[1].name);

    var dormant_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const dormant_call = dormant_watchdog.registerDeviceCallSummary(false);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, dormant_call.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, dormant_call.start_mode);
    try std.testing.expect(!dormant_call.always_running);
    try std.testing.expect(!dormant_call.nowayout);
    try std.testing.expectEqual(@as(u32, 500), dormant_call.max_hw_heartbeat_ms);
    try std.testing.expect(!dormant_call.reaches_registration_running);
    try std.testing.expect(!dormant_call.reaches_registration_line_state);
    try std.testing.expect(dormant_call.reaches_registration_line_is_output);

    const dormant_failure = dormant_watchdog.registerDeviceFailureSummary(false);
    try std.testing.expectEqual(gpio_wdt.RegisterDeviceFailureMode.descriptor_preflight_pending, dormant_failure.primary_failure_mode);
    try std.testing.expectEqual(@as(u8, 3), dormant_failure.failure_mode_count);
    try std.testing.expect(!dormant_failure.preserves_registration_running_state);
    try std.testing.expect(!dormant_failure.preserves_registration_line_state);
    try std.testing.expect(dormant_failure.preserves_registration_line_is_output);
}
