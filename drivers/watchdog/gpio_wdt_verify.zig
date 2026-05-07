const std = @import("std");
const gpio_wdt = @import("gpio_wdt.zig");

test "gpio_wdt register-device summary carries module ownership for toggle wiring" {
    const lab = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    const summary = lab.registerDeviceCallSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", summary.register_call);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, summary.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, summary.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.in, summary.descriptor_flags);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, summary.start_mode);
    try std.testing.expect(summary.watchdog_info_ready);
    try std.testing.expect(summary.watchdog_ops_ready);
    try std.testing.expect(summary.watchdog_device_ready);
    try std.testing.expect(summary.watchdog_drvdata_set);
    try std.testing.expect(summary.module_owner_attached);
    try std.testing.expect(summary.descriptor_request_ready);
    try std.testing.expect(summary.timeout_init_requested);
    try std.testing.expect(!summary.nowayout_applied);
    try std.testing.expect(summary.parent_attached);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expectEqual(@as(u32, 1), summary.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, 60), summary.default_timeout_sec);
    try std.testing.expectEqual(@as(u32, 250), summary.max_hw_heartbeat_ms);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.blocked_on_live_gpio_lookup);
    try std.testing.expect(summary.blocked_on_platform_registration);
    try std.testing.expect(summary.blocked_on_reboot_glue);
}

test "gpio_wdt registration handoff keeps always-running level ownership and start-before-register explicit" {
    const lab = try gpio_wdt.GpioWatchdogLab.init(.level, 900, true);
    const handoff = lab.registrationHandoffSummary(true);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", handoff.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, handoff.hw_algo);
    try std.testing.expect(handoff.always_running);
    try std.testing.expect(handoff.nowayout);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, handoff.requested_line);
    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, handoff.start_mode);
    try std.testing.expect(handoff.reaches_registration_running);
    try std.testing.expect(!handoff.reaches_registration_line_state);
    try std.testing.expect(handoff.reaches_registration_line_is_output);
    try std.testing.expect(!handoff.stop_allowed_by_watchdog_core);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, handoff.pre_registration_stop_disposition);
    try std.testing.expect(handoff.timeout_init_requested);
    try std.testing.expect(handoff.stop_on_reboot);
    try std.testing.expect(handoff.parent_attached);
    try std.testing.expect(handoff.module_owner_attached);
    try std.testing.expectEqualStrings("GPIO Watchdog", handoff.identity);
    try std.testing.expectEqual(gpio_wdt.WatchdogOption.magicclose, handoff.supported_options[0]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOption.keepaliveping, handoff.supported_options[1]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOption.settimeout, handoff.supported_options[2]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOp.start, handoff.supported_ops[0]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOp.stop, handoff.supported_ops[1]);
    try std.testing.expectEqual(gpio_wdt.WatchdogOp.ping, handoff.supported_ops[2]);
}

test "gpio_wdt teardown stops toggle hardware and returns line to tristate when stoppable" {
    var lab = try gpio_wdt.GpioWatchdogLab.init(.toggle, 128, false);
    const teardown = try lab.teardownSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", teardown.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, teardown.hw_algo);
    try std.testing.expect(!teardown.always_running);
    try std.testing.expect(!teardown.nowayout);
    try std.testing.expect(teardown.running_before_teardown);
    try std.testing.expect(teardown.line_state_before_teardown);
    try std.testing.expect(teardown.line_is_output_before_teardown);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, teardown.disposition);
    try std.testing.expect(teardown.stop_allowed_by_watchdog_core);
    try std.testing.expect(teardown.driver_stop_invoked);
    try std.testing.expect(!teardown.running_after_teardown);
    try std.testing.expect(teardown.line_state_after_teardown);
    try std.testing.expect(!teardown.line_is_output_after_teardown);
    try std.testing.expectEqual(@as(usize, 1), teardown.disable_count);
    try std.testing.expectEqual(@as(usize, 1), lab.runtimeSnapshot().disable_count);
}

test "gpio_wdt teardown keeps always-running level watchdog active when stop is allowed" {
    var lab = try gpio_wdt.GpioWatchdogLab.init(.level, 640, true);
    const teardown = try lab.teardownSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", teardown.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, teardown.hw_algo);
    try std.testing.expect(teardown.always_running);
    try std.testing.expect(!teardown.nowayout);
    try std.testing.expect(teardown.running_before_teardown);
    try std.testing.expect(!teardown.line_state_before_teardown);
    try std.testing.expect(teardown.line_is_output_before_teardown);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.kept_running, teardown.disposition);
    try std.testing.expect(teardown.stop_allowed_by_watchdog_core);
    try std.testing.expect(teardown.driver_stop_invoked);
    try std.testing.expect(teardown.running_after_teardown);
    try std.testing.expect(!teardown.line_state_after_teardown);
    try std.testing.expect(teardown.line_is_output_after_teardown);
    try std.testing.expectEqual(@as(usize, 0), teardown.disable_count);
    try std.testing.expectEqual(@as(usize, 1), lab.runtimeSnapshot().pulse_count);
}

test "gpio_wdt teardown leaves started toggle watchdog running when nowayout blocks stop" {
    var lab = try gpio_wdt.GpioWatchdogLab.init(.toggle, 333, false);
    const teardown = try lab.teardownSummary(true);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", teardown.anchor);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, teardown.disposition);
    try std.testing.expect(!teardown.stop_allowed_by_watchdog_core);
    try std.testing.expect(!teardown.driver_stop_invoked);
    try std.testing.expect(teardown.running_before_teardown);
    try std.testing.expect(teardown.running_after_teardown);
    try std.testing.expect(teardown.line_state_before_teardown);
    try std.testing.expect(teardown.line_state_after_teardown);
    try std.testing.expect(teardown.line_is_output_before_teardown);
    try std.testing.expect(teardown.line_is_output_after_teardown);
    try std.testing.expectEqual(@as(usize, 0), teardown.disable_count);
    try std.testing.expectEqual(@as(usize, 1), lab.runtimeSnapshot().ping_count);
}
