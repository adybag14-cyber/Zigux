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
    try std.testing.expect(!level_probe.pre_registration_line_state);
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

test "phase11 gpio_wdt level stop keeps disable-state teardown reviewable" {
    var watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);

    var runtime = try watchdog.start();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.line_is_output);
    try std.testing.expect(!runtime.line_state);
    try std.testing.expect(runtime.last_ping_was_pulse);
    try std.testing.expectEqual(@as(u32, gpio_wdt.level_pulse_width_usec), runtime.last_pulse_width_usec);

    runtime = watchdog.stop();
    try std.testing.expect(!runtime.running);
    try std.testing.expect(runtime.line_is_output);
    try std.testing.expect(runtime.line_state);
    try std.testing.expectEqual(@as(usize, 1), runtime.disable_count);
    try std.testing.expectEqual(@as(usize, 1), runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 1), runtime.pulse_count);
    try std.testing.expect(!runtime.last_ping_was_pulse);
    try std.testing.expectEqual(@as(u32, 0), runtime.last_pulse_width_usec);
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

test "phase11 gpio_wdt descriptor preflight keeps the first devm_gpiod_get boundary explicit" {
    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, true);
    const toggle_preflight = toggle_watchdog.descriptorPreflightSummary();
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, toggle_preflight.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, toggle_preflight.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.in, toggle_preflight.descriptor_flags);
    try std.testing.expect(toggle_preflight.descriptor_lookup_required);
    try std.testing.expect(toggle_preflight.hw_algo_selected_before_lookup);
    try std.testing.expect(toggle_preflight.lookup_precedes_margin_validation);
    try std.testing.expect(toggle_preflight.lookup_precedes_always_running_read);
    try std.testing.expect(toggle_preflight.lookup_precedes_registration_handoff);
    try std.testing.expect(toggle_preflight.blocked_on_live_gpio_lookup);
    try std.testing.expect(toggle_preflight.blocked_on_platform_registration);

    var level_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const level_preflight = level_watchdog.descriptorPreflightSummary();
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, level_preflight.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, level_preflight.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.out_low, level_preflight.descriptor_flags);
    try std.testing.expect(level_preflight.descriptor_lookup_required);
    try std.testing.expect(level_preflight.lookup_precedes_margin_validation);
    try std.testing.expect(level_preflight.lookup_precedes_always_running_read);
    try std.testing.expect(level_preflight.lookup_precedes_registration_handoff);
    try std.testing.expect(level_preflight.blocked_on_live_gpio_lookup);
    try std.testing.expect(level_preflight.blocked_on_platform_registration);
}

test "phase11 gpio_wdt timeout-property checkpoint keeps ordering and failure gating explicit" {
    var toggle_watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, true);
    const toggle_checkpoint = toggle_watchdog.timeoutPropertyCheckpointSummary();
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, toggle_checkpoint.hw_algo);
    try std.testing.expectEqual(@as(u32, 20), toggle_checkpoint.hw_margin_ms);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, toggle_checkpoint.requested_line);
    try std.testing.expect(toggle_checkpoint.timeout_property_required);
    try std.testing.expect(toggle_checkpoint.descriptor_lookup_precedes_timeout_property);
    try std.testing.expect(toggle_checkpoint.timeout_property_bounds_checked);
    try std.testing.expect(toggle_checkpoint.timeout_property_precedes_always_running_read);
    try std.testing.expect(toggle_checkpoint.timeout_property_precedes_watchdog_drvdata_handoff);
    try std.testing.expect(toggle_checkpoint.timeout_property_precedes_registration_handoff);
    try std.testing.expect(toggle_checkpoint.invalid_timeout_blocks_later_handoffs);
    try std.testing.expect(toggle_checkpoint.blocked_on_live_property_read);
    try std.testing.expect(toggle_checkpoint.blocked_on_platform_registration);

    var level_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const level_checkpoint = level_watchdog.timeoutPropertyCheckpointSummary();
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, level_checkpoint.hw_algo);
    try std.testing.expectEqual(@as(u32, 500), level_checkpoint.hw_margin_ms);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, level_checkpoint.requested_line);
    try std.testing.expect(level_checkpoint.timeout_property_required);
    try std.testing.expect(level_checkpoint.descriptor_lookup_precedes_timeout_property);
    try std.testing.expect(level_checkpoint.timeout_property_bounds_checked);
    try std.testing.expect(level_checkpoint.timeout_property_precedes_always_running_read);
    try std.testing.expect(level_checkpoint.timeout_property_precedes_watchdog_drvdata_handoff);
    try std.testing.expect(level_checkpoint.timeout_property_precedes_registration_handoff);
    try std.testing.expect(level_checkpoint.invalid_timeout_blocks_later_handoffs);
    try std.testing.expect(level_checkpoint.blocked_on_live_property_read);
    try std.testing.expect(level_checkpoint.blocked_on_platform_registration);
}

test "phase11 gpio_wdt registration handoff summary records startup state, stop policy, and watchdog metadata" {
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
    try std.testing.expect(prestarted_handoff.module_owner_attached);
    try std.testing.expectEqualStrings("GPIO Watchdog", prestarted_handoff.identity);
    try std.testing.expectEqual(gpio_wdt.WatchdogOption.magicclose, prestarted_handoff.supported_options[0]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOption.keepaliveping, prestarted_handoff.supported_options[1]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOption.settimeout, prestarted_handoff.supported_options[2]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOp.start, prestarted_handoff.supported_ops[0]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOp.stop, prestarted_handoff.supported_ops[1]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOp.ping, prestarted_handoff.supported_ops[2]);

    var always_running_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 75, true);
    const kept_running_handoff = always_running_watchdog.registrationHandoffSummary(false);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, kept_running_handoff.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, kept_running_handoff.start_mode);
    try std.testing.expect(kept_running_handoff.reaches_registration_running);
    try std.testing.expect(!kept_running_handoff.reaches_registration_line_state);
    try std.testing.expect(kept_running_handoff.reaches_registration_line_is_output);
    try std.testing.expect(kept_running_handoff.stop_allowed_by_watchdog_core);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.kept_running, kept_running_handoff.pre_registration_stop_disposition);
    try std.testing.expect(kept_running_handoff.timeout_init_requested);
    try std.testing.expect(kept_running_handoff.stop_on_reboot);
    try std.testing.expect(kept_running_handoff.parent_attached);
    try std.testing.expect(kept_running_handoff.module_owner_attached);
    try std.testing.expectEqualStrings("GPIO Watchdog", kept_running_handoff.identity);
    try std.testing.expectEqual(gpio_wdt.WatchdogOption.magicclose, kept_running_handoff.supported_options[0]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOption.keepaliveping, kept_running_handoff.supported_options[1]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOption.settimeout, kept_running_handoff.supported_options[2]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOp.start, kept_running_handoff.supported_ops[0]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOp.stop, kept_running_handoff.supported_ops[1]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOp.ping, kept_running_handoff.supported_ops[2]);

    var dormant_watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, false);
    const dormant_handoff = dormant_watchdog.registrationHandoffSummary(false);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, dormant_handoff.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, dormant_handoff.start_mode);
    try std.testing.expect(!dormant_handoff.reaches_registration_running);
    try std.testing.expect(!dormant_handoff.reaches_registration_line_state);
    try std.testing.expect(dormant_handoff.reaches_registration_line_is_output);
    try std.testing.expect(dormant_handoff.stop_allowed_by_watchdog_core);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, dormant_handoff.pre_registration_stop_disposition);
    try std.testing.expect(dormant_handoff.module_owner_attached);
    try std.testing.expectEqualStrings("GPIO Watchdog", dormant_handoff.identity);
}
