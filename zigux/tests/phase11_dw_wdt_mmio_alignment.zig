const std = @import("std");

const dw_wdt_pm = @import("dw_wdt_pm");
const dw_wdt_pm_scaffold = @import("dw_wdt_pm_scaffold");

test "phase11 dw_wdt mmio alignment blocks fabricated suspend and resume execution when the window is absent" {
    const request = dw_wdt_pm_scaffold.PmTransitionRequest{
        .watchdog_running = true,
        .nowayout = false,
        .reset_control_available = true,
        .state_snapshot_available = true,
        .mmio_window_available = false,
        .pretimeout_irq_present = true,
    };

    const suspend_scaffold = dw_wdt_pm_scaffold.suspendSummary(request);
    const resume_scaffold = dw_wdt_pm_scaffold.resumeSummary(request);
    const suspend_helper = dw_wdt_pm.summarizePmSuspend(.{
        .drvdata_published = true,
        .hardware_running = true,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
    });
    const resume_helper = dw_wdt_pm.summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = true,
        .timeout_programmed = false,
        .imported_running = false,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
        .pretimeout_irq_present = true,
    });

    try std.testing.expectEqualStrings(dw_wdt_pm.anchor_path, suspend_scaffold.anchor);
    try std.testing.expectEqual(
        dw_wdt_pm_scaffold.SuspendDisposition.blocked_on_live_mmio,
        suspend_scaffold.disposition,
    );
    try std.testing.expect(!suspend_scaffold.stop_requested);
    try std.testing.expect(!suspend_scaffold.reset_assert_requested);
    try std.testing.expect(!suspend_scaffold.register_snapshot_requested);
    try std.testing.expect(suspend_scaffold.pretimeout_mask_requested);
    try std.testing.expect(suspend_scaffold.blocked_on_live_mmio);

    try std.testing.expectEqual(
        dw_wdt_pm_scaffold.ResumeDisposition.blocked_on_live_mmio,
        resume_scaffold.disposition,
    );
    try std.testing.expect(resume_scaffold.clock_enable_requested);
    try std.testing.expect(!resume_scaffold.register_restore_requested);
    try std.testing.expect(!resume_scaffold.restart_requested);
    try std.testing.expect(!resume_scaffold.pretimeout_restore_requested);
    try std.testing.expect(!resume_scaffold.returns_watchdog_to_running_state);
    try std.testing.expect(resume_scaffold.blocked_on_live_mmio);

    try std.testing.expectEqual(
        dw_wdt_pm.PmSuspendState.running_suspend_requires_stop,
        suspend_helper.state,
    );
    try std.testing.expect(suspend_helper.stop_requested);
    try std.testing.expect(suspend_helper.reset_assert_ready);
    try std.testing.expect(suspend_helper.unregister_stop_on_reboot_requested);
    try std.testing.expect(suspend_helper.clear_restart_priority_requested);
    try std.testing.expect(suspend_helper.blocked_on_live_mmio);

    try std.testing.expectEqual(
        dw_wdt_pm.PmResumeState.blocked_live_mmio_timeout_reprogram,
        resume_helper.state,
    );
    try std.testing.expect(resume_helper.reset_release_ready);
    try std.testing.expect(resume_helper.timeout_reprogram_requested);
    try std.testing.expect(!resume_helper.restore_stop_on_reboot_requested);
    try std.testing.expect(!resume_helper.restore_restart_priority_requested);
    try std.testing.expect(!resume_helper.pretimeout_restore_requested);
    try std.testing.expect(resume_helper.blocked_on_live_mmio);
}

test "phase11 dw_wdt mmio alignment keeps ready branches reviewable without pretending host-free execution already happened" {
    const request = dw_wdt_pm_scaffold.PmTransitionRequest{
        .watchdog_running = true,
        .nowayout = false,
        .reset_control_available = true,
        .state_snapshot_available = true,
        .mmio_window_available = true,
        .pretimeout_irq_present = true,
    };

    const suspend_scaffold = dw_wdt_pm_scaffold.suspendSummary(request);
    const resume_scaffold = dw_wdt_pm_scaffold.resumeSummary(request);
    const suspend_helper = dw_wdt_pm.summarizePmSuspend(.{
        .drvdata_published = true,
        .hardware_running = true,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
    });
    const resume_helper = dw_wdt_pm.summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = true,
        .timeout_programmed = true,
        .imported_running = false,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
        .pretimeout_irq_present = true,
    });

    try std.testing.expectEqualStrings(dw_wdt_pm.anchor_path, suspend_scaffold.anchor);
    try std.testing.expectEqual(
        dw_wdt_pm_scaffold.SuspendDisposition.quiesce_before_suspend,
        suspend_scaffold.disposition,
    );
    try std.testing.expect(suspend_scaffold.stop_requested);
    try std.testing.expect(suspend_scaffold.reset_assert_requested);
    try std.testing.expect(suspend_scaffold.register_snapshot_requested);
    try std.testing.expect(suspend_scaffold.pretimeout_mask_requested);
    try std.testing.expect(suspend_scaffold.enters_low_power_ready_state);
    try std.testing.expect(!suspend_scaffold.blocked_on_live_mmio);

    try std.testing.expectEqual(
        dw_wdt_pm_scaffold.ResumeDisposition.restore_then_restart,
        resume_scaffold.disposition,
    );
    try std.testing.expect(resume_scaffold.clock_enable_requested);
    try std.testing.expect(resume_scaffold.register_restore_requested);
    try std.testing.expect(resume_scaffold.restart_requested);
    try std.testing.expect(resume_scaffold.pretimeout_restore_requested);
    try std.testing.expect(resume_scaffold.returns_watchdog_to_running_state);
    try std.testing.expect(!resume_scaffold.blocked_on_live_mmio);

    try std.testing.expectEqual(
        dw_wdt_pm.PmSuspendState.running_suspend_requires_stop,
        suspend_helper.state,
    );
    try std.testing.expect(suspend_helper.stop_requested);
    try std.testing.expect(suspend_helper.reset_assert_ready);
    try std.testing.expect(suspend_helper.unregister_stop_on_reboot_requested);
    try std.testing.expect(suspend_helper.clear_restart_priority_requested);
    try std.testing.expect(suspend_helper.blocked_on_live_mmio);

    try std.testing.expectEqual(dw_wdt_pm.PmResumeState.restore_idle_hooks, resume_helper.state);
    try std.testing.expect(resume_helper.reset_release_ready);
    try std.testing.expect(!resume_helper.timeout_reprogram_requested);
    try std.testing.expect(!resume_helper.imported_running_state);
    try std.testing.expect(resume_helper.restore_stop_on_reboot_requested);
    try std.testing.expect(resume_helper.restore_restart_priority_requested);
    try std.testing.expect(resume_helper.pretimeout_restore_requested);
    try std.testing.expect(!resume_helper.blocked_on_live_mmio);
}
