const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio_wdt parses the bounded property surface and reports config limits" {
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

test "phase11 gpio_wdt watchdog metadata summary keeps the simple-driver contract explicit" {
    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    const toggle_metadata = toggle_watchdog.watchdogMetadataSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", toggle_metadata.anchor);
    try std.testing.expectEqualStrings("GPIO Watchdog", toggle_metadata.identity);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, toggle_metadata.hw_algo);
    try std.testing.expect(!toggle_metadata.always_running);
    try std.testing.expect(toggle_metadata.supports_set_timeout);
    try std.testing.expect(toggle_metadata.supports_magic_close);
    try std.testing.expect(toggle_metadata.supports_keepalive_ping);
    try std.testing.expect(toggle_metadata.start_op_ready);
    try std.testing.expect(toggle_metadata.stop_op_ready);
    try std.testing.expect(toggle_metadata.ping_op_ready);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_min), toggle_metadata.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_default), toggle_metadata.default_timeout_sec);
    try std.testing.expectEqual(@as(u32, 250), toggle_metadata.max_hw_heartbeat_ms);

    var level_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, true);
    const level_metadata = level_watchdog.watchdogMetadataSummary();
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, level_metadata.hw_algo);
    try std.testing.expect(level_metadata.always_running);
    try std.testing.expectEqual(@as(u32, 500), level_metadata.max_hw_heartbeat_ms);
}

test "phase11 gpio_wdt nowayout policy summary keeps module-param bookkeeping explicit" {
    const policy = gpio_wdt.GpioWatchdogLab.nowayoutPolicySummary();
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", policy.anchor);
    try std.testing.expectEqualStrings("nowayout", policy.module_param_name);
    try std.testing.expectEqual(gpio_wdt.NowayoutDefaultSource.watchdog_nowayout, policy.default_source);
    try std.testing.expect(policy.module_param_declared);
    try std.testing.expect(policy.module_param_is_bool);
    try std.testing.expect(policy.default_follows_watchdog_nowayout);
    try std.testing.expect(policy.applied_via_watchdog_set_nowayout);
    try std.testing.expect(policy.bounded_to_summary_bookkeeping);
}

test "phase11 gpio_wdt probe summary keeps startup and registration bookkeeping reviewable" {
    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, true);
    const toggle_probe = toggle_watchdog.probeSummary(true);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, toggle_probe.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, toggle_probe.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, toggle_probe.start_mode);
    try std.testing.expect(toggle_probe.starts_during_probe);
    try std.testing.expect(toggle_probe.pre_registration_running);
    try std.testing.expect(toggle_probe.pre_registration_line_is_output);
    try std.testing.expect(toggle_probe.pre_registration_line_state);
    try std.testing.expect(toggle_probe.parent_attached);
    try std.testing.expect(toggle_probe.stop_on_reboot);
    try std.testing.expect(toggle_probe.timeout_init_requested);
    try std.testing.expect(toggle_probe.nowayout);
    try std.testing.expectEqual(@as(u32, 20), toggle_probe.max_hw_heartbeat_ms);

    var level_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const level_probe = level_watchdog.probeSummary(false);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, level_probe.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, level_probe.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, level_probe.start_mode);
    try std.testing.expect(!level_probe.starts_during_probe);
    try std.testing.expect(!level_probe.pre_registration_running);
    try std.testing.expect(level_probe.pre_registration_line_is_output);
    try std.testing.expect(!level_probe.nowayout);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_default), level_probe.default_timeout_sec);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_min), level_probe.min_timeout_sec);
}

test "phase11 gpio_wdt toggle mode mirrors start, ping, and stop transitions" {
    var watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, false);

    var runtime = try watchdog.start();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.line_is_output);
    try std.testing.expect(runtime.line_state);
    try std.testing.expectEqual(@as(usize, 1), runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 0), runtime.pulse_count);
    try std.testing.expect(!runtime.last_ping_was_pulse);

    runtime = try watchdog.ping();
    try std.testing.expect(runtime.running);
    try std.testing.expect(!runtime.line_state);
    try std.testing.expectEqual(@as(usize, 2), runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 0), runtime.pulse_count);

    runtime = watchdog.stop();
    try std.testing.expect(!runtime.running);
    try std.testing.expect(!runtime.line_is_output);
    try std.testing.expect(runtime.line_state);
    try std.testing.expectEqual(@as(usize, 1), runtime.disable_count);
}

test "phase11 gpio_wdt level mode records pulses and keeps always-running hardware active" {
    var watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, true);

    var runtime = try watchdog.start();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.line_is_output);
    try std.testing.expect(!runtime.line_state);
    try std.testing.expectEqual(@as(usize, 1), runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 1), runtime.pulse_count);
    try std.testing.expect(runtime.last_ping_was_pulse);
    try std.testing.expectEqual(@as(u32, gpio_wdt.level_pulse_width_usec), runtime.last_pulse_width_usec);

    runtime = watchdog.stop();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.line_is_output);
    try std.testing.expect(!runtime.line_state);
    try std.testing.expectEqual(@as(usize, 0), runtime.disable_count);

    runtime = try watchdog.ping();
    try std.testing.expect(runtime.running);
    try std.testing.expectEqual(@as(usize, 2), runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 2), runtime.pulse_count);
}

test "phase11 gpio_wdt stop requests distinguish nowayout gating from always-running hardware" {
    var blocked_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, false);
    _ = try blocked_watchdog.start();
    const blocked = blocked_watchdog.requestStop(true);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, blocked.disposition);
    try std.testing.expect(!blocked.stop_allowed_by_watchdog_core);
    try std.testing.expect(!blocked.driver_stop_invoked);
    try std.testing.expect(blocked.running);
    try std.testing.expect(blocked.line_is_output);
    try std.testing.expectEqual(@as(usize, 0), blocked.disable_count);

    var blocked_always_running = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, true);
    _ = try blocked_always_running.start();
    const blocked_always_running_summary = blocked_always_running.requestStop(true);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, blocked_always_running_summary.disposition);
    try std.testing.expect(!blocked_always_running_summary.stop_allowed_by_watchdog_core);
    try std.testing.expect(!blocked_always_running_summary.driver_stop_invoked);
    try std.testing.expect(blocked_always_running_summary.running);
    try std.testing.expect(blocked_always_running_summary.line_state);
    try std.testing.expect(blocked_always_running_summary.line_is_output);
    try std.testing.expectEqual(@as(usize, 0), blocked_always_running_summary.disable_count);

    var dormant_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, false);
    const dormant = dormant_watchdog.requestStop(false);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, dormant.disposition);
    try std.testing.expect(dormant.stop_allowed_by_watchdog_core);
    try std.testing.expect(!dormant.driver_stop_invoked);
    try std.testing.expect(!dormant.running);
    try std.testing.expect(!dormant.line_state);
    try std.testing.expect(!dormant.line_is_output);
    try std.testing.expectEqual(@as(usize, 0), dormant.disable_count);

    var stoppable_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, false);
    _ = try stoppable_watchdog.start();
    const stopped = stoppable_watchdog.requestStop(false);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, stopped.disposition);
    try std.testing.expect(stopped.stop_allowed_by_watchdog_core);
    try std.testing.expect(stopped.driver_stop_invoked);
    try std.testing.expect(!stopped.running);
    try std.testing.expect(!stopped.line_is_output);
    try std.testing.expect(stopped.line_state);
    try std.testing.expectEqual(@as(usize, 1), stopped.disable_count);

    var always_running_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 50, true);
    _ = try always_running_watchdog.start();
    const kept_running = always_running_watchdog.requestStop(false);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.kept_running, kept_running.disposition);
    try std.testing.expect(kept_running.stop_allowed_by_watchdog_core);
    try std.testing.expect(kept_running.driver_stop_invoked);
    try std.testing.expect(kept_running.running);
    try std.testing.expect(kept_running.line_is_output);
    try std.testing.expectEqual(@as(usize, 0), kept_running.disable_count);
}

test "phase11 gpio_wdt teardown summary keeps disable ordering and failure modes reviewable" {
    var dormant_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, false);
    const dormant = try dormant_watchdog.summarizeTeardown(false);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, dormant.hw_algo);
    try std.testing.expect(!dormant.running_before_teardown);
    try std.testing.expect(dormant.teardown_skipped_without_running);
    try std.testing.expect(!dormant.stop_allowed_by_watchdog_core);
    try std.testing.expect(!dormant.driver_stop_invoked);
    try std.testing.expect(!dormant.disable_requested);
    try std.testing.expect(!dormant.disable_performs_eternal_ping);
    try std.testing.expect(!dormant.disable_returns_toggle_line_to_input);
    try std.testing.expect(!dormant.disable_keeps_level_line_output);
    try std.testing.expect(!dormant.stop_keeps_running_for_always_running);
    try std.testing.expect(!dormant.final_running);
    try std.testing.expect(!dormant.final_line_state);
    try std.testing.expect(!dormant.final_line_is_output);
    try std.testing.expectEqual(@as(usize, 0), dormant.disable_count);

    var blocked_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, false);
    _ = try blocked_watchdog.start();
    const blocked = try blocked_watchdog.summarizeTeardown(true);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, blocked.hw_algo);
    try std.testing.expect(blocked.running_before_teardown);
    try std.testing.expect(!blocked.teardown_skipped_without_running);
    try std.testing.expect(!blocked.stop_allowed_by_watchdog_core);
    try std.testing.expect(!blocked.driver_stop_invoked);
    try std.testing.expect(!blocked.disable_requested);
    try std.testing.expect(!blocked.disable_performs_eternal_ping);
    try std.testing.expect(!blocked.disable_returns_toggle_line_to_input);
    try std.testing.expect(!blocked.disable_keeps_level_line_output);
    try std.testing.expect(blocked.final_running);
    try std.testing.expect(blocked.final_line_is_output);
    try std.testing.expectEqual(@as(usize, 0), blocked.disable_count);

    var blocked_always_running_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, true);
    _ = try blocked_always_running_watchdog.start();
    const blocked_always_running = try blocked_always_running_watchdog.summarizeTeardown(true);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, blocked_always_running.hw_algo);
    try std.testing.expect(blocked_always_running.running_before_teardown);
    try std.testing.expect(!blocked_always_running.teardown_skipped_without_running);
    try std.testing.expect(!blocked_always_running.stop_allowed_by_watchdog_core);
    try std.testing.expect(!blocked_always_running.driver_stop_invoked);
    try std.testing.expect(!blocked_always_running.disable_requested);
    try std.testing.expect(!blocked_always_running.disable_performs_eternal_ping);
    try std.testing.expect(!blocked_always_running.disable_returns_toggle_line_to_input);
    try std.testing.expect(!blocked_always_running.disable_keeps_level_line_output);
    try std.testing.expect(!blocked_always_running.stop_keeps_running_for_always_running);
    try std.testing.expect(blocked_always_running.final_running);
    try std.testing.expect(blocked_always_running.final_line_state);
    try std.testing.expect(blocked_always_running.final_line_is_output);
    try std.testing.expectEqual(@as(usize, 0), blocked_always_running.disable_count);

    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, false);
    _ = try toggle_watchdog.start();
    const toggle_teardown = try toggle_watchdog.summarizeTeardown(false);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, toggle_teardown.hw_algo);
    try std.testing.expect(toggle_teardown.running_before_teardown);
    try std.testing.expect(!toggle_teardown.teardown_skipped_without_running);
    try std.testing.expect(toggle_teardown.stop_allowed_by_watchdog_core);
    try std.testing.expect(toggle_teardown.driver_stop_invoked);
    try std.testing.expect(toggle_teardown.disable_requested);
    try std.testing.expect(toggle_teardown.disable_performs_eternal_ping);
    try std.testing.expect(toggle_teardown.disable_returns_toggle_line_to_input);
    try std.testing.expect(!toggle_teardown.disable_keeps_level_line_output);
    try std.testing.expect(!toggle_teardown.stop_keeps_running_for_always_running);
    try std.testing.expect(!toggle_teardown.final_running);
    try std.testing.expect(toggle_teardown.final_line_state);
    try std.testing.expect(!toggle_teardown.final_line_is_output);
    try std.testing.expectEqual(@as(usize, 1), toggle_teardown.disable_count);

    var level_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 50, false);
    _ = try level_watchdog.start();
    const level_teardown = try level_watchdog.summarizeTeardown(false);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, level_teardown.hw_algo);
    try std.testing.expect(level_teardown.running_before_teardown);
    try std.testing.expect(!level_teardown.teardown_skipped_without_running);
    try std.testing.expect(level_teardown.disable_requested);
    try std.testing.expect(level_teardown.disable_performs_eternal_ping);
    try std.testing.expect(!level_teardown.disable_returns_toggle_line_to_input);
    try std.testing.expect(level_teardown.disable_keeps_level_line_output);
    try std.testing.expect(!level_teardown.final_running);
    try std.testing.expect(level_teardown.final_line_state);
    try std.testing.expect(level_teardown.final_line_is_output);
    try std.testing.expectEqual(@as(usize, 1), level_teardown.disable_count);

    var always_running_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 50, true);
    _ = try always_running_watchdog.start();
    const always_running = try always_running_watchdog.summarizeTeardown(false);
    try std.testing.expect(always_running.running_before_teardown);
    try std.testing.expect(!always_running.teardown_skipped_without_running);
    try std.testing.expect(always_running.stop_allowed_by_watchdog_core);
    try std.testing.expect(always_running.driver_stop_invoked);
    try std.testing.expect(!always_running.disable_requested);
    try std.testing.expect(!always_running.disable_performs_eternal_ping);
    try std.testing.expect(!always_running.disable_returns_toggle_line_to_input);
    try std.testing.expect(!always_running.disable_keeps_level_line_output);
    try std.testing.expect(always_running.stop_keeps_running_for_always_running);
    try std.testing.expect(always_running.final_running);
    try std.testing.expect(!always_running.final_line_state);
    try std.testing.expect(always_running.final_line_is_output);
    try std.testing.expectEqual(@as(usize, 0), always_running.disable_count);
}

test "phase11 gpio_wdt registration handoff summary records startup state and stop policy" {
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

    var dormant_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const dormant_handoff = dormant_watchdog.registrationHandoffSummary(false);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, dormant_handoff.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, dormant_handoff.start_mode);
    try std.testing.expect(!dormant_handoff.reaches_registration_running);
    try std.testing.expect(!dormant_handoff.reaches_registration_line_state);
    try std.testing.expect(dormant_handoff.reaches_registration_line_is_output);
    try std.testing.expect(dormant_handoff.stop_allowed_by_watchdog_core);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, dormant_handoff.pre_registration_stop_disposition);
}

test "phase11 gpio_wdt registration plan summary keeps the first registration surface explicit" {
    var prestarted_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, true);
    const prestarted_plan = prestarted_watchdog.registrationPlanSummary(true);
    try std.testing.expectEqual(gpio_wdt.RegistrationSurface.watchdog_device_metadata, prestarted_plan.selected_surface);
    try std.testing.expectEqual(gpio_wdt.ValidationFocus.pre_registration_metadata, prestarted_plan.validation_focus);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, prestarted_plan.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, prestarted_plan.start_mode);
    try std.testing.expect(prestarted_plan.always_running);
    try std.testing.expect(prestarted_plan.nowayout);
    try std.testing.expect(prestarted_plan.watchdog_info_ready);
    try std.testing.expect(prestarted_plan.watchdog_ops_ready);
    try std.testing.expect(prestarted_plan.watchdog_device_ready);
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

    var dormant_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const dormant_plan = dormant_watchdog.registrationPlanSummary(false);
    try std.testing.expectEqual(gpio_wdt.RegistrationSurface.watchdog_device_metadata, dormant_plan.selected_surface);
    try std.testing.expectEqual(gpio_wdt.ValidationFocus.pre_registration_metadata, dormant_plan.validation_focus);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, dormant_plan.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, dormant_plan.start_mode);
    try std.testing.expect(!dormant_plan.always_running);
    try std.testing.expect(!dormant_plan.nowayout);
    try std.testing.expect(!dormant_plan.reaches_registration_running);
    try std.testing.expect(!dormant_plan.reaches_registration_line_state);
    try std.testing.expect(dormant_plan.reaches_registration_line_is_output);
    try std.testing.expect(!dormant_plan.register_device_requested);
    try std.testing.expect(dormant_plan.blocked_on_gpio_descriptor);
    try std.testing.expect(dormant_plan.blocked_on_platform_registration);
    try std.testing.expect(dormant_plan.blocked_on_reboot_glue);
}

test "phase11 gpio_wdt register-device call summary keeps the first bounded request explicit" {
    var prestarted_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, true);
    const prestarted_call = prestarted_watchdog.registerDeviceCallSummary(true);
    try std.testing.expectEqual(gpio_wdt.RegistrationSurface.devm_watchdog_register_device_call, prestarted_call.selected_surface);
    try std.testing.expectEqual(gpio_wdt.ValidationFocus.register_device_call_surface, prestarted_call.validation_focus);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, prestarted_call.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, prestarted_call.start_mode);
    try std.testing.expect(prestarted_call.always_running);
    try std.testing.expect(prestarted_call.nowayout);
    try std.testing.expect(prestarted_call.watchdog_info_ready);
    try std.testing.expect(prestarted_call.watchdog_ops_ready);
    try std.testing.expect(prestarted_call.watchdog_device_ready);
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

    var dormant_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const dormant_call = dormant_watchdog.registerDeviceCallSummary(false);
    try std.testing.expectEqual(gpio_wdt.RegistrationSurface.devm_watchdog_register_device_call, dormant_call.selected_surface);
    try std.testing.expectEqual(gpio_wdt.ValidationFocus.register_device_call_surface, dormant_call.validation_focus);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, dormant_call.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, dormant_call.start_mode);
    try std.testing.expect(!dormant_call.always_running);
    try std.testing.expect(!dormant_call.nowayout);
    try std.testing.expect(!dormant_call.nowayout_applied);
    try std.testing.expectEqual(@as(u32, 500), dormant_call.max_hw_heartbeat_ms);
    try std.testing.expect(!dormant_call.reaches_registration_running);
    try std.testing.expect(!dormant_call.reaches_registration_line_state);
    try std.testing.expect(dormant_call.reaches_registration_line_is_output);
    try std.testing.expect(dormant_call.register_device_requested);
    try std.testing.expect(dormant_call.blocked_on_gpio_descriptor);
    try std.testing.expect(dormant_call.blocked_on_platform_registration);
    try std.testing.expect(dormant_call.blocked_on_reboot_glue);
}

test "phase11 gpio_wdt platform-driver identity keeps probe ownership and wrapper choice explicit" {
    const surface = gpio_wdt.GpioWatchdogLab.platformDriverIdentitySummary();
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", surface.anchor);
    try std.testing.expectEqualStrings("gpio-wdt", surface.driver_name);
    try std.testing.expectEqualStrings("linux,wdt-gpio", surface.of_compatible);
    try std.testing.expectEqualStrings("gpio_wdt_probe", surface.probe_callback);
    try std.testing.expectEqual(gpio_wdt.PlatformDriverRegistrationMode.module_platform_driver, surface.default_registration_mode);
    try std.testing.expect(surface.supports_arch_initcall_override);
    try std.testing.expect(surface.of_match_table_ready);
    try std.testing.expect(surface.platform_probe_ready);
}

test "phase11 gpio_wdt registration planning enums include the first real call surface and platform wrapper choices" {
    const registration_surface_fields = @typeInfo(gpio_wdt.RegistrationSurface).@"enum".fields;
    try std.testing.expectEqual(@as(usize, 2), registration_surface_fields.len);
    try std.testing.expectEqualStrings("watchdog_device_metadata", registration_surface_fields[0].name);
    try std.testing.expectEqualStrings("devm_watchdog_register_device_call", registration_surface_fields[1].name);

    const validation_focus_fields = @typeInfo(gpio_wdt.ValidationFocus).@"enum".fields;
    try std.testing.expectEqual(@as(usize, 2), validation_focus_fields.len);
    try std.testing.expectEqualStrings("pre_registration_metadata", validation_focus_fields[0].name);
    try std.testing.expectEqualStrings("register_device_call_surface", validation_focus_fields[1].name);

    const wrapper_fields = @typeInfo(gpio_wdt.PlatformDriverRegistrationMode).@"enum".fields;
    try std.testing.expectEqual(@as(usize, 2), wrapper_fields.len);
    try std.testing.expectEqualStrings("module_platform_driver", wrapper_fields[0].name);
    try std.testing.expectEqualStrings("arch_initcall_platform_driver", wrapper_fields[1].name);
}

test "phase11 gpio_wdt always-running toggle teardown keeps the line asserted without disable" {
    var watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 50, true);
    _ = try watchdog.start();

    const summary = try watchdog.summarizeTeardown(false);
    try std.testing.expect(summary.always_running);
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
    try std.testing.expect(summary.final_line_state);
    try std.testing.expect(summary.final_line_is_output);
    try std.testing.expectEqual(@as(usize, 0), summary.disable_count);
}
