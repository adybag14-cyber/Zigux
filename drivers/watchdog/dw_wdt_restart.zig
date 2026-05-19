const std = @import("std");

pub const anchor_path = "drivers/watchdog/dw_wdt.c";

pub const RestartState = enum {
    blocked_missing_drvdata,
    blocked_missing_timeout_image,
    restart_ready,
};

pub const RestartRequest = struct {
    drvdata_ready: bool,
    timeout_image_ready: bool,
    restart_priority_registered: bool,
    reset_pulse_available: bool,
    keeps_live_mmio_execution_out_of_scope: bool = true,
};

pub const RestartSummary = struct {
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
    keeps_live_mmio_execution_out_of_scope: bool,
    blocked_on_live_mmio: bool,
    state: RestartState,
};

pub fn summarizeRestart(request: RestartRequest) RestartSummary {
    if (!request.drvdata_ready) {
        return .{
            .anchor = anchor_path,
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
            .keeps_live_mmio_execution_out_of_scope = request.keeps_live_mmio_execution_out_of_scope,
            .blocked_on_live_mmio = false,
            .state = .blocked_missing_drvdata,
        };
    }

    if (!request.timeout_image_ready) {
        return .{
            .anchor = anchor_path,
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
            .keeps_live_mmio_execution_out_of_scope = request.keeps_live_mmio_execution_out_of_scope,
            .blocked_on_live_mmio = false,
            .state = .blocked_missing_timeout_image,
        };
    }

    return .{
        .anchor = anchor_path,
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
        .keeps_live_mmio_execution_out_of_scope = request.keeps_live_mmio_execution_out_of_scope,
        .blocked_on_live_mmio = true,
        .state = .restart_ready,
    };
}

test "phase11 dw_wdt restart summary keeps missing drvdata explicit" {
    const summary = summarizeRestart(.{
        .drvdata_ready = false,
        .timeout_image_ready = true,
        .restart_priority_registered = true,
        .reset_pulse_available = true,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqualStrings("dw_wdt_restart", summary.restart_call);
    try std.testing.expect(!summary.restart_requested);
    try std.testing.expect(!summary.writes_timeout_range);
    try std.testing.expect(!summary.writes_control);
    try std.testing.expect(summary.restart_priority_registered);
    try std.testing.expect(summary.expects_reset_pulse);
    try std.testing.expect(summary.keeps_missing_drvdata_explicit);
    try std.testing.expect(!summary.keeps_missing_timeout_image_explicit);
    try std.testing.expect(summary.keeps_live_mmio_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
    try std.testing.expectEqual(RestartState.blocked_missing_drvdata, summary.state);
}

test "phase11 dw_wdt restart summary keeps missing timeout image explicit" {
    const summary = summarizeRestart(.{
        .drvdata_ready = true,
        .timeout_image_ready = false,
        .restart_priority_registered = false,
        .reset_pulse_available = true,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expect(!summary.restart_requested);
    try std.testing.expect(!summary.writes_timeout_range);
    try std.testing.expect(!summary.writes_control);
    try std.testing.expect(!summary.restart_priority_registered);
    try std.testing.expect(summary.expects_reset_pulse);
    try std.testing.expect(!summary.keeps_missing_drvdata_explicit);
    try std.testing.expect(summary.keeps_missing_timeout_image_explicit);
    try std.testing.expect(summary.keeps_live_mmio_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
    try std.testing.expectEqual(RestartState.blocked_missing_timeout_image, summary.state);
}

test "phase11 dw_wdt restart summary keeps restart register writes explicit" {
    const summary = summarizeRestart(.{
        .drvdata_ready = true,
        .timeout_image_ready = true,
        .restart_priority_registered = true,
        .reset_pulse_available = false,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqualStrings("WDOG_TIMEOUT_RANGE_REG_OFFSET", summary.timeout_range_anchor);
    try std.testing.expectEqualStrings("WDOG_CONTROL_REG_OFFSET", summary.control_anchor);
    try std.testing.expectEqualStrings(
        "watchdog_set_restart_priority",
        summary.restart_priority_call,
    );
    try std.testing.expect(summary.restart_requested);
    try std.testing.expect(summary.writes_timeout_range);
    try std.testing.expect(summary.writes_control);
    try std.testing.expect(summary.restart_priority_registered);
    try std.testing.expect(!summary.expects_reset_pulse);
    try std.testing.expect(!summary.keeps_missing_drvdata_explicit);
    try std.testing.expect(!summary.keeps_missing_timeout_image_explicit);
    try std.testing.expect(summary.keeps_live_mmio_execution_out_of_scope);
    try std.testing.expect(summary.blocked_on_live_mmio);
    try std.testing.expectEqual(RestartState.restart_ready, summary.state);
}

test "phase11 dw_wdt restart summary preserves explicit in-scope replay overrides" {
    const summary = summarizeRestart(.{
        .drvdata_ready = true,
        .timeout_image_ready = true,
        .restart_priority_registered = false,
        .reset_pulse_available = true,
        .keeps_live_mmio_execution_out_of_scope = false,
    });

    try std.testing.expect(summary.restart_requested);
    try std.testing.expect(summary.writes_timeout_range);
    try std.testing.expect(summary.writes_control);
    try std.testing.expect(!summary.restart_priority_registered);
    try std.testing.expect(summary.expects_reset_pulse);
    try std.testing.expect(!summary.keeps_live_mmio_execution_out_of_scope);
    try std.testing.expect(summary.blocked_on_live_mmio);
    try std.testing.expectEqual(RestartState.restart_ready, summary.state);
}
