const std = @import("std");

const dw_wdt_verify = @import("dw_wdt_verify");

test "phase11 dw_wdt keeps inactive teardown hooks and missing-timeout restart split explicit" {
    const teardown = dw_wdt_verify.summarizeStopTeardown(.{
        .drvdata_ready = true,
        .watchdog_registered = false,
        .hardware_running = false,
        .restart_priority_registered = true,
        .stop_on_reboot_registered = true,
    });

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", teardown.anchor);
    try std.testing.expectEqualStrings("watchdog_unregister_device", teardown.unregister_device_call);
    try std.testing.expect(!teardown.unregister_device_requested);
    try std.testing.expect(teardown.unregister_stop_on_reboot_requested);
    try std.testing.expect(teardown.clear_restart_priority_requested);
    try std.testing.expect(!teardown.stop_requested);
    try std.testing.expectEqual(dw_wdt_verify.TeardownState.inactive_teardown, teardown.state);

    const restart = dw_wdt_verify.summarizeRestartFailureMode(.{
        .drvdata_ready = true,
        .timeout_image_ready = false,
        .restart_priority_registered = true,
        .reset_pulse_available = true,
    });

    try std.testing.expectEqualStrings("dw_wdt_restart", restart.restart_call);
    try std.testing.expect(!restart.restart_requested);
    try std.testing.expect(!restart.writes_timeout_range);
    try std.testing.expect(!restart.writes_control);
    try std.testing.expect(restart.restart_priority_registered);
    try std.testing.expect(restart.expects_reset_pulse);
    try std.testing.expect(!restart.keeps_missing_drvdata_explicit);
    try std.testing.expect(restart.keeps_missing_timeout_image_explicit);
    try std.testing.expectEqual(
        dw_wdt_verify.RestartFailureState.blocked_missing_timeout_image,
        restart.state,
    );
}

test "phase11 dw_wdt keeps missing-drvdata teardown and restart guardrails aligned" {
    const teardown = dw_wdt_verify.summarizeStopTeardown(.{
        .drvdata_ready = false,
        .watchdog_registered = true,
        .hardware_running = true,
        .restart_priority_registered = true,
        .stop_on_reboot_registered = true,
    });

    try std.testing.expect(!teardown.unregister_device_requested);
    try std.testing.expect(!teardown.unregister_stop_on_reboot_requested);
    try std.testing.expect(!teardown.clear_restart_priority_requested);
    try std.testing.expect(!teardown.stop_requested);
    try std.testing.expect(teardown.keeps_missing_drvdata_explicit);
    try std.testing.expectEqual(dw_wdt_verify.TeardownState.blocked_missing_drvdata, teardown.state);

    const restart = dw_wdt_verify.summarizeRestartFailureMode(.{
        .drvdata_ready = false,
        .timeout_image_ready = true,
        .restart_priority_registered = false,
        .reset_pulse_available = false,
    });

    try std.testing.expect(!restart.restart_requested);
    try std.testing.expect(!restart.writes_timeout_range);
    try std.testing.expect(!restart.writes_control);
    try std.testing.expect(!restart.restart_priority_registered);
    try std.testing.expect(!restart.expects_reset_pulse);
    try std.testing.expect(restart.keeps_missing_drvdata_explicit);
    try std.testing.expect(!restart.keeps_missing_timeout_image_explicit);
    try std.testing.expectEqual(
        dw_wdt_verify.RestartFailureState.blocked_missing_drvdata,
        restart.state,
    );
}

test "phase11 dw_wdt keeps live-stop teardown separate from ready restart flow" {
    const teardown = dw_wdt_verify.summarizeStopTeardown(.{
        .drvdata_ready = true,
        .watchdog_registered = true,
        .hardware_running = true,
        .restart_priority_registered = false,
        .stop_on_reboot_registered = false,
    });

    try std.testing.expect(teardown.unregister_device_requested);
    try std.testing.expect(!teardown.unregister_stop_on_reboot_requested);
    try std.testing.expect(!teardown.clear_restart_priority_requested);
    try std.testing.expect(teardown.stop_requested);
    try std.testing.expectEqual(dw_wdt_verify.TeardownState.running_teardown, teardown.state);

    const restart = dw_wdt_verify.summarizeRestartFailureMode(.{
        .drvdata_ready = true,
        .timeout_image_ready = true,
        .restart_priority_registered = false,
        .reset_pulse_available = false,
    });

    try std.testing.expect(restart.restart_requested);
    try std.testing.expect(restart.writes_timeout_range);
    try std.testing.expect(restart.writes_control);
    try std.testing.expect(!restart.restart_priority_registered);
    try std.testing.expect(!restart.expects_reset_pulse);
    try std.testing.expect(!restart.keeps_missing_drvdata_explicit);
    try std.testing.expect(!restart.keeps_missing_timeout_image_explicit);
    try std.testing.expectEqual(dw_wdt_verify.RestartFailureState.restart_ready, restart.state);
}
