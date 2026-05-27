const std = @import("std");

const dw_wdt = @import("dw_wdt");
const dw_wdt_pm = @import("dw_wdt_pm");

test "phase11 dw_wdt keeps live mmio timeout barriers aligned across probe and resume" {
    const handoff = dw_wdt.platformHandoffSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = false,
    });
    const scaffold = dw_wdt.platformRegistrationScaffoldSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = false,
    });
    const cleanup = dw_wdt.probeFailureCleanupSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = false,
        .failure_stage = .timeout_programming,
    });
    const resume_summary = dw_wdt_pm.summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = true,
        .timeout_programmed = false,
        .imported_running = false,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
        .pretimeout_irq_present = true,
    });

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", handoff.anchor);
    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.blocked_on_live_mmio, handoff.state);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.blocked_on_live_mmio, handoff.probe_timeout_origin);
    try std.testing.expect(handoff.timeout_programming_requested);
    try std.testing.expect(!handoff.registration_ready);
    try std.testing.expect(handoff.blocked_on_live_mmio);

    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.blocked_on_live_mmio, scaffold.state);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.blocked_on_live_mmio, scaffold.probe_timeout_origin);
    try std.testing.expect(!scaffold.registration_requested);
    try std.testing.expect(scaffold.blocked_on_live_mmio);

    try std.testing.expectEqual(dw_wdt.ProbeFailureStage.timeout_programming, cleanup.failure_stage);
    try std.testing.expect(cleanup.drvdata_cleanup_reviewable);
    try std.testing.expect(!cleanup.timeout_cleanup_reviewable);
    try std.testing.expect(cleanup.pretimeout_irq_release_reviewable);
    try std.testing.expect(cleanup.reset_assert_requested);
    try std.testing.expect(cleanup.timer_clock_disable_requested);
    try std.testing.expect(cleanup.apb_clock_disable_requested);
    try std.testing.expect(cleanup.blocked_on_live_mmio_cleanup);

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", resume_summary.anchor);
    try std.testing.expectEqual(dw_wdt_pm.PmResumeState.blocked_live_mmio_timeout_reprogram, resume_summary.state);
    try std.testing.expect(resume_summary.reset_release_ready);
    try std.testing.expect(resume_summary.timeout_reprogram_requested);
    try std.testing.expect(!resume_summary.imported_running_state);
    try std.testing.expect(!resume_summary.restore_stop_on_reboot_requested);
    try std.testing.expect(!resume_summary.restore_restart_priority_requested);
    try std.testing.expect(!resume_summary.pretimeout_restore_requested);
    try std.testing.expect(resume_summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt keeps imported-running handoff free of fabricated live mmio blockers" {
    const handoff = dw_wdt.platformHandoffSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = true,
        .has_pclk = false,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = true,
    });
    const scaffold = dw_wdt.platformRegistrationScaffoldSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = true,
        .has_pclk = false,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = true,
    });
    const order = dw_wdt.registrationOrderSummary(.{
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = true,
    });
    const resume_summary = dw_wdt_pm.summarizePmResume(.{
        .drvdata_published = true,
        .hardware_running = false,
        .timeout_programmed = false,
        .imported_running = true,
        .reset_control_available = true,
        .stop_on_reboot_registered = true,
        .restart_priority_registered = true,
        .pretimeout_irq_present = true,
    });

    try std.testing.expectEqual(
        dw_wdt.RegistrationScaffoldState.import_running_state_then_register,
        handoff.state,
    );
    try std.testing.expectEqual(
        dw_wdt.TimerClockPath.unnamed_shared_fallback,
        handoff.timer_clock_path,
    );
    try std.testing.expectEqual(
        dw_wdt.ProbeTimeoutOrigin.imported_running_counter,
        handoff.probe_timeout_origin,
    );
    try std.testing.expect(handoff.registration_ready);
    try std.testing.expect(!handoff.blocked_on_live_mmio);

    try std.testing.expectEqual(
        dw_wdt.RegistrationScaffoldState.import_running_state_then_register,
        scaffold.state,
    );
    try std.testing.expect(scaffold.registration_requested);
    try std.testing.expect(scaffold.reset_release_ready);
    try std.testing.expect(!scaffold.blocked_on_live_mmio);

    try std.testing.expectEqual(
        dw_wdt.RegistrationScaffoldState.import_running_state_then_register,
        order.state,
    );
    try std.testing.expect(order.publishes_drvdata_before_register);
    try std.testing.expect(order.imports_running_state_before_register);
    try std.testing.expect(!order.programs_timeout_before_register);
    try std.testing.expect(order.registration_requested);
    try std.testing.expect(!order.blocked_on_live_mmio);

    try std.testing.expectEqual(
        dw_wdt_pm.PmResumeState.import_running_state_then_restore_hooks,
        resume_summary.state,
    );
    try std.testing.expect(resume_summary.reset_release_ready);
    try std.testing.expect(!resume_summary.timeout_reprogram_requested);
    try std.testing.expect(resume_summary.imported_running_state);
    try std.testing.expect(resume_summary.restore_stop_on_reboot_requested);
    try std.testing.expect(resume_summary.restore_restart_priority_requested);
    try std.testing.expect(resume_summary.pretimeout_restore_requested);
    try std.testing.expect(!resume_summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt keeps remove-time live mmio stop boundaries explicit" {
    const stoppable = dw_wdt.removeTeardownSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = true,
        .imported_running = false,
        .nowayout = false,
        .restart_handler_registered = true,
    });
    const nowayout = dw_wdt.removeTeardownSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = false,
        .has_reset_control = false,
        .has_pretimeout_irq = false,
        .drvdata_published = true,
        .timeout_programmed = true,
        .imported_running = false,
        .nowayout = true,
        .restart_handler_registered = true,
    });

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", stoppable.anchor);
    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.ready_to_register, stoppable.state);
    try std.testing.expect(stoppable.watchdog_stop_requested);
    try std.testing.expect(stoppable.restart_handler_unregistered);
    try std.testing.expect(stoppable.pretimeout_irq_release_reviewable);
    try std.testing.expect(stoppable.reset_assert_requested);
    try std.testing.expect(stoppable.timer_clock_disable_requested);
    try std.testing.expect(stoppable.apb_clock_disable_requested);
    try std.testing.expect(stoppable.blocked_on_live_mmio_stop);
    try std.testing.expect(stoppable.blocked_on_live_remove_callback);

    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.ready_to_register, nowayout.state);
    try std.testing.expect(!nowayout.watchdog_stop_requested);
    try std.testing.expect(nowayout.restart_handler_unregistered);
    try std.testing.expect(!nowayout.pretimeout_irq_release_reviewable);
    try std.testing.expect(!nowayout.reset_assert_requested);
    try std.testing.expect(nowayout.timer_clock_disable_requested);
    try std.testing.expect(!nowayout.apb_clock_disable_requested);
    try std.testing.expect(nowayout.blocked_on_live_mmio_stop);
    try std.testing.expect(nowayout.blocked_on_live_remove_callback);
}
