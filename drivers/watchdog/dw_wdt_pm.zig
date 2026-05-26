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
    hardware_running: bool,
    timeout_programmed: bool,
    imported_running: bool,
    reset_control_available: bool,
    stop_on_reboot_registered: bool,
    restart_priority_registered: bool,
    pretimeout_irq_present: bool = false,
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
    pretimeout_restore_requested: bool,
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
            .pretimeout_restore_requested = false,
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
            .pretimeout_restore_requested = request.pretimeout_irq_present,
            .keeps_live_pm_execution_out_of_scope = request.keeps_live_pm_execution_out_of_scope,
            .blocked_on_live_mmio = false,
        };
    }

    if (!request.hardware_running) {
        return .{
            .anchor = anchor_path,
            .state = .restore_idle_hooks,
            .reset_release_ready = false,
            .timeout_reprogram_requested = false,
            .imported_running_state = false,
            .restore_stop_on_reboot_requested = request.stop_on_reboot_registered,
            .restore_restart_priority_requested = request.restart_priority_registered,
            .pretimeout_restore_requested = false,
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
            .pretimeout_restore_requested = false,
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
        .pretimeout_restore_requested = request.pretimeout_irq_present,
        .keeps_live_pm_execution_out_of_scope = request.keeps_live_pm_execution_out_of_scope,
        .blocked_on_live_mmio = false,
    };
}

pub const PmShutdownState = enum {
    blocked_missing_drvdata,
    idle_unregister_only,
    running_shutdown_requires_stop,
};

pub const PmShutdownRequest = struct {
    drvdata_published: bool,
    hardware_running: bool,
    reset_control_available: bool,
    stop_on_reboot_registered: bool,
    restart_priority_registered: bool,
    pretimeout_irq_present: bool = false,
    keeps_live_pm_execution_out_of_scope: bool = true,
};

pub const PmShutdownSummary = struct {
    anchor: []const u8,
    state: PmShutdownState,
    stop_requested: bool,
    reset_assert_ready: bool,
    unregister_stop_on_reboot_requested: bool,
    clear_restart_priority_requested: bool,
    pretimeout_mask_requested: bool,
    keeps_live_pm_execution_out_of_scope: bool,
    blocked_on_live_mmio: bool,
};

pub fn summarizePmShutdown(request: PmShutdownRequest) PmShutdownSummary {
    if (!request.drvdata_published) {
        return .{
            .anchor = anchor_path,
            .state = .blocked_missing_drvdata,
            .stop_requested = false,
            .reset_assert_ready = false,
            .unregister_stop_on_reboot_requested = false,
            .clear_restart_priority_requested = false,
            .pretimeout_mask_requested = false,
            .keeps_live_pm_execution_out_of_scope = request.keeps_live_pm_execution_out_of_scope,
            .blocked_on_live_mmio = false,
        };
    }

    const stop_requested = request.hardware_running;
    return .{
        .anchor = anchor_path,
        .state = if (request.hardware_running)
            .running_shutdown_requires_stop
        else
            .idle_unregister_only,
        .stop_requested = stop_requested,
        .reset_assert_ready = stop_requested and request.reset_control_available,
        .unregister_stop_on_reboot_requested = request.stop_on_reboot_registered,
        .clear_restart_priority_requested = request.restart_priority_registered,
        .pretimeout_mask_requested = stop_requested and request.pretimeout_irq_present,
        .keeps_live_pm_execution_out_of_scope = request.keeps_live_pm_execution_out_of_scope,
        .blocked_on_live_mmio = stop_requested,
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

test "phase11 dw_wdt pm suspend keeps idle path explicit without teardown hooks" {
    const summary = summarizePmSuspend(.{
        .drvdata_published = true,
        .hardware_running = false,
        .reset_control_available = true,
        .stop_on_reboot_registered = false,
        .restart_priority_registered = false,
    });

    try std.testing.expectEqual(PmSuspendState.idle_suspend_ready, summary.state);
    try std.testing.expect(!summary.stop_requested);
    try std.testing.expect(summary.reset_assert_ready);
    try std.testing.expect(!summary.unregister_stop_on_reboot_requested);
    try std.testing.expect(!summary.clear_restart_priority_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm suspend keeps missing hook teardown explicit during running stop" {
    const summary = summarizePmSuspend(.{
        .drvdata_published = true,
        .hardware_running = true,
        .reset_control_available = false,
        .stop_on_reboot_registered = false,
        .restart_priority_registered = false,
    });

    try std.testing.expectEqual(PmSuspendState.running_suspend_requires_stop, summary.state);
    try std.testing.expect(summary.stop_requested);
    try std.testing.expect(!summary.reset_assert_ready);
    try std.testing.expect(!summary.unregister_stop_on_reboot_requested);
    try std.testing.expect(!summary.clear_restart_priority_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm resume keeps imported-running handoff explicit" {
    const summary = summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = true,
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
    try std.testing.expect(!summary.pretimeout_restore_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm resume restores pretimeout hook after imported-running handoff" {
    const summary = summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = true,
        .timeout_programmed = false,
        .imported_running = true,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
        .pretimeout_irq_present = true,
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
    try std.testing.expect(summary.pretimeout_restore_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm resume keeps imported-running precedence explicit over idle restore" {
    const summary = summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = false,
        .timeout_programmed = true,
        .imported_running = true,
        .reset_control_available = false,
        .stop_on_reboot_registered = false,
        .restart_priority_registered = false,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqual(
        PmResumeState.import_running_state_then_restore_hooks,
        summary.state,
    );
    try std.testing.expect(!summary.reset_release_ready);
    try std.testing.expect(!summary.timeout_reprogram_requested);
    try std.testing.expect(summary.imported_running_state);
    try std.testing.expect(!summary.restore_stop_on_reboot_requested);
    try std.testing.expect(!summary.restore_restart_priority_requested);
    try std.testing.expect(!summary.pretimeout_restore_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm resume keeps idle restore path explicit" {
    const summary = summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = false,
        .timeout_programmed = false,
        .imported_running = false,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqual(PmResumeState.restore_idle_hooks, summary.state);
    try std.testing.expect(!summary.reset_release_ready);
    try std.testing.expect(!summary.timeout_reprogram_requested);
    try std.testing.expect(!summary.imported_running_state);
    try std.testing.expect(summary.restore_stop_on_reboot_requested);
    try std.testing.expect(summary.restore_restart_priority_requested);
    try std.testing.expect(!summary.pretimeout_restore_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore" {
    const blocked = summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = true,
        .timeout_programmed = false,
        .imported_running = false,
        .reset_control_available = false,
        .stop_on_reboot_registered = false,
        .restart_priority_registered = false,
        .keeps_live_pm_execution_out_of_scope = false,
    });
    const restored = summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = true,
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
    try std.testing.expect(!blocked.imported_running_state);
    try std.testing.expect(!blocked.restore_stop_on_reboot_requested);
    try std.testing.expect(!blocked.restore_restart_priority_requested);
    try std.testing.expect(!blocked.pretimeout_restore_requested);
    try std.testing.expect(!blocked.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(blocked.blocked_on_live_mmio);

    try std.testing.expectEqual(PmResumeState.restore_idle_hooks, restored.state);
    try std.testing.expect(!restored.reset_release_ready);
    try std.testing.expect(!restored.timeout_reprogram_requested);
    try std.testing.expect(!restored.imported_running_state);
    try std.testing.expect(restored.restore_stop_on_reboot_requested);
    try std.testing.expect(restored.restore_restart_priority_requested);
    try std.testing.expect(!restored.pretimeout_restore_requested);
    try std.testing.expect(restored.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!restored.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm resume keeps timeout reprogram blocker ahead of pretimeout restore" {
    const summary = summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = true,
        .timeout_programmed = false,
        .imported_running = false,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
        .pretimeout_irq_present = true,
    });

    try std.testing.expectEqual(
        PmResumeState.blocked_live_mmio_timeout_reprogram,
        summary.state,
    );
    try std.testing.expect(summary.reset_release_ready);
    try std.testing.expect(summary.timeout_reprogram_requested);
    try std.testing.expect(!summary.imported_running_state);
    try std.testing.expect(!summary.restore_stop_on_reboot_requested);
    try std.testing.expect(!summary.restore_restart_priority_requested);
    try std.testing.expect(!summary.pretimeout_restore_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm resume keeps running ready-to-restore path explicit when timeout is already programmed" {
    const summary = summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = true,
        .timeout_programmed = true,
        .imported_running = false,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = false,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqual(PmResumeState.restore_idle_hooks, summary.state);
    try std.testing.expect(summary.reset_release_ready);
    try std.testing.expect(!summary.timeout_reprogram_requested);
    try std.testing.expect(!summary.imported_running_state);
    try std.testing.expect(summary.restore_stop_on_reboot_requested);
    try std.testing.expect(!summary.restore_restart_priority_requested);
    try std.testing.expect(!summary.pretimeout_restore_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm resume restores pretimeout hook once timeout image is ready" {
    const summary = summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = true,
        .timeout_programmed = true,
        .imported_running = false,
        .reset_control_available = false,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = false,
        .pretimeout_irq_present = true,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqual(PmResumeState.restore_idle_hooks, summary.state);
    try std.testing.expect(!summary.reset_release_ready);
    try std.testing.expect(!summary.timeout_reprogram_requested);
    try std.testing.expect(!summary.imported_running_state);
    try std.testing.expect(summary.restore_stop_on_reboot_requested);
    try std.testing.expect(!summary.restore_restart_priority_requested);
    try std.testing.expect(summary.pretimeout_restore_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm resume keeps idle restore path free of fabricated pretimeout work" {
    const summary = summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = false,
        .timeout_programmed = true,
        .imported_running = false,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
        .pretimeout_irq_present = true,
    });

    try std.testing.expectEqual(PmResumeState.restore_idle_hooks, summary.state);
    try std.testing.expect(!summary.imported_running_state);
    try std.testing.expect(summary.restore_stop_on_reboot_requested);
    try std.testing.expect(summary.restore_restart_priority_requested);
    try std.testing.expect(!summary.pretimeout_restore_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm shutdown keeps missing drvdata explicit" {
    const summary = summarizePmShutdown(.{
        .drvdata_published = false,
        .hardware_running = true,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqual(PmShutdownState.blocked_missing_drvdata, summary.state);
    try std.testing.expect(!summary.stop_requested);
    try std.testing.expect(!summary.reset_assert_ready);
    try std.testing.expect(!summary.unregister_stop_on_reboot_requested);
    try std.testing.expect(!summary.clear_restart_priority_requested);
    try std.testing.expect(!summary.pretimeout_mask_requested);
    try std.testing.expect(!summary.blocked_on_live_mmio);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
}

test "phase11 dw_wdt pm shutdown keeps running teardown stop and hook removal explicit" {
    const summary = summarizePmShutdown(.{
        .drvdata_published = true,
        .hardware_running = true,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
    });

    try std.testing.expectEqual(PmShutdownState.running_shutdown_requires_stop, summary.state);
    try std.testing.expect(summary.stop_requested);
    try std.testing.expect(summary.reset_assert_ready);
    try std.testing.expect(summary.unregister_stop_on_reboot_requested);
    try std.testing.expect(summary.clear_restart_priority_requested);
    try std.testing.expect(!summary.pretimeout_mask_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit" {
    const summary = summarizePmShutdown(.{
        .drvdata_published = true,
        .hardware_running = true,
        .reset_control_available = false,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = false,
        .pretimeout_irq_present = true,
    });

    try std.testing.expectEqual(PmShutdownState.running_shutdown_requires_stop, summary.state);
    try std.testing.expect(summary.stop_requested);
    try std.testing.expect(!summary.reset_assert_ready);
    try std.testing.expect(summary.unregister_stop_on_reboot_requested);
    try std.testing.expect(!summary.clear_restart_priority_requested);
    try std.testing.expect(summary.pretimeout_mask_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm shutdown keeps idle hook teardown explicit without stop" {
    const summary = summarizePmShutdown(.{
        .drvdata_published = true,
        .hardware_running = false,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
        .pretimeout_irq_present = true,
    });

    try std.testing.expectEqual(PmShutdownState.idle_unregister_only, summary.state);
    try std.testing.expect(!summary.stop_requested);
    try std.testing.expect(!summary.reset_assert_ready);
    try std.testing.expect(summary.unregister_stop_on_reboot_requested);
    try std.testing.expect(summary.clear_restart_priority_requested);
    try std.testing.expect(!summary.pretimeout_mask_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt pm shutdown keeps idle no-hook teardown explicit" {
    const summary = summarizePmShutdown(.{
        .drvdata_published = true,
        .hardware_running = false,
        .reset_control_available = false,
        .stop_on_reboot_registered = false,
        .restart_priority_registered = false,
    });

    try std.testing.expectEqual(PmShutdownState.idle_unregister_only, summary.state);
    try std.testing.expect(!summary.stop_requested);
    try std.testing.expect(!summary.reset_assert_ready);
    try std.testing.expect(!summary.unregister_stop_on_reboot_requested);
    try std.testing.expect(!summary.clear_restart_priority_requested);
    try std.testing.expect(!summary.pretimeout_mask_requested);
    try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}
