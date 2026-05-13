const std = @import("std");

pub const TeardownState = enum {
    blocked_missing_drvdata,
    inactive_teardown,
    running_teardown,
};

pub const StopTeardownRequest = struct {
    drvdata_ready: bool,
    watchdog_registered: bool,
    hardware_running: bool,
    restart_priority_registered: bool,
    stop_on_reboot_registered: bool,
};

pub const StopTeardownSummary = struct {
    anchor: []const u8,
    unregister_device_call: []const u8,
    stop_on_reboot_call: []const u8,
    restart_priority_call: []const u8,
    stop_call: []const u8,
    control_anchor: []const u8,
    unregister_device_requested: bool,
    unregister_stop_on_reboot_requested: bool,
    clear_restart_priority_requested: bool,
    stop_requested: bool,
    keeps_missing_drvdata_explicit: bool,
    state: TeardownState,
};

pub fn summarizeStopTeardown(request: StopTeardownRequest) StopTeardownSummary {
    if (!request.drvdata_ready) {
        return .{
            .anchor = "drivers/watchdog/dw_wdt.c",
            .unregister_device_call = "watchdog_unregister_device",
            .stop_on_reboot_call = "watchdog_stop_on_reboot",
            .restart_priority_call = "watchdog_set_restart_priority",
            .stop_call = "dw_wdt_stop",
            .control_anchor = "WDOG_CONTROL_REG_OFFSET",
            .unregister_device_requested = false,
            .unregister_stop_on_reboot_requested = false,
            .clear_restart_priority_requested = false,
            .stop_requested = false,
            .keeps_missing_drvdata_explicit = true,
            .state = .blocked_missing_drvdata,
        };
    }

    return .{
        .anchor = "drivers/watchdog/dw_wdt.c",
        .unregister_device_call = "watchdog_unregister_device",
        .stop_on_reboot_call = "watchdog_stop_on_reboot",
        .restart_priority_call = "watchdog_set_restart_priority",
        .stop_call = "dw_wdt_stop",
        .control_anchor = "WDOG_CONTROL_REG_OFFSET",
        .unregister_device_requested = request.watchdog_registered,
        .unregister_stop_on_reboot_requested = request.stop_on_reboot_registered,
        .clear_restart_priority_requested = request.restart_priority_registered,
        .stop_requested = request.hardware_running,
        .keeps_missing_drvdata_explicit = false,
        .state = if (request.hardware_running) .running_teardown else .inactive_teardown,
    };
}

pub const RestartFailureState = enum {
    blocked_missing_drvdata,
    blocked_missing_timeout_image,
    restart_ready,
};

pub const RestartFailureModeRequest = struct {
    drvdata_ready: bool,
    timeout_image_ready: bool,
    restart_priority_registered: bool,
    reset_pulse_available: bool,
};

pub const RestartFailureModeSummary = struct {
    anchor: []const u8,
    restart_call: []const u8,
    timeout_range_anchor: []const u8,
    control_anchor: []const u8,
    restart_priority_call: []const u8,
    restart_requested: bool,
    writes_timeout_range: bool,
    writes_control: bool,
    restart_priority_registered: bool,
    expects_reset_pulse: bool,
    keeps_missing_drvdata_explicit: bool,
    keeps_missing_timeout_image_explicit: bool,
    state: RestartFailureState,
};

pub fn summarizeRestartFailureMode(request: RestartFailureModeRequest) RestartFailureModeSummary {
    if (!request.drvdata_ready) {
        return .{
            .anchor = "drivers/watchdog/dw_wdt.c",
            .restart_call = "dw_wdt_restart",
            .timeout_range_anchor = "WDOG_TIMEOUT_RANGE_REG_OFFSET",
            .control_anchor = "WDOG_CONTROL_REG_OFFSET",
            .restart_priority_call = "watchdog_set_restart_priority",
            .restart_requested = false,
            .writes_timeout_range = false,
            .writes_control = false,
            .restart_priority_registered = request.restart_priority_registered,
            .expects_reset_pulse = request.reset_pulse_available,
            .keeps_missing_drvdata_explicit = true,
            .keeps_missing_timeout_image_explicit = false,
            .state = .blocked_missing_drvdata,
        };
    }

    if (!request.timeout_image_ready) {
        return .{
            .anchor = "drivers/watchdog/dw_wdt.c",
            .restart_call = "dw_wdt_restart",
            .timeout_range_anchor = "WDOG_TIMEOUT_RANGE_REG_OFFSET",
            .control_anchor = "WDOG_CONTROL_REG_OFFSET",
            .restart_priority_call = "watchdog_set_restart_priority",
            .restart_requested = false,
            .writes_timeout_range = false,
            .writes_control = false,
            .restart_priority_registered = request.restart_priority_registered,
            .expects_reset_pulse = request.reset_pulse_available,
            .keeps_missing_drvdata_explicit = false,
            .keeps_missing_timeout_image_explicit = true,
            .state = .blocked_missing_timeout_image,
        };
    }

    return .{
        .anchor = "drivers/watchdog/dw_wdt.c",
        .restart_call = "dw_wdt_restart",
        .timeout_range_anchor = "WDOG_TIMEOUT_RANGE_REG_OFFSET",
        .control_anchor = "WDOG_CONTROL_REG_OFFSET",
        .restart_priority_call = "watchdog_set_restart_priority",
        .restart_requested = true,
        .writes_timeout_range = true,
        .writes_control = true,
        .restart_priority_registered = request.restart_priority_registered,
        .expects_reset_pulse = request.reset_pulse_available,
        .keeps_missing_drvdata_explicit = false,
        .keeps_missing_timeout_image_explicit = false,
        .state = .restart_ready,
    };
}

test "phase11 dw_wdt verify keeps stop teardown ownership explicit" {
    const summary = summarizeStopTeardown(.{
        .drvdata_ready = true,
        .watchdog_registered = true,
        .hardware_running = true,
        .restart_priority_registered = true,
        .stop_on_reboot_registered = true,
    });

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", summary.anchor);
    try std.testing.expectEqualStrings("watchdog_unregister_device", summary.unregister_device_call);
    try std.testing.expectEqualStrings("watchdog_stop_on_reboot", summary.stop_on_reboot_call);
    try std.testing.expectEqualStrings("watchdog_set_restart_priority", summary.restart_priority_call);
    try std.testing.expectEqualStrings("dw_wdt_stop", summary.stop_call);
    try std.testing.expectEqualStrings("WDOG_CONTROL_REG_OFFSET", summary.control_anchor);
    try std.testing.expect(summary.unregister_device_requested);
    try std.testing.expect(summary.unregister_stop_on_reboot_requested);
    try std.testing.expect(summary.clear_restart_priority_requested);
    try std.testing.expect(summary.stop_requested);
    try std.testing.expectEqual(TeardownState.running_teardown, summary.state);
}

test "phase11 dw_wdt verify keeps inactive and missing-drvdata teardown paths distinct" {
    const inactive = summarizeStopTeardown(.{
        .drvdata_ready = true,
        .watchdog_registered = true,
        .hardware_running = false,
        .restart_priority_registered = false,
        .stop_on_reboot_registered = false,
    });
    try std.testing.expect(inactive.unregister_device_requested);
    try std.testing.expect(!inactive.unregister_stop_on_reboot_requested);
    try std.testing.expect(!inactive.clear_restart_priority_requested);
    try std.testing.expect(!inactive.stop_requested);
    try std.testing.expectEqual(TeardownState.inactive_teardown, inactive.state);

    const blocked = summarizeStopTeardown(.{
        .drvdata_ready = false,
        .watchdog_registered = true,
        .hardware_running = true,
        .restart_priority_registered = true,
        .stop_on_reboot_registered = true,
    });
    try std.testing.expect(!blocked.unregister_device_requested);
    try std.testing.expect(!blocked.unregister_stop_on_reboot_requested);
    try std.testing.expect(!blocked.clear_restart_priority_requested);
    try std.testing.expect(!blocked.stop_requested);
    try std.testing.expect(blocked.keeps_missing_drvdata_explicit);
    try std.testing.expectEqual(TeardownState.blocked_missing_drvdata, blocked.state);
}

test "phase11 dw_wdt verify keeps restart failure modes explicit" {
    const blocked_timeout = summarizeRestartFailureMode(.{
        .drvdata_ready = true,
        .timeout_image_ready = false,
        .restart_priority_registered = true,
        .reset_pulse_available = true,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", blocked_timeout.anchor);
    try std.testing.expectEqualStrings("dw_wdt_restart", blocked_timeout.restart_call);
    try std.testing.expectEqualStrings("WDOG_TIMEOUT_RANGE_REG_OFFSET", blocked_timeout.timeout_range_anchor);
    try std.testing.expectEqualStrings("WDOG_CONTROL_REG_OFFSET", blocked_timeout.control_anchor);
    try std.testing.expect(!blocked_timeout.restart_requested);
    try std.testing.expect(!blocked_timeout.writes_timeout_range);
    try std.testing.expect(!blocked_timeout.writes_control);
    try std.testing.expect(blocked_timeout.keeps_missing_timeout_image_explicit);
    try std.testing.expectEqual(RestartFailureState.blocked_missing_timeout_image, blocked_timeout.state);

    const ready = summarizeRestartFailureMode(.{
        .drvdata_ready = true,
        .timeout_image_ready = true,
        .restart_priority_registered = true,
        .reset_pulse_available = false,
    });
    try std.testing.expect(ready.restart_requested);
    try std.testing.expect(ready.writes_timeout_range);
    try std.testing.expect(ready.writes_control);
    try std.testing.expect(ready.restart_priority_registered);
    try std.testing.expect(!ready.expects_reset_pulse);
    try std.testing.expectEqual(RestartFailureState.restart_ready, ready.state);
}

test "phase11 dw_wdt verify keeps missing-drvdata restart failures explicit" {
    const blocked_drvdata = summarizeRestartFailureMode(.{
        .drvdata_ready = false,
        .timeout_image_ready = true,
        .restart_priority_registered = false,
        .reset_pulse_available = true,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", blocked_drvdata.anchor);
    try std.testing.expectEqualStrings("dw_wdt_restart", blocked_drvdata.restart_call);
    try std.testing.expectEqualStrings("WDOG_TIMEOUT_RANGE_REG_OFFSET", blocked_drvdata.timeout_range_anchor);
    try std.testing.expectEqualStrings("WDOG_CONTROL_REG_OFFSET", blocked_drvdata.control_anchor);
    try std.testing.expect(!blocked_drvdata.restart_requested);
    try std.testing.expect(!blocked_drvdata.writes_timeout_range);
    try std.testing.expect(!blocked_drvdata.writes_control);
    try std.testing.expect(!blocked_drvdata.restart_priority_registered);
    try std.testing.expect(blocked_drvdata.expects_reset_pulse);
    try std.testing.expect(blocked_drvdata.keeps_missing_drvdata_explicit);
    try std.testing.expect(!blocked_drvdata.keeps_missing_timeout_image_explicit);
    try std.testing.expectEqual(RestartFailureState.blocked_missing_drvdata, blocked_drvdata.state);
}
