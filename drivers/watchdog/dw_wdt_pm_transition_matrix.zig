const std = @import("std");

const dw_wdt_pm = @import("dw_wdt_pm.zig");
const dw_wdt_pm_scaffold = @import("dw_wdt_pm_scaffold.zig");

test "phase11 dw_wdt suspend and scaffold matrices keep bounded PM branches explicit" {
    const helper_cases = [_]struct {
        name: []const u8,
        request: dw_wdt_pm.PmSuspendRequest,
        expected_state: dw_wdt_pm.PmSuspendState,
        expect_stop: bool,
        expect_reset_ready: bool,
        expect_unregister_stop: bool,
        expect_clear_restart: bool,
        expect_mmio_blocker: bool,
    }{
        .{
            .name = "missing-drvdata",
            .request = .{
                .drvdata_published = false,
                .hardware_running = true,
                .reset_control_available = true,
                .stop_on_reboot_registered = true,
                .restart_priority_registered = true,
            },
            .expected_state = .blocked_missing_drvdata,
            .expect_stop = false,
            .expect_reset_ready = false,
            .expect_unregister_stop = false,
            .expect_clear_restart = false,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "idle",
            .request = .{
                .drvdata_published = true,
                .hardware_running = false,
                .reset_control_available = true,
                .stop_on_reboot_registered = false,
                .restart_priority_registered = false,
            },
            .expected_state = .idle_suspend_ready,
            .expect_stop = false,
            .expect_reset_ready = true,
            .expect_unregister_stop = false,
            .expect_clear_restart = false,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "running",
            .request = .{
                .drvdata_published = true,
                .hardware_running = true,
                .reset_control_available = true,
                .stop_on_reboot_registered = true,
                .restart_priority_registered = true,
            },
            .expected_state = .running_suspend_requires_stop,
            .expect_stop = true,
            .expect_reset_ready = true,
            .expect_unregister_stop = true,
            .expect_clear_restart = true,
            .expect_mmio_blocker = true,
        },
    };

    inline for (helper_cases) |case| {
        const summary = dw_wdt_pm.summarizePmSuspend(case.request);
        try std.testing.expectEqualStrings(dw_wdt_pm.anchor_path, summary.anchor);
        try std.testing.expectEqual(case.expected_state, summary.state);
        try std.testing.expectEqual(case.expect_stop, summary.stop_requested);
        try std.testing.expectEqual(case.expect_reset_ready, summary.reset_assert_ready);
        try std.testing.expectEqual(
            case.expect_unregister_stop,
            summary.unregister_stop_on_reboot_requested,
        );
        try std.testing.expectEqual(
            case.expect_clear_restart,
            summary.clear_restart_priority_requested,
        );
        try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
        try std.testing.expectEqual(case.expect_mmio_blocker, summary.blocked_on_live_mmio);
    }

    const scaffold_cases = [_]struct {
        name: []const u8,
        request: dw_wdt_pm_scaffold.PmTransitionRequest,
        expected_disposition: dw_wdt_pm_scaffold.SuspendDisposition,
        expect_stop: bool,
        expect_snapshot: bool,
        expect_keep_running: bool,
        expect_mmio_blocker: bool,
    }{
        .{
            .name = "idle",
            .request = .{
                .watchdog_running = false,
                .nowayout = true,
                .reset_control_available = false,
                .state_snapshot_available = false,
                .mmio_window_available = false,
                .pretimeout_irq_present = true,
            },
            .expected_disposition = .idle_noop,
            .expect_stop = false,
            .expect_snapshot = false,
            .expect_keep_running = false,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "quiesce",
            .request = .{
                .watchdog_running = true,
                .nowayout = false,
                .reset_control_available = true,
                .state_snapshot_available = true,
                .mmio_window_available = true,
                .pretimeout_irq_present = true,
            },
            .expected_disposition = .quiesce_before_suspend,
            .expect_stop = true,
            .expect_snapshot = true,
            .expect_keep_running = false,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "keep-running",
            .request = .{
                .watchdog_running = true,
                .nowayout = true,
                .reset_control_available = false,
                .state_snapshot_available = false,
                .mmio_window_available = false,
                .pretimeout_irq_present = false,
            },
            .expected_disposition = .keep_running_across_suspend,
            .expect_stop = false,
            .expect_snapshot = false,
            .expect_keep_running = true,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "blocked-live-mmio",
            .request = .{
                .watchdog_running = true,
                .nowayout = false,
                .reset_control_available = true,
                .state_snapshot_available = false,
                .mmio_window_available = false,
                .pretimeout_irq_present = true,
            },
            .expected_disposition = .blocked_on_live_mmio,
            .expect_stop = false,
            .expect_snapshot = false,
            .expect_keep_running = false,
            .expect_mmio_blocker = true,
        },
    };

    inline for (scaffold_cases) |case| {
        const summary = dw_wdt_pm_scaffold.suspendSummary(case.request);
        try std.testing.expectEqualStrings(dw_wdt_pm_scaffold.anchor_path, summary.anchor);
        try std.testing.expectEqual(case.expected_disposition, summary.disposition);
        try std.testing.expect(summary.suspend_requested);
        try std.testing.expectEqual(case.expect_stop, summary.stop_requested);
        try std.testing.expectEqual(case.expect_snapshot, summary.register_snapshot_requested);
        try std.testing.expectEqual(case.expect_keep_running, summary.keeps_hardware_running);
        try std.testing.expectEqual(case.expect_mmio_blocker, summary.blocked_on_live_mmio);
    }
}

test "phase11 dw_wdt resume and shutdown matrices keep timeout and hook ordering reviewable" {
    const resume_cases = [_]struct {
        name: []const u8,
        request: dw_wdt_pm.PmResumeRequest,
        expected_state: dw_wdt_pm.PmResumeState,
        expect_timeout_reprogram: bool,
        expect_imported_running: bool,
        expect_restore_stop: bool,
        expect_restore_restart: bool,
        expect_restore_pretimeout: bool,
        expect_mmio_blocker: bool,
    }{
        .{
            .name = "missing-drvdata",
            .request = .{
                .drvdata_published = false,
                .hardware_running = true,
                .timeout_programmed = false,
                .imported_running = false,
                .reset_control_available = true,
                .stop_on_reboot_registered = true,
                .restart_priority_registered = true,
            },
            .expected_state = .blocked_missing_drvdata,
            .expect_timeout_reprogram = false,
            .expect_imported_running = false,
            .expect_restore_stop = false,
            .expect_restore_restart = false,
            .expect_restore_pretimeout = false,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "imported-running",
            .request = .{
                .drvdata_published = true,
                .hardware_running = true,
                .timeout_programmed = false,
                .imported_running = true,
                .reset_control_available = true,
                .stop_on_reboot_registered = true,
                .restart_priority_registered = false,
                .pretimeout_irq_present = true,
            },
            .expected_state = .import_running_state_then_restore_hooks,
            .expect_timeout_reprogram = false,
            .expect_imported_running = true,
            .expect_restore_stop = true,
            .expect_restore_restart = false,
            .expect_restore_pretimeout = true,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "idle-restore",
            .request = .{
                .drvdata_published = true,
                .hardware_running = false,
                .timeout_programmed = false,
                .imported_running = false,
                .reset_control_available = false,
                .stop_on_reboot_registered = true,
                .restart_priority_registered = true,
            },
            .expected_state = .restore_idle_hooks,
            .expect_timeout_reprogram = false,
            .expect_imported_running = false,
            .expect_restore_stop = true,
            .expect_restore_restart = true,
            .expect_restore_pretimeout = false,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "timeout-blocked",
            .request = .{
                .drvdata_published = true,
                .hardware_running = true,
                .timeout_programmed = false,
                .imported_running = false,
                .reset_control_available = true,
                .stop_on_reboot_registered = true,
                .restart_priority_registered = true,
                .pretimeout_irq_present = true,
            },
            .expected_state = .blocked_live_mmio_timeout_reprogram,
            .expect_timeout_reprogram = true,
            .expect_imported_running = false,
            .expect_restore_stop = false,
            .expect_restore_restart = false,
            .expect_restore_pretimeout = false,
            .expect_mmio_blocker = true,
        },
        .{
            .name = "ready-to-restore",
            .request = .{
                .drvdata_published = true,
                .hardware_running = true,
                .timeout_programmed = true,
                .imported_running = false,
                .reset_control_available = false,
                .stop_on_reboot_registered = true,
                .restart_priority_registered = false,
                .pretimeout_irq_present = true,
            },
            .expected_state = .restore_idle_hooks,
            .expect_timeout_reprogram = false,
            .expect_imported_running = false,
            .expect_restore_stop = true,
            .expect_restore_restart = false,
            .expect_restore_pretimeout = true,
            .expect_mmio_blocker = false,
        },
    };

    inline for (resume_cases) |case| {
        const summary = dw_wdt_pm.summarizePmResume(case.request);
        try std.testing.expectEqualStrings(dw_wdt_pm.anchor_path, summary.anchor);
        try std.testing.expectEqual(case.expected_state, summary.state);
        try std.testing.expectEqual(case.expect_timeout_reprogram, summary.timeout_reprogram_requested);
        try std.testing.expectEqual(case.expect_imported_running, summary.imported_running_state);
        try std.testing.expectEqual(case.expect_restore_stop, summary.restore_stop_on_reboot_requested);
        try std.testing.expectEqual(case.expect_restore_restart, summary.restore_restart_priority_requested);
        try std.testing.expectEqual(case.expect_restore_pretimeout, summary.pretimeout_restore_requested);
        try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
        try std.testing.expectEqual(case.expect_mmio_blocker, summary.blocked_on_live_mmio);
    }

    const scaffold_resume_cases = [_]struct {
        name: []const u8,
        request: dw_wdt_pm_scaffold.PmTransitionRequest,
        expected_disposition: dw_wdt_pm_scaffold.ResumeDisposition,
        expect_restore: bool,
        expect_restart: bool,
        expect_pretimeout_restore: bool,
        expect_keep_running: bool,
        expect_mmio_blocker: bool,
    }{
        .{
            .name = "idle",
            .request = .{
                .watchdog_running = false,
                .nowayout = true,
                .reset_control_available = false,
                .state_snapshot_available = false,
                .mmio_window_available = false,
                .pretimeout_irq_present = true,
            },
            .expected_disposition = .idle_noop,
            .expect_restore = false,
            .expect_restart = false,
            .expect_pretimeout_restore = false,
            .expect_keep_running = false,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "restore",
            .request = .{
                .watchdog_running = true,
                .nowayout = false,
                .reset_control_available = true,
                .state_snapshot_available = true,
                .mmio_window_available = true,
                .pretimeout_irq_present = true,
            },
            .expected_disposition = .restore_then_restart,
            .expect_restore = true,
            .expect_restart = true,
            .expect_pretimeout_restore = true,
            .expect_keep_running = false,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "keep-running",
            .request = .{
                .watchdog_running = true,
                .nowayout = true,
                .reset_control_available = false,
                .state_snapshot_available = false,
                .mmio_window_available = false,
                .pretimeout_irq_present = false,
            },
            .expected_disposition = .keep_running_without_restore,
            .expect_restore = false,
            .expect_restart = false,
            .expect_pretimeout_restore = false,
            .expect_keep_running = true,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "blocked-live-mmio",
            .request = .{
                .watchdog_running = true,
                .nowayout = false,
                .reset_control_available = true,
                .state_snapshot_available = false,
                .mmio_window_available = false,
                .pretimeout_irq_present = true,
            },
            .expected_disposition = .blocked_on_live_mmio,
            .expect_restore = false,
            .expect_restart = false,
            .expect_pretimeout_restore = false,
            .expect_keep_running = false,
            .expect_mmio_blocker = true,
        },
    };

    inline for (scaffold_resume_cases) |case| {
        const summary = dw_wdt_pm_scaffold.resumeSummary(case.request);
        try std.testing.expectEqualStrings(dw_wdt_pm_scaffold.anchor_path, summary.anchor);
        try std.testing.expectEqual(case.expected_disposition, summary.disposition);
        try std.testing.expect(summary.resume_requested);
        try std.testing.expectEqual(case.expect_restore, summary.register_restore_requested);
        try std.testing.expectEqual(case.expect_restart, summary.restart_requested);
        try std.testing.expectEqual(case.expect_pretimeout_restore, summary.pretimeout_restore_requested);
        try std.testing.expectEqual(case.expect_keep_running, summary.preserves_running_hardware_without_restore);
        try std.testing.expectEqual(case.expect_mmio_blocker, summary.blocked_on_live_mmio);
    }

    const shutdown_cases = [_]struct {
        name: []const u8,
        request: dw_wdt_pm.PmShutdownRequest,
        expected_state: dw_wdt_pm.PmShutdownState,
        expect_stop: bool,
        expect_reset_ready: bool,
        expect_unregister_stop: bool,
        expect_clear_restart: bool,
        expect_pretimeout_mask: bool,
        expect_mmio_blocker: bool,
    }{
        .{
            .name = "missing-drvdata",
            .request = .{
                .drvdata_published = false,
                .hardware_running = true,
                .reset_control_available = true,
                .stop_on_reboot_registered = true,
                .restart_priority_registered = true,
                .pretimeout_irq_present = true,
            },
            .expected_state = .blocked_missing_drvdata,
            .expect_stop = false,
            .expect_reset_ready = false,
            .expect_unregister_stop = false,
            .expect_clear_restart = false,
            .expect_pretimeout_mask = false,
            .expect_mmio_blocker = false,
        },
        .{
            .name = "running-with-pretimeout",
            .request = .{
                .drvdata_published = true,
                .hardware_running = true,
                .reset_control_available = false,
                .stop_on_reboot_registered = true,
                .restart_priority_registered = false,
                .pretimeout_irq_present = true,
            },
            .expected_state = .running_shutdown_requires_stop,
            .expect_stop = true,
            .expect_reset_ready = false,
            .expect_unregister_stop = true,
            .expect_clear_restart = false,
            .expect_pretimeout_mask = true,
            .expect_mmio_blocker = true,
        },
        .{
            .name = "idle-unregister-only",
            .request = .{
                .drvdata_published = true,
                .hardware_running = false,
                .reset_control_available = true,
                .stop_on_reboot_registered = true,
                .restart_priority_registered = true,
                .pretimeout_irq_present = true,
            },
            .expected_state = .idle_unregister_only,
            .expect_stop = false,
            .expect_reset_ready = false,
            .expect_unregister_stop = true,
            .expect_clear_restart = true,
            .expect_pretimeout_mask = false,
            .expect_mmio_blocker = false,
        },
    };

    inline for (shutdown_cases) |case| {
        const summary = dw_wdt_pm.summarizePmShutdown(case.request);
        try std.testing.expectEqualStrings(dw_wdt_pm.anchor_path, summary.anchor);
        try std.testing.expectEqual(case.expected_state, summary.state);
        try std.testing.expectEqual(case.expect_stop, summary.stop_requested);
        try std.testing.expectEqual(case.expect_reset_ready, summary.reset_assert_ready);
        try std.testing.expectEqual(
            case.expect_unregister_stop,
            summary.unregister_stop_on_reboot_requested,
        );
        try std.testing.expectEqual(
            case.expect_clear_restart,
            summary.clear_restart_priority_requested,
        );
        try std.testing.expectEqual(case.expect_pretimeout_mask, summary.pretimeout_mask_requested);
        try std.testing.expect(summary.keeps_live_pm_execution_out_of_scope);
        try std.testing.expectEqual(case.expect_mmio_blocker, summary.blocked_on_live_mmio);
    }
}
