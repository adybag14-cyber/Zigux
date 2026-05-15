const std = @import("std");

const testing = std.testing;
const dw_wdt = @import("dw_wdt.zig");

test "phase11 dw_wdt verify keeps registration-blocking failure paths explicit" {
    const missing_drvdata = dw_wdt.registrationOrderSummary(.{
        .drvdata_published = false,
        .timeout_programmed = true,
        .imported_running = false,
    });

    try testing.expectEqualStrings(dw_wdt.anchor_path, missing_drvdata.anchor);
    try testing.expectEqual(dw_wdt.RegistrationScaffoldState.blocked_missing_drvdata, missing_drvdata.state);
    try testing.expect(!missing_drvdata.publishes_drvdata_before_register);
    try testing.expect(!missing_drvdata.registration_requested);
    try testing.expect(missing_drvdata.blocked_on_live_platform_registration);
    try testing.expect(!missing_drvdata.blocked_on_live_mmio);

    const missing_timer_clock = dw_wdt.platformRegistrationScaffoldSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = true,
        .imported_running = false,
    });

    try testing.expectEqual(dw_wdt.RegistrationScaffoldState.blocked_missing_timer_clock, missing_timer_clock.state);
    try testing.expectEqual(dw_wdt.TimerClockPath.blocked_no_timer_clock, missing_timer_clock.timer_clock_path);
    try testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.blocked_missing_timer_clock, missing_timer_clock.probe_timeout_origin);
    try testing.expect(!missing_timer_clock.registration_requested);
    try testing.expect(!missing_timer_clock.stop_on_reboot_requested);
    try testing.expect(!missing_timer_clock.reset_release_requested);
    try testing.expect(missing_timer_clock.blocked_on_live_platform_registration);
    try testing.expect(!missing_timer_clock.blocked_on_live_mmio);
}

test "phase11 dw_wdt verify keeps imported-running handoff and shared-clock fallback explicit" {
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

    try testing.expectEqualStrings(dw_wdt.anchor_path, handoff.anchor);
    try testing.expectEqual(dw_wdt.RegistrationScaffoldState.import_running_state_then_register, handoff.state);
    try testing.expectEqual(dw_wdt.TimerClockPath.unnamed_shared_fallback, handoff.timer_clock_path);
    try testing.expectEqual(dw_wdt.ApbClockPath.optional_absent, handoff.apb_clock_path);
    try testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.imported_running_counter, handoff.probe_timeout_origin);
    try testing.expect(handoff.timer_clock_available);
    try testing.expect(handoff.imported_running_state);
    try testing.expect(!handoff.timeout_programming_requested);
    try testing.expect(handoff.registration_ready);
    try testing.expect(handoff.stop_on_reboot_requested);
    try testing.expect(handoff.reset_release_requested);
    try testing.expect(handoff.pretimeout_irq_optional);
    try testing.expect(handoff.pretimeout_irq_present);
    try testing.expectEqualStrings("platform_get_irq_optional", handoff.pretimeout_irq_call);
    try testing.expect(handoff.blocked_on_live_platform_registration);
    try testing.expect(!handoff.blocked_on_live_mmio);
}

test "phase11 dw_wdt verify keeps continued-heartbeat teardown and remove failure modes explicit" {
    var unstoppable = try dw_wdt.DwWdtLab.initFixedTops(9, false);
    _ = try unstoppable.start();
    try unstoppable.setInterruptPending(true);

    const stop_summary = unstoppable.stopSummary();
    try testing.expectEqual(dw_wdt.TeardownOutcome.continued_heartbeat, stop_summary.outcome);
    try testing.expect(stop_summary.stop_requested);
    try testing.expect(!stop_summary.enable_bit_cleared);
    try testing.expect(stop_summary.interrupt_cleared);
    try testing.expect(stop_summary.running_after_stop);
    try testing.expect(stop_summary.hardware_running_after_stop);
    try testing.expect(stop_summary.keeps_heartbeat_running);

    var teardown_unstoppable = try dw_wdt.DwWdtLab.initFixedTops(9, false);
    _ = try teardown_unstoppable.start();
    try teardown_unstoppable.setInterruptPending(true);
    const teardown_summary = try teardown_unstoppable.teardownSummary();
    try testing.expectEqual(dw_wdt.TeardownOutcome.continued_heartbeat, teardown_summary.outcome);
    try testing.expect(!teardown_summary.can_stop);
    try testing.expect(teardown_summary.stop_invoked);
    try testing.expect(teardown_summary.interrupt_cleared);
    try testing.expect(teardown_summary.running_after_teardown);
    try testing.expect(teardown_summary.hardware_running_after_teardown);

    var remove_unstoppable = try dw_wdt.DwWdtLab.initFixedTops(9, false);
    _ = try remove_unstoppable.start();
    try remove_unstoppable.setInterruptPending(true);
    const remove_summary = remove_unstoppable.removeSummary();
    try testing.expectEqualStrings(dw_wdt.anchor_path, remove_summary.anchor);
    try testing.expect(remove_summary.debugfs_clear_requested);
    try testing.expect(remove_summary.unregister_device_requested);
    try testing.expect(!remove_summary.reset_assert_requested);
    try testing.expect(remove_summary.hardware_running_before_remove);
    try testing.expect(remove_summary.hardware_running_after_remove);
    try testing.expect(remove_summary.running_after_remove);
    try testing.expect(!remove_summary.interrupt_pending_after_remove);
    try testing.expect(remove_summary.remove_leaves_hardware_running);
}

test "phase11 dw_wdt verify keeps reset-backed teardown and remove cleanup distinct" {
    var stoppable = try dw_wdt.DwWdtLab.initFixedTops(9, true);
    _ = try stoppable.start();
    try stoppable.setInterruptPending(true);

    const stop_summary = stoppable.stopSummary();
    try testing.expectEqual(dw_wdt.TeardownOutcome.reset_control_stop, stop_summary.outcome);
    try testing.expect(stop_summary.stop_requested);
    try testing.expect(stop_summary.enable_bit_cleared);
    try testing.expect(stop_summary.interrupt_cleared);
    try testing.expect(!stop_summary.running_after_stop);
    try testing.expect(!stop_summary.hardware_running_after_stop);
    try testing.expect(!stop_summary.keeps_heartbeat_running);

    var teardown_stoppable = try dw_wdt.DwWdtLab.initFixedTops(9, true);
    _ = try teardown_stoppable.start();
    try teardown_stoppable.setInterruptPending(true);
    const teardown_summary = try teardown_stoppable.teardownSummary();
    try testing.expectEqual(dw_wdt.TeardownOutcome.reset_control_stop, teardown_summary.outcome);
    try testing.expect(teardown_summary.can_stop);
    try testing.expect(teardown_summary.stop_invoked);
    try testing.expect(teardown_summary.enable_bit_cleared);
    try testing.expect(teardown_summary.interrupt_cleared);
    try testing.expect(!teardown_summary.running_after_teardown);
    try testing.expect(!teardown_summary.hardware_running_after_teardown);

    var remove_stoppable = try dw_wdt.DwWdtLab.initFixedTops(9, true);
    _ = try remove_stoppable.start();
    try remove_stoppable.setInterruptPending(true);
    const remove_summary = remove_stoppable.removeSummary();
    try testing.expect(remove_summary.reset_assert_requested);
    try testing.expect(remove_summary.hardware_running_before_remove);
    try testing.expect(!remove_summary.hardware_running_after_remove);
    try testing.expect(!remove_summary.running_after_remove);
    try testing.expect(!remove_summary.interrupt_pending_after_remove);
    try testing.expect(!remove_summary.remove_leaves_hardware_running);
}

test "phase11 dw_wdt verify keeps idle no-op teardown and remove paths explicit" {
    var idle_stop = try dw_wdt.DwWdtLab.initFixedTops(9, true);
    try idle_stop.setInterruptPending(true);
    const stop_summary = idle_stop.stopSummary();
    try testing.expectEqualStrings(dw_wdt.anchor_path, stop_summary.anchor);
    try testing.expectEqual(dw_wdt.TeardownOutcome.idle_noop, stop_summary.outcome);
    try testing.expect(idle_stop.reset_control_available);
    try testing.expect(!stop_summary.stop_requested);
    try testing.expect(!stop_summary.enable_bit_cleared);
    try testing.expect(stop_summary.interrupt_cleared);
    try testing.expect(!stop_summary.running_before_stop);
    try testing.expect(!stop_summary.running_after_stop);
    try testing.expect(!stop_summary.hardware_running_after_stop);
    try testing.expect(!stop_summary.keeps_heartbeat_running);

    var idle_teardown = try dw_wdt.DwWdtLab.initFixedTops(9, true);
    try idle_teardown.setInterruptPending(true);
    const teardown_summary = try idle_teardown.teardownSummary();
    try testing.expectEqual(dw_wdt.TeardownOutcome.idle_noop, teardown_summary.outcome);
    try testing.expect(!teardown_summary.can_stop);
    try testing.expect(!teardown_summary.running_before_teardown);
    try testing.expect(!teardown_summary.stop_invoked);
    try testing.expect(!teardown_summary.enable_bit_cleared);
    try testing.expect(teardown_summary.interrupt_cleared);
    try testing.expect(!teardown_summary.running_after_teardown);
    try testing.expect(!teardown_summary.hardware_running_after_teardown);

    var idle_remove = try dw_wdt.DwWdtLab.initFixedTops(9, true);
    try idle_remove.setInterruptPending(true);
    const remove_summary = idle_remove.removeSummary();
    try testing.expectEqualStrings(dw_wdt.anchor_path, remove_summary.anchor);
    try testing.expect(remove_summary.debugfs_clear_requested);
    try testing.expect(remove_summary.unregister_device_requested);
    try testing.expect(remove_summary.reset_control_available);
    try testing.expect(!remove_summary.reset_assert_requested);
    try testing.expect(!remove_summary.hardware_running_before_remove);
    try testing.expect(!remove_summary.hardware_running_after_remove);
    try testing.expect(!remove_summary.running_after_remove);
    try testing.expect(!remove_summary.interrupt_pending_after_remove);
    try testing.expect(!remove_summary.remove_leaves_hardware_running);
}
