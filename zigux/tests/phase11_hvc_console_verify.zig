const std = @import("std");
const hvc_console = @import("hvc_console");

test "phase11 hvc console verify keeps poll drain wakeup ordering distinct from retry-only loops" {
    const active = hvc_console.summarizePollDrainOrder(.{
        .irq_backed_drained_reads = true,
        .partial_write_progress = true,
        .stalled_retry_path = false,
        .pending_sysrq_dispatch_separate = true,
        .tty_wakeup_pending = true,
        .read_activity_detected = true,
    });
    const retry_only = hvc_console.summarizePollDrainOrder(.{
        .irq_backed_drained_reads = false,
        .partial_write_progress = false,
        .stalled_retry_path = true,
        .pending_sysrq_dispatch_separate = false,
        .tty_wakeup_pending = true,
        .read_activity_detected = false,
    });

    try std.testing.expect(active.tty_wakeup_precedes_flip_push);
    try std.testing.expect(active.read_activity_resets_timeout);
    try std.testing.expect(!retry_only.tty_wakeup_precedes_flip_push);
    try std.testing.expect(!retry_only.read_activity_resets_timeout);
    try std.testing.expect(retry_only.stalled_retry_path);
}

test "phase11 hvc console verify keeps cleanup trigger selection explicit across close and hangup" {
    const final_close_only = try hvc_console.summarizeCleanupPrerequisite(.{
        .final_close_completed = true,
        .hangup_completed = false,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });
    const hangup_only = try hvc_console.summarizeCleanupPrerequisite(.{
        .final_close_completed = false,
        .hangup_completed = true,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });
    const combined = try hvc_console.summarizeCleanupPrerequisite(.{
        .final_close_completed = true,
        .hangup_completed = true,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });

    try std.testing.expectEqual(hvc_console.CleanupTrigger.final_close_only, final_close_only.trigger);
    try std.testing.expectEqual(hvc_console.CleanupTrigger.hangup_only, hangup_only.trigger);
    try std.testing.expectEqual(hvc_console.CleanupTrigger.final_close_and_hangup, combined.trigger);
    try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, hvc_console.summarizeCleanupPrerequisite(.{
        .final_close_completed = false,
        .hangup_completed = false,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    }));
}

test "phase11 hvc console verify keeps targetless notifier unregister sanitization reviewable" {
    const targetless = hvc_console.summarizeTargetlessNotifierEdge(.{
        .target_present = false,
        .notifier_registered = true,
        .unregister_requested = true,
    });
    const targeted = hvc_console.summarizeTargetlessNotifierEdge(.{
        .target_present = true,
        .notifier_registered = true,
        .unregister_requested = true,
    });

    try std.testing.expect(targetless.targetless_unregister_request_sanitized);
    try std.testing.expect(!targetless.unregister_requested);
    try std.testing.expect(!targeted.targetless_unregister_request_sanitized);
    try std.testing.expect(targeted.unregister_requested);
}

test "phase11 hvc console verify keeps notifier irq helper targetless hangup and invalid irq distinct" {
    const targetless = hvc_console.summarizeNotifierIrqHelper(.{
        .irq = 7,
        .notifier_registered = true,
        .target_present = false,
        .hangup_requested = true,
    });
    const invalid = hvc_console.summarizeNotifierIrqHelper(.{
        .irq = -1,
        .notifier_registered = false,
        .target_present = false,
        .hangup_requested = false,
    });
    const fake_hp: *hvc_console.HvcStruct = @ptrFromInt(1);

    try std.testing.expect(targetless.irq_valid);
    try std.testing.expect(targetless.del_surface_visible);
    try std.testing.expect(!targetless.hangup_surface_visible);
    try std.testing.expect(targetless.targetless_hangup_short_circuit);

    try std.testing.expect(!invalid.irq_valid);
    try std.testing.expectEqual(@as(c_int, -1), invalid.add_result);
    try std.testing.expectEqual(invalid.add_result, hvc_console.notifier_add_irq(fake_hp, -1));

    hvc_console.notifier_del_irq(fake_hp, 7);
    hvc_console.notifier_hangup_irq(fake_hp, 7);
}

test "phase11 hvc console verify keeps modem-control visibility tied to available ops" {
    const active = hvc_console.summarizeModemControlHandoff(.{
        .tiocmget_available = true,
        .tiocmset_available = true,
        .dtr_rts_available = true,
        .set_mask_requested = true,
        .clear_mask_requested = true,
        .dtr_rts_asserted = true,
    });
    const read_only = hvc_console.summarizeModemControlHandoff(.{
        .tiocmget_available = true,
        .tiocmset_available = false,
        .dtr_rts_available = false,
        .set_mask_requested = true,
        .clear_mask_requested = false,
        .dtr_rts_asserted = true,
    });

    try std.testing.expect(active.get_surface_visible);
    try std.testing.expect(active.set_surface_visible);
    try std.testing.expect(active.dtr_rts_surface_visible);
    try std.testing.expect(active.set_mask_requested);
    try std.testing.expect(active.clear_mask_requested);
    try std.testing.expect(active.dtr_rts_asserted);

    try std.testing.expect(read_only.get_surface_visible);
    try std.testing.expect(!read_only.set_surface_visible);
    try std.testing.expect(!read_only.dtr_rts_surface_visible);
    try std.testing.expect(!read_only.set_mask_requested);
    try std.testing.expect(!read_only.clear_mask_requested);
    try std.testing.expect(!read_only.dtr_rts_asserted);
}

test "phase11 hvc console verify keeps kick wakeup cue bounded to visible handoff surfaces" {
    const summary = hvc_console.summarizeKickWakeupCue(.{
        .registration_handoff_visible = true,
        .notifier_add_handoff_visible = true,
        .khvcd_polling_contract_visible = true,
    });

    try std.testing.expect(summary.registration_handoff_visible);
    try std.testing.expect(summary.notifier_add_handoff_visible);
    try std.testing.expect(summary.khvcd_polling_contract_visible);
    try std.testing.expect(summary.keeps_live_khvcd_execution_out_of_scope);

    hvc_console.hvc_kick();
}
