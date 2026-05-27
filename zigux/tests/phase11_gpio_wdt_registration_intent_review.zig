const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio watchdog keeps registration intent ordering explicit before register-device glue" {
    const prestarted = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, true);
    const intent = prestarted.registrationIntentCheckpointSummary(true);
    const handoff = prestarted.registrationHandoffSummary(true);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", intent.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, intent.hw_algo);
    try std.testing.expectEqual(@as(u32, 250), intent.hw_margin_ms);
    try std.testing.expect(intent.always_running);
    try std.testing.expect(intent.timeout_init_requested);
    try std.testing.expect(intent.nowayout_from_module_param);
    try std.testing.expect(intent.stop_on_reboot_requested);
    try std.testing.expect(intent.pre_registration_start_requested);
    try std.testing.expect(intent.timeout_init_stays_before_nowayout);
    try std.testing.expect(intent.nowayout_stays_before_stop_on_reboot);
    try std.testing.expect(intent.stop_on_reboot_stays_before_pre_registration_start);
    try std.testing.expect(intent.pre_registration_start_stays_before_registration);
    try std.testing.expect(intent.blocked_on_live_gpio_lookup);
    try std.testing.expect(intent.blocked_on_platform_registration);

    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.start_before_register, handoff.start_mode);
    try std.testing.expect(handoff.reaches_registration_running);
    try std.testing.expect(handoff.reaches_registration_line_state);
    try std.testing.expect(handoff.reaches_registration_line_is_output);
    try std.testing.expect(!handoff.stop_allowed_by_watchdog_core);
    try std.testing.expect(handoff.timeout_init_requested);
    try std.testing.expect(handoff.stop_on_reboot);
}

test "phase11 gpio watchdog keeps dormant registration intent distinct from always-running startup" {
    const dormant = try gpio_wdt.GpioWatchdogLab.init(.level, 400, false);
    const intent = dormant.registrationIntentCheckpointSummary(false);
    const handoff = dormant.registrationHandoffSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", intent.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, intent.hw_algo);
    try std.testing.expectEqual(@as(u32, 400), intent.hw_margin_ms);
    try std.testing.expect(!intent.always_running);
    try std.testing.expect(intent.timeout_init_requested);
    try std.testing.expect(!intent.nowayout_from_module_param);
    try std.testing.expect(intent.stop_on_reboot_requested);
    try std.testing.expect(!intent.pre_registration_start_requested);
    try std.testing.expect(intent.timeout_init_stays_before_nowayout);
    try std.testing.expect(intent.nowayout_stays_before_stop_on_reboot);
    try std.testing.expect(intent.stop_on_reboot_stays_before_pre_registration_start);
    try std.testing.expect(intent.pre_registration_start_stays_before_registration);
    try std.testing.expect(intent.blocked_on_live_gpio_lookup);
    try std.testing.expect(intent.blocked_on_platform_registration);

    try std.testing.expectEqual(gpio_wdt.ProbeStartMode.register_only, handoff.start_mode);
    try std.testing.expect(!handoff.reaches_registration_running);
    try std.testing.expect(!handoff.reaches_registration_line_state);
    try std.testing.expect(handoff.reaches_registration_line_is_output);
    try std.testing.expect(handoff.stop_allowed_by_watchdog_core);
    try std.testing.expect(handoff.timeout_init_requested);
    try std.testing.expect(handoff.stop_on_reboot);
}
