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

pub fn summarizeRemoveWhenTtyAlreadyAbsent(request: VerifyRemoveHandoffRequest) VerifyRemoveHandoffSummary {
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

pub const CleanupPrerequisiteSummary = struct {
    cleanup: console.CleanupHandoffSummary,
    drops_tty_port_reference: bool,
    hangup_or_final_close_seen: bool,
};

pub fn summarizeCleanupPrerequisites(request: CleanupPrerequisiteRequest) !CleanupPrerequisiteSummary {
    if (!request.final_close_seen and !request.hangup_seen) {
        return error.CleanupRequiresFinalCloseOrHangup;
    }

    const cleanup = console.summarizeCleanupHandoff(.{
        .tty_port_release_handoff = request.tty_port_release_handoff,
        .cleanup_time_tty_port_ownership = request.cleanup_time_tty_port_ownership,
        .port_reference_drop_timing = request.port_reference_drop_timing,
    });

    return .{
        .cleanup = cleanup,
        .drops_tty_port_reference = cleanup.port_reference_drop_timing,
        .hangup_or_final_close_seen = request.final_close_seen or request.hangup_seen,
    };
}

pub const NotifierUnregisterTimingRequest = struct {
    target_present: bool,
    notifier_registered: bool,
    unregister_requested: bool,
};

pub const NotifierUnregisterTimingSummary = struct {
    edge: console.TargetlessNotifierEdgeSummary,
    unregister_stays_false: bool,
};

pub fn summarizeNotifierUnregisterTiming(request: NotifierUnregisterTimingRequest) NotifierUnregisterTimingSummary {
    const edge = console.summarizeTargetlessNotifierEdge(.{
        .target_present = request.target_present,
        .notifier_registered = request.notifier_registered,
        .unregister_requested = request.unregister_requested,
    });

    return .{
        .edge = edge,
        .unregister_stays_false = !edge.unregister_requested,
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

pub fn summarizeTargetlessSysrqDispatch(request: TargetlessSysrqDispatchRequest) TargetlessSysrqDispatchSummary {
    const handoff = sysrq.summarizeSysrqHandoff(.{
        .target_vtermno = request.target_vtermno,
        .byte = request.byte,
        .toggles_sysrq_mode = request.toggles_sysrq_mode,
        .invokes_sysrq_handler = request.invokes_sysrq_handler,
        .is_kernel_console = request.is_kernel_console,
    });

    return .{
        .handoff = handoff,
        .notifier_callback_implied = request.notifier_callback_implied and request.target_vtermno != null,
        .targetless_dispatch_without_notifier = request.target_vtermno == null and !request.notifier_callback_implied,
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

    try std.testing.expect(targetless_registered.edge.notifier_registered);
    try std.testing.expect(targetless_registered.edge.targetless_no_unregister_edge);
    try std.testing.expect(!targetless_registered.edge.unregister_requested);
    try std.testing.expect(targetless_registered.unregister_stays_false);
    try std.testing.expect(targetless_registered.edge.keeps_live_notifier_execution_out_of_scope);
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
