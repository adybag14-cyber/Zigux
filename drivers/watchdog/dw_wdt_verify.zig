const std = @import("std");

const dw_wdt_pm = @import("dw_wdt_pm.zig");
const dw_wdt_pm_scaffold = @import("dw_wdt_pm_scaffold.zig");
const dw_wdt_restart = @import("dw_wdt_restart.zig");

test "dw_wdt verify keeps restart blockers and register-write readiness aligned" {
    const blocked_drvdata = dw_wdt_restart.summarizeRestart(.{
        .drvdata_ready = false,
        .timeout_image_ready = true,
        .restart_priority_registered = true,
        .reset_pulse_available = true,
    });
    const blocked_timeout = dw_wdt_restart.summarizeRestart(.{
        .drvdata_ready = true,
        .timeout_image_ready = false,
        .restart_priority_registered = false,
        .reset_pulse_available = true,
    });
    const ready = dw_wdt_restart.summarizeRestart(.{
        .drvdata_ready = true,
        .timeout_image_ready = true,
        .restart_priority_registered = true,
        .reset_pulse_available = false,
    });

    try std.testing.expectEqualStrings(dw_wdt_restart.anchor_path, blocked_drvdata.anchor);
    try std.testing.expectEqual(dw_wdt_restart.RestartState.blocked_missing_drvdata, blocked_drvdata.state);
    try std.testing.expect(blocked_drvdata.keeps_missing_drvdata_explicit);
    try std.testing.expect(!blocked_drvdata.keeps_missing_timeout_image_explicit);
    try std.testing.expect(!blocked_drvdata.restart_requested);

    try std.testing.expectEqual(dw_wdt_restart.RestartState.blocked_missing_timeout_image, blocked_timeout.state);
    try std.testing.expect(!blocked_timeout.keeps_missing_drvdata_explicit);
    try std.testing.expect(blocked_timeout.keeps_missing_timeout_image_explicit);
    try std.testing.expect(!blocked_timeout.restart_requested);

    try std.testing.expectEqual(dw_wdt_restart.RestartState.restart_ready, ready.state);
    try std.testing.expect(ready.restart_requested);
    try std.testing.expect(ready.writes_timeout_range);
    try std.testing.expect(ready.writes_control);
    try std.testing.expect(ready.restart_priority_registered);
    try std.testing.expect(!ready.expects_reset_pulse);
    try std.testing.expect(ready.blocked_on_live_mmio);
}

test "dw_wdt verify keeps PM helper ordering and blocker branches explicit" {
    const suspend_summary = dw_wdt_pm.summarizePmSuspend(.{
        .drvdata_published = true,
        .hardware_running = true,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = false,
    });
    const imported_resume = dw_wdt_pm.summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = false,
        .timeout_programmed = false,
        .imported_running = true,
        .reset_control_available = false,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = false,
    });
    const timeout_blocked_resume = dw_wdt_pm.summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = true,
        .timeout_programmed = false,
        .imported_running = false,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
    });
    const shutdown = dw_wdt_pm.summarizePmShutdown(.{
        .drvdata_published = true,
        .hardware_running = true,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
        .pretimeout_irq_present = true,
    });

    try std.testing.expectEqualStrings(dw_wdt_pm.anchor_path, suspend_summary.anchor);
    try std.testing.expectEqual(dw_wdt_pm.PmSuspendState.running_suspend_requires_stop, suspend_summary.state);
    try std.testing.expect(suspend_summary.stop_requested);
    try std.testing.expect(suspend_summary.reset_assert_ready);
    try std.testing.expect(suspend_summary.unregister_stop_on_reboot_requested);
    try std.testing.expect(!suspend_summary.clear_restart_priority_requested);
    try std.testing.expect(suspend_summary.blocked_on_live_mmio);

    try std.testing.expectEqual(
        dw_wdt_pm.PmResumeState.import_running_state_then_restore_hooks,
        imported_resume.state,
    );
    try std.testing.expect(imported_resume.imported_running_state);
    try std.testing.expect(!imported_resume.timeout_reprogram_requested);
    try std.testing.expect(imported_resume.restore_stop_on_reboot_requested);
    try std.testing.expect(!imported_resume.restore_restart_priority_requested);
    try std.testing.expect(!imported_resume.blocked_on_live_mmio);

    try std.testing.expectEqual(
        dw_wdt_pm.PmResumeState.blocked_live_mmio_timeout_reprogram,
        timeout_blocked_resume.state,
    );
    try std.testing.expect(timeout_blocked_resume.reset_release_ready);
    try std.testing.expect(timeout_blocked_resume.timeout_reprogram_requested);
    try std.testing.expect(!timeout_blocked_resume.restore_stop_on_reboot_requested);
    try std.testing.expect(!timeout_blocked_resume.restore_restart_priority_requested);
    try std.testing.expect(timeout_blocked_resume.blocked_on_live_mmio);

    try std.testing.expectEqual(dw_wdt_pm.PmShutdownState.running_shutdown_requires_stop, shutdown.state);
    try std.testing.expect(shutdown.stop_requested);
    try std.testing.expect(shutdown.reset_assert_ready);
    try std.testing.expect(shutdown.unregister_stop_on_reboot_requested);
    try std.testing.expect(shutdown.clear_restart_priority_requested);
    try std.testing.expect(shutdown.pretimeout_mask_requested);
    try std.testing.expect(shutdown.blocked_on_live_mmio);
}

test "dw_wdt verify keeps PM scaffold dispositions aligned with the stronger helper packet" {
    const idle_request = dw_wdt_pm_scaffold.PmTransitionRequest{
        .watchdog_running = false,
        .nowayout = true,
        .reset_control_available = false,
        .state_snapshot_available = false,
        .mmio_window_available = false,
        .pretimeout_irq_present = true,
    };
    const running_request = dw_wdt_pm_scaffold.PmTransitionRequest{
        .watchdog_running = true,
        .nowayout = false,
        .reset_control_available = true,
        .state_snapshot_available = true,
        .mmio_window_available = true,
        .pretimeout_irq_present = true,
    };
    const keep_running_request = dw_wdt_pm_scaffold.PmTransitionRequest{
        .watchdog_running = true,
        .nowayout = true,
        .reset_control_available = false,
        .state_snapshot_available = false,
        .mmio_window_available = true,
        .pretimeout_irq_present = false,
    };

    const idle_suspend = dw_wdt_pm_scaffold.suspendSummary(idle_request);
    const idle_resume = dw_wdt_pm_scaffold.resumeSummary(idle_request);
    try std.testing.expectEqual(dw_wdt_pm_scaffold.SuspendDisposition.idle_noop, idle_suspend.disposition);
    try std.testing.expect(idle_suspend.enters_low_power_ready_state);
    try std.testing.expectEqual(dw_wdt_pm_scaffold.ResumeDisposition.idle_noop, idle_resume.disposition);
    try std.testing.expect(!idle_resume.returns_watchdog_to_running_state);

    const running_suspend = dw_wdt_pm_scaffold.suspendSummary(running_request);
    const running_resume = dw_wdt_pm_scaffold.resumeSummary(running_request);
    try std.testing.expectEqual(
        dw_wdt_pm_scaffold.SuspendDisposition.quiesce_before_suspend,
        running_suspend.disposition,
    );
    try std.testing.expect(running_suspend.stop_requested);
    try std.testing.expect(running_suspend.register_snapshot_requested);
    try std.testing.expectEqual(
        dw_wdt_pm_scaffold.ResumeDisposition.restore_then_restart,
        running_resume.disposition,
    );
    try std.testing.expect(running_resume.register_restore_requested);
    try std.testing.expect(running_resume.restart_requested);
    try std.testing.expect(running_resume.pretimeout_restore_requested);

    const keep_running_suspend = dw_wdt_pm_scaffold.suspendSummary(keep_running_request);
    const keep_running_resume = dw_wdt_pm_scaffold.resumeSummary(keep_running_request);
    try std.testing.expectEqual(
        dw_wdt_pm_scaffold.SuspendDisposition.keep_running_across_suspend,
        keep_running_suspend.disposition,
    );
    try std.testing.expect(keep_running_suspend.keeps_hardware_running);
    try std.testing.expectEqual(
        dw_wdt_pm_scaffold.ResumeDisposition.keep_running_without_restore,
        keep_running_resume.disposition,
    );
    try std.testing.expect(keep_running_resume.preserves_running_hardware_without_restore);
    try std.testing.expect(keep_running_resume.returns_watchdog_to_running_state);
}
