const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio watchdog keeps descriptor preflight glued to timeout and drvdata ordering" {
    const toggle = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    const preflight = toggle.descriptorPreflightSummary();
    const descriptor = toggle.descriptorRequestSummary();
    const timeout = toggle.timeoutPropertyCheckpointSummary();
    const platform_drvdata = toggle.platformDrvdataCheckpointSummary();
    const watchdog_drvdata = toggle.watchdogDrvdataCheckpointSummary();

    try std.testing.expectEqualDeep(descriptor, preflight);
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", preflight.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, preflight.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.input, preflight.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.in, preflight.descriptor_flags);
    try std.testing.expect(preflight.descriptor_lookup_required);
    try std.testing.expect(preflight.hw_algo_selected_before_lookup);
    try std.testing.expect(preflight.lookup_precedes_margin_validation);
    try std.testing.expect(preflight.lookup_precedes_always_running_read);
    try std.testing.expect(preflight.lookup_precedes_registration_handoff);
    try std.testing.expect(preflight.blocked_on_live_gpio_lookup);
    try std.testing.expect(preflight.blocked_on_platform_registration);

    try std.testing.expectEqualStrings("hw_margin_ms", timeout.timeout_property_name);
    try std.testing.expectEqual(@as(u32, 250), timeout.hw_margin_ms);
    try std.testing.expect(timeout.timeout_property_required);
    try std.testing.expect(timeout.descriptor_lookup_precedes_timeout_property);
    try std.testing.expect(timeout.timeout_property_precedes_always_running_read);
    try std.testing.expect(timeout.timeout_property_precedes_registration_handoff);
    try std.testing.expect(timeout.blocked_on_live_gpio_lookup);
    try std.testing.expect(timeout.blocked_on_platform_registration);

    try std.testing.expect(platform_drvdata.parent_attached);
    try std.testing.expect(platform_drvdata.module_owner_attached);
    try std.testing.expectEqualStrings("gpio_wdt_priv", platform_drvdata.drvdata_owner_identity);
    try std.testing.expect(platform_drvdata.timeout_property_precedes_drvdata_binding);
    try std.testing.expect(platform_drvdata.drvdata_binding_precedes_registration_handoff);
    try std.testing.expect(platform_drvdata.drvdata_binding_reuses_parent_linkage);
    try std.testing.expect(platform_drvdata.blocked_on_live_gpio_lookup);
    try std.testing.expect(platform_drvdata.blocked_on_platform_registration);

    try std.testing.expect(watchdog_drvdata.parent_attached);
    try std.testing.expect(watchdog_drvdata.module_owner_attached);
    try std.testing.expectEqualStrings("gpio_wdt_priv", watchdog_drvdata.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings("gpio_wdt_priv", watchdog_drvdata.watchdog_drvdata_owner_identity);
    try std.testing.expect(watchdog_drvdata.timeout_property_precedes_platform_drvdata);
    try std.testing.expect(watchdog_drvdata.platform_drvdata_precedes_watchdog_drvdata);
    try std.testing.expect(watchdog_drvdata.watchdog_drvdata_precedes_registration_handoff);
    try std.testing.expect(watchdog_drvdata.watchdog_drvdata_reuses_parent_linkage);
    try std.testing.expect(watchdog_drvdata.blocked_on_live_gpio_lookup);
    try std.testing.expect(watchdog_drvdata.blocked_on_platform_registration);
    try std.testing.expect(watchdog_drvdata.blocked_on_reboot_glue);
}

test "phase11 gpio watchdog keeps always-running level preflight reviewable before reboot glue" {
    const level = try gpio_wdt.GpioWatchdogLab.init(.level, 400, true);
    const preflight = level.descriptorPreflightSummary();
    const descriptor = level.descriptorRequestSummary();
    const timeout = level.timeoutPropertyCheckpointSummary();
    const platform_drvdata = level.platformDrvdataCheckpointSummary();
    const watchdog_drvdata = level.watchdogDrvdataCheckpointSummary();

    try std.testing.expectEqualDeep(descriptor, preflight);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, preflight.hw_algo);
    try std.testing.expectEqual(gpio_wdt.ProbeLineRequest.output_low, preflight.requested_line);
    try std.testing.expectEqual(gpio_wdt.DescriptorRequestFlags.out_low, preflight.descriptor_flags);
    try std.testing.expect(preflight.lookup_precedes_margin_validation);
    try std.testing.expect(preflight.lookup_precedes_always_running_read);
    try std.testing.expect(preflight.lookup_precedes_registration_handoff);

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
}
