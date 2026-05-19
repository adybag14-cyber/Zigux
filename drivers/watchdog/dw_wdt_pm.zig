const std = @import("std");

pub const anchor_path = "drivers/watchdog/dw_wdt.c";

pub const PmSuspendState = enum {
    blocked_missing_drvdata,
    idle_suspend_ready,
    running_suspend_requires_stop,
};

pub const PmSuspendRequest = struct {
    drvdata_published: bool,
    hardware_running: bool,
    reset_control_available: bool,
    stop_on_reboot_registered: bool,
    restart_priority_registered: bool,
    keeps_live_pm_execution_out_of_scope: bool = true,
};

pub const PmSuspendSummary = struct {
    anchor: []const u8,
    state: PmSuspendState,
    stop_requested: bool,
    reset_assert_ready: bool,
    unregister_stop_on_reboot_requested: bool,
    clear_restart_priority_requested: bool,
    keeps_live_pm_execution_out_of_scope: bool,
    blocked_on_live_mmio: bool,
};

pub fn summarizePmSuspend(request: PmSuspendRequest) PmSuspendSummary {
    if (!request.drvdata_published) {
        return .{
            .anchor = anchor_path,
            .state = .blocked_missing_drvdata,
            .stop_requested = false,
            .reset_assert_ready = false,
            .unregister_stop_on_reboot_requested = false,
            .clear_restart_priority_requested = false,
            .keeps_live_pm_execution_out_of_scope = request.keeps_live_pm_execution_out_of_scope,
            .blocked_on_live_mmio = false,
        };
    }

    const stop_requested = request.hardware_running;
    return .{
        .anchor = anchor_path,
        .state = if (request.hardware_running)
            .running_suspend_requires_stop
        else
            .idle_suspend_ready,
        .stop_requested = stop_requested,
        .reset_assert_ready = request.reset_control_available,
        .unregister_stop_on_reboot_requested = stop_requested and request.stop_on_reboot_registered,
        .clear_restart_priority_requested = stop_requested and request.restart_priority_registered,
        .keeps_live_pm_execution_out_of_scope = request.keeps_live_pm_execution_out_of_scope,
        .blocked_on_live_mmio = stop_requested,
    };
}

pub const PmResumeState = enum {
    blocked_missing_drvdata,
    blocked_live_mmio_timeout_reprogram,
    import_running_state_then_restore_hooks,
    restore_idle_hooks,
};

pub const PmResumeRequest = struct {
    drvdata_published: bool,
    timeout_programmed: bool,
    imported_running: bool,
    reset_control_available: bool,
    stop_on_reboot_registered: bool,
    restart_priority_registered: bool,
    keeps_live_pm_execution_out_of_scope: bool = true,
};

pub const PmResumeSummary = struct {
    anchor: []const u8,
    state: PmResumeState,
    reset_release_ready: bool,
    timeout_reprogram_requested: bool,
    imported_running_state: bool,
    restore_stop_on_reboot_requested: bool,
    restore_restart_priority_requested: bool,
    keeps_live_pm_execution_out_of_scope: bool,
    blocked_on_live_mmio: bool,
};

pub fn summarizePmResume(request: PmResumeRequest) PmResumeSummary {
    if (!request.drvdata_published) {
        return .{
            .anchor = anchor_path,
            .state = .blocked_missing_drvdata,
            .reset_release_ready = false,
            .timeout_reprogram_requested = false,
            .imported_running_state = false,
            .restore_stop_on_reboot_requested = false,
            .restore_restart_priority_requested = false,
            .keeps_live_pm_execution_out_of_scope = request.keeps_live_pm_execution_out_of_scope,
            .blocked_on_live_mmio = false,
        };
    }

    if (request.imported_running) {
        return .{
            .anchor = anchor_path,
            .state = .import_running_state_then_restore_hooks,
            .reset_release_ready = request.reset_control_available,
            .timeout_reprogram_requested = false,
            .imported_running_state = true,
            .restore_stop_on_reboot_requested = request.stop_on_reboot_registered,
            .restore_restart_priority_requested = request.restart_priority_registered,
            .keeps_live_pm_execution_out_of_scope = request.keeps_live_pm_execution_out_of_scope,
            .blocked_on_live_mmio = false,
        };
    }

    if (!request.timeout_programmed) {
        return .{
            .anchor = anchor_path,
            .state = .blocked_live_mmio_timeout_reprogram,
            .reset_release_ready = request.reset_control_available,
            .timeout_reprogram_requested = true,
            .imported_running_state = false,
            .restore_stop_on_reboot_requested = false,
            .restore_restart_priority_requested = false,
            .keeps_live_pm_execution_out_of_scope = request.keeps_live_pm_execution_out_of_scope,
            .blocked_on_live_mmio = true,
        };
    }

    return .{
        .anchor = anchor_path,
        .state = .restore_idle_hooks,
        .reset_release_ready = request.reset_control_available,
        .timeout_reprogram_requested = false,
        .imported_running_state = false,
        .restore_stop_on_reboot_requested = request.stop_on_reboot_registered,
        .restore_restart_priority_requested = request.restart_priority_registered,
        .keeps_live_pm_execution_out_of_scope = request.keeps_live_pm_execution_out_of_scope,
        .blocked_on_live_mmio = false,
    };
}

test "phase11 dw_wdt pm suspend keeps missing drvdata explicit" {
    const summary = summarizePmSuspend(.{
        .drvdata_published = false,
        .hardware_running = true,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqual(PmSuspendState.blocked_missing_drvdata, summary.state);
    try std.testing.expect(!summary.stop_requested);
    try std.testing.expect(!summary.reset_assert_ready);
    try std.testing.expect(!summary.unregister_stop_on_reboot_requested);
    try std.testing.expect(!summary.clear_restart_priority_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm suspend keeps running-hardware stop handoff explicit" {
    const summary = summarizePmSuspend(.{
        .drvdata_published = true,
        .hardware_running = true,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
    });

    try std.testing.expectEqual(PmSuspendState.running_suspend_requires_stop, summary.state);
    try std.testing.expect(summary.stop_requested);
    try std.testing.expect(summary.reset_assert_ready);
    try std.testing.expect(summary.unregister_stop_on_reboot_requested);
    try std.testing.expect(summary.clear_restart_priority_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm resume keeps imported-running handoff explicit" {
    const summary = summarizePmResume(.{
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = true,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqual(
        PmResumeState.import_running_state_then_restore_hooks,
        summary.state,
    );
    try std.testing.expect(summary.reset_release_ready);
    try std.testing.expect(!summary.timeout_reprogram_requested);
    try std.testing.expect(summary.imported_running_state);
    try std.testing.expect(summary.restore_stop_on_reboot_requested);
    try std.testing.expect(summary.restore_restart_priority_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore" {
    const blocked = summarizePmResume(.{
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = false,
        .reset_control_available = false,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
    });
    const restored = summarizePmResume(.{
        .drvdata_published = true,
        .timeout_programmed = true,
        .imported_running = false,
        .reset_control_available = false,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
    });

    try std.testing.expectEqual(
        PmResumeState.blocked_live_mmio_timeout_reprogram,
        blocked.state,
    );
    try std.testing.expect(!blocked.reset_release_ready);
    try std.testing.expect(blocked.timeout_reprogram_requested);
    try std.testing.expect(!blocked.restore_stop_on_reboot_requested);
    try std.testing.expect(!blocked.restore_restart_priority_requested);
    try std.testing.expect(blocked.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(blocked.blocked_on_live_mmio);

    try std.testing.expectEqual(PmResumeState.restore_idle_hooks, restored.state);
    try std.testing.expect(!restored.reset_release_ready);
    try std.testing.expect(!restored.timeout_reprogram_requested);
    try std.testing.expect(!restored.imported_running_state);
    try std.testing.expect(restored.restore_stop_on_reboot_requested);
    try std.testing.expect(restored.restore_restart_priority_requested);
    try std.testing.expect(restored.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!restored.blocked_on_live_mmio);
}
