const std = @import("std");
const console = @import("hvc_console.zig");
const sysrq = @import("hvc_console_sysrq.zig");

pub const VerifyRemoveHandoffRequest = struct {
    tty_present: bool,
    console_lock_slot_cleared: bool,
    vtermno_and_cons_ops_released: bool,
    tty_port_put_ordered: bool,
    tty_vhangup_follow_through: bool,
    tty_kref_put_release: bool,
    keep_irq_until_hangup: bool,
    keeps_live_remove_execution_out_of_scope: bool = true,
};

pub const VerifyRemoveHandoffSummary = struct {
    tty_present: bool,
    tty_already_absent: bool,
    remove_handoff: console.RemoveHandoffSummary,
    keeps_live_remove_execution_out_of_scope: bool,
};

pub fn summarizeRemoveWhenTtyAlreadyAbsent(
    request: VerifyRemoveHandoffRequest,
) VerifyRemoveHandoffSummary {
    return .{
        .tty_present = request.tty_present,
        .tty_already_absent = !request.tty_present,
        .remove_handoff = console.summarizeRemoveHandoff(.{
            .console_lock_slot_cleared = request.console_lock_slot_cleared,
            .vtermno_and_cons_ops_released = request.vtermno_and_cons_ops_released,
            .tty_port_put_ordered = request.tty_port_put_ordered,
            .tty_vhangup_follow_through = request.tty_vhangup_follow_through,
            .tty_kref_put_release = request.tty_kref_put_release,
            .keep_irq_until_hangup = request.keep_irq_until_hangup,
        }),
        .keeps_live_remove_execution_out_of_scope = request.keeps_live_remove_execution_out_of_scope,
    };
}

pub const CleanupPrerequisiteRequest = struct {
    final_close_seen: bool,
    hangup_seen: bool,
    tty_port_release_handoff: bool,
    cleanup_time_tty_port_ownership: bool,
    port_reference_drop_timing: bool,
};

pub const CleanupTrigger = enum {
    final_close_only,
    hangup_only,
    final_close_and_hangup,
};

pub const CleanupPrerequisiteSummary = struct {
    cleanup: console.CleanupHandoffSummary,
    drops_tty_port_reference: bool,
    hangup_or_final_close_seen: bool,
    trigger: CleanupTrigger,
};

pub fn summarizeCleanupPrerequisites(
    request: CleanupPrerequisiteRequest,
) !CleanupPrerequisiteSummary {
    if (!request.final_close_seen and !request.hangup_seen) {
        return error.CleanupRequiresFinalCloseOrHangup;
    }

    const cleanup = console.summarizeCleanupHandoff(.{
        .tty_port_release_handoff = request.tty_port_release_handoff,
        .cleanup_time_tty_port_ownership = request.cleanup_time_tty_port_ownership,
        .port_reference_drop_timing = request.port_reference_drop_timing,
    });
    const trigger: CleanupTrigger = if (request.final_close_seen and request.hangup_seen)
        .final_close_and_hangup
    else if (request.final_close_seen)
        .final_close_only
    else
        .hangup_only;

    return .{
        .cleanup = cleanup,
        .drops_tty_port_reference = cleanup.port_reference_drop_timing,
        .hangup_or_final_close_seen = request.final_close_seen or request.hangup_seen,
        .trigger = trigger,
    };
}

pub const NotifierUnregisterTimingRequest = struct {
    target_present: bool,
    notifier_registered: bool,
    unregister_requested: bool,
};

pub const NotifierUnregisterTimingState = enum {
    idle_no_unregister,
    targetless_no_unregister_edge,
    targetless_unregister_request_sanitized,
    targeted_unregister_request,
};

pub const NotifierUnregisterTimingSummary = struct {
    edge: console.TargetlessNotifierEdgeSummary,
    unregister_stays_false: bool,
    targetless_unregister_request_sanitized: bool,
    state: NotifierUnregisterTimingState,
};

pub fn summarizeNotifierUnregisterTiming(
    request: NotifierUnregisterTimingRequest,
) NotifierUnregisterTimingSummary {
    const edge = console.summarizeTargetlessNotifierEdge(.{
        .target_present = request.target_present,
        .notifier_registered = request.notifier_registered,
        .unregister_requested = request.unregister_requested,
    });
    const state: NotifierUnregisterTimingState = if (request.unregister_requested and request.target_present)
        .targeted_unregister_request
    else if (request.unregister_requested)
        .targetless_unregister_request_sanitized
    else if (edge.targetless_no_unregister_edge)
        .targetless_no_unregister_edge
    else
        .idle_no_unregister;

    return .{
        .edge = edge,
        .unregister_stays_false = !edge.unregister_requested,
        .targetless_unregister_request_sanitized = request.unregister_requested and
            !request.target_present and
            !edge.unregister_requested,
        .state = state,
    };
}

pub const TargetlessSysrqDispatchRequest = struct {
    target_vtermno: ?u32,
    byte: u8,
    toggles_sysrq_mode: bool,
    invokes_sysrq_handler: bool,
    notifier_callback_implied: bool,
    is_kernel_console: bool,
};

pub const TargetlessSysrqDispatchSummary = struct {
    handoff: sysrq.SysrqHandoffSnapshot,
    notifier_callback_implied: bool,
    targetless_dispatch_without_notifier: bool,
};

pub fn summarizeTargetlessSysrqDispatch(
    request: TargetlessSysrqDispatchRequest,
) TargetlessSysrqDispatchSummary {
    const handoff = sysrq.summarizeSysrqHandoff(.{
        .target_vtermno = request.target_vtermno,
        .byte = request.byte,
        .toggles_sysrq_mode = request.toggles_sysrq_mode,
        .invokes_sysrq_handler = request.invokes_sysrq_handler,
        .is_kernel_console = request.is_kernel_console,
    });
    const notifier_callback_implied =
        request.notifier_callback_implied and handoff.invokes_sysrq_handler;

    return .{
        .handoff = handoff,
        .notifier_callback_implied = notifier_callback_implied,
        .targetless_dispatch_without_notifier = request.target_vtermno == null and
            !notifier_callback_implied,
    };
}

test "hvc_console verify keeps remove handoff explicit when tty is already absent" {
    const summary = summarizeRemoveWhenTtyAlreadyAbsent(.{
        .tty_present = false,
        .console_lock_slot_cleared = true,
        .vtermno_and_cons_ops_released = true,
        .tty_port_put_ordered = true,
        .tty_vhangup_follow_through = true,
        .tty_kref_put_release = true,
        .keep_irq_until_hangup = true,
    });

    try std.testing.expect(!summary.tty_present);
    try std.testing.expect(summary.tty_already_absent);
    try std.testing.expect(summary.remove_handoff.console_lock_slot_cleared);
    try std.testing.expect(summary.remove_handoff.tty_port_put_ordered);
    try std.testing.expect(summary.remove_handoff.keep_irq_until_hangup);
    try std.testing.expect(summary.keeps_live_remove_execution_out_of_scope);
}

test "hvc_console verify keeps attached remove handoff explicit before tty detach" {
    const summary = summarizeRemoveWhenTtyAlreadyAbsent(.{
        .tty_present = true,
        .console_lock_slot_cleared = true,
        .vtermno_and_cons_ops_released = true,
        .tty_port_put_ordered = true,
        .tty_vhangup_follow_through = true,
        .tty_kref_put_release = true,
        .keep_irq_until_hangup = true,
    });

    try std.testing.expect(summary.tty_present);
    try std.testing.expect(!summary.tty_already_absent);
    try std.testing.expect(summary.remove_handoff.console_lock_slot_cleared);
    try std.testing.expect(summary.remove_handoff.slot_release_ownership);
    try std.testing.expect(summary.remove_handoff.tty_port_put_ordered);
    try std.testing.expect(summary.remove_handoff.tty_vhangup_follow_through);
    try std.testing.expect(summary.remove_handoff.tty_kref_put_release);
    try std.testing.expect(summary.remove_handoff.keep_irq_until_hangup);
    try std.testing.expect(summary.keeps_live_remove_execution_out_of_scope);
}

test "hvc_console verify keeps cleanup prerequisite failures explicit" {
    try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, summarizeCleanupPrerequisites(.{
        .final_close_seen = false,
        .hangup_seen = false,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    }));

    const summary = try summarizeCleanupPrerequisites(.{
        .final_close_seen = true,
        .hangup_seen = false,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });

    try std.testing.expect(summary.cleanup.tty_port_release_handoff);
    try std.testing.expect(summary.cleanup.cleanup_time_tty_port_ownership);
    try std.testing.expect(summary.drops_tty_port_reference);
    try std.testing.expect(summary.hangup_or_final_close_seen);
    try std.testing.expectEqual(CleanupTrigger.final_close_only, summary.trigger);
}

test "hvc_console verify keeps hangup-only cleanup prerequisites explicit" {
    const summary = try summarizeCleanupPrerequisites(.{
        .final_close_seen = false,
        .hangup_seen = true,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });

    try std.testing.expect(summary.cleanup.tty_port_release_handoff);
    try std.testing.expect(summary.cleanup.cleanup_time_tty_port_ownership);
    try std.testing.expect(summary.cleanup.port_reference_drop_timing);
    try std.testing.expect(summary.drops_tty_port_reference);
    try std.testing.expect(summary.hangup_or_final_close_seen);
    try std.testing.expectEqual(CleanupTrigger.hangup_only, summary.trigger);
}

test "hvc_console verify keeps missing tty-port release from claiming cleanup ownership" {
    const summary = try summarizeCleanupPrerequisites(.{
        .final_close_seen = false,
        .hangup_seen = true,
        .tty_port_release_handoff = false,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });

    try std.testing.expect(!summary.cleanup.tty_port_release_handoff);
    try std.testing.expect(!summary.cleanup.cleanup_time_tty_port_ownership);
    try std.testing.expect(!summary.cleanup.port_reference_drop_timing);
    try std.testing.expect(!summary.drops_tty_port_reference);
    try std.testing.expect(summary.hangup_or_final_close_seen);
    try std.testing.expectEqual(CleanupTrigger.hangup_only, summary.trigger);
}

test "hvc_console verify keeps combined cleanup trigger explicit" {
    const summary = try summarizeCleanupPrerequisites(.{
        .final_close_seen = true,
        .hangup_seen = true,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });

    try std.testing.expect(summary.cleanup.tty_port_release_handoff);
    try std.testing.expect(summary.cleanup.cleanup_time_tty_port_ownership);
    try std.testing.expect(summary.cleanup.port_reference_drop_timing);
    try std.testing.expect(summary.drops_tty_port_reference);
    try std.testing.expect(summary.hangup_or_final_close_seen);
    try std.testing.expectEqual(CleanupTrigger.final_close_and_hangup, summary.trigger);
}

test "hvc_console verify keeps notifier unregister timing false for never-registered and targetless surfaces" {
    const never_registered = summarizeNotifierUnregisterTiming(.{
        .target_present = false,
        .notifier_registered = false,
        .unregister_requested = false,
    });
    const targetless_registered = summarizeNotifierUnregisterTiming(.{
        .target_present = false,
        .notifier_registered = true,
        .unregister_requested = false,
    });

    try std.testing.expect(!never_registered.edge.notifier_registered);
    try std.testing.expect(!never_registered.edge.targetless_no_unregister_edge);
    try std.testing.expect(never_registered.unregister_stays_false);
    try std.testing.expect(!never_registered.targetless_unregister_request_sanitized);
    try std.testing.expectEqual(NotifierUnregisterTimingState.idle_no_unregister, never_registered.state);

    try std.testing.expect(targetless_registered.edge.notifier_registered);
    try std.testing.expect(targetless_registered.edge.targetless_no_unregister_edge);
    try std.testing.expect(!targetless_registered.edge.unregister_requested);
    try std.testing.expect(targetless_registered.unregister_stays_false);
    try std.testing.expect(!targetless_registered.targetless_unregister_request_sanitized);
    try std.testing.expectEqual(
        NotifierUnregisterTimingState.targetless_no_unregister_edge,
        targetless_registered.state,
    );
    try std.testing.expect(targetless_registered.edge.keeps_live_notifier_execution_out_of_scope);
}

test "hvc_console verify keeps targetless unregister requests sanitized" {
    const summary = summarizeNotifierUnregisterTiming(.{
        .target_present = false,
        .notifier_registered = true,
        .unregister_requested = true,
    });

    try std.testing.expect(summary.edge.notifier_registered);
    try std.testing.expect(!summary.edge.targetless_no_unregister_edge);
    try std.testing.expect(!summary.edge.unregister_requested);
    try std.testing.expect(summary.unregister_stays_false);
    try std.testing.expect(summary.targetless_unregister_request_sanitized);
    try std.testing.expectEqual(
        NotifierUnregisterTimingState.targetless_unregister_request_sanitized,
        summary.state,
    );
    try std.testing.expect(summary.edge.keeps_live_notifier_execution_out_of_scope);
}

test "hvc_console verify keeps targeted unregister requests explicit" {
    const summary = summarizeNotifierUnregisterTiming(.{
        .target_present = true,
        .notifier_registered = true,
        .unregister_requested = true,
    });

    try std.testing.expect(summary.edge.target_present);
    try std.testing.expect(summary.edge.notifier_registered);
    try std.testing.expect(!summary.edge.targetless_no_unregister_edge);
    try std.testing.expect(summary.edge.unregister_requested);
    try std.testing.expect(!summary.unregister_stays_false);
    try std.testing.expect(!summary.targetless_unregister_request_sanitized);
    try std.testing.expectEqual(
        NotifierUnregisterTimingState.targeted_unregister_request,
        summary.state,
    );
    try std.testing.expect(summary.edge.keeps_live_notifier_execution_out_of_scope);
}

test "hvc_console verify keeps notifier irq helper failures explicit" {
    const active = console.summarizeNotifierIrqHelper(.{
        .irq = 3,
        .notifier_registered = true,
        .target_present = true,
        .hangup_requested = true,
    });
    const targetless = console.summarizeNotifierIrqHelper(.{
        .irq = 7,
        .notifier_registered = true,
        .target_present = false,
        .hangup_requested = true,
    });
    const invalid = console.summarizeNotifierIrqHelper(.{
        .irq = -1,
        .notifier_registered = false,
        .target_present = false,
        .hangup_requested = false,
    });
    const fake_hp: *console.HvcStruct = @ptrFromInt(1);

    try std.testing.expect(active.irq_valid);
    try std.testing.expectEqual(@as(c_int, 0), active.add_result);
    try std.testing.expect(active.del_surface_visible);
    try std.testing.expect(active.hangup_surface_visible);
    try std.testing.expect(!active.targetless_hangup_short_circuit);
    try std.testing.expect(active.keeps_live_notifier_execution_out_of_scope);

    try std.testing.expect(targetless.irq_valid);
    try std.testing.expectEqual(@as(c_int, 0), targetless.add_result);
    try std.testing.expect(targetless.del_surface_visible);
    try std.testing.expect(!targetless.hangup_surface_visible);
    try std.testing.expect(targetless.targetless_hangup_short_circuit);
    try std.testing.expect(targetless.keeps_live_notifier_execution_out_of_scope);

    try std.testing.expect(!invalid.irq_valid);
    try std.testing.expectEqual(@as(c_int, -1), invalid.add_result);
    try std.testing.expect(!invalid.del_surface_visible);
    try std.testing.expect(!invalid.hangup_surface_visible);
    try std.testing.expect(!invalid.targetless_hangup_short_circuit);
    try std.testing.expect(invalid.keeps_live_notifier_execution_out_of_scope);

    try std.testing.expectEqual(active.add_result, console.notifier_add_irq(fake_hp, 3));
    try std.testing.expectEqual(invalid.add_result, console.notifier_add_irq(fake_hp, -1));

    console.notifier_del_irq(fake_hp, 7);
    console.notifier_hangup_irq(fake_hp, 9);
}

test "hvc_console verify keeps targetless sysrq dispatch from implying notifier callbacks" {
    const summary = summarizeTargetlessSysrqDispatch(.{
        .target_vtermno = null,
        .byte = 0x0f,
        .toggles_sysrq_mode = true,
        .invokes_sysrq_handler = true,
        .notifier_callback_implied = false,
        .is_kernel_console = true,
    });

    try std.testing.expect(summary.handoff.toggles_sysrq_mode);
    try std.testing.expect(!summary.handoff.invokes_sysrq_handler);
    try std.testing.expect(summary.handoff.falls_back_to_literal);
    try std.testing.expect(summary.handoff.keeps_live_sysrq_execution_out_of_scope);
    try std.testing.expect(!summary.notifier_callback_implied);
    try std.testing.expect(summary.targetless_dispatch_without_notifier);
}

test "hvc_console verify keeps targetless literal fallback aligned with sanitized notifier state" {
    const summary = summarizeTargetlessSysrqDispatch(.{
        .target_vtermno = null,
        .byte = 0x0f,
        .toggles_sysrq_mode = false,
        .invokes_sysrq_handler = true,
        .notifier_callback_implied = true,
        .is_kernel_console = true,
    });

    try std.testing.expect(!summary.handoff.invokes_sysrq_handler);
    try std.testing.expect(summary.handoff.falls_back_to_literal);
    try std.testing.expect(!summary.notifier_callback_implied);
    try std.testing.expect(summary.targetless_dispatch_without_notifier);
}

test "hvc_console verify keeps non-kernel sysrq literal fallback from implying notifier callbacks" {
    const summary = summarizeTargetlessSysrqDispatch(.{
        .target_vtermno = 0,
        .byte = 0x0f,
        .toggles_sysrq_mode = false,
        .invokes_sysrq_handler = true,
        .notifier_callback_implied = true,
        .is_kernel_console = false,
    });

    try std.testing.expect(!summary.handoff.invokes_sysrq_handler);
    try std.testing.expect(summary.handoff.falls_back_to_literal);
    try std.testing.expect(summary.handoff.keeps_live_sysrq_execution_out_of_scope);
    try std.testing.expect(!summary.notifier_callback_implied);
    try std.testing.expect(!summary.targetless_dispatch_without_notifier);
}
