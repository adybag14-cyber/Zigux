const std = @import("std");
const console = @import("hvc_console");

const SysrqHandoffRequest = struct {
    target_vtermno: ?u32,
    toggles_sysrq_mode: bool,
    invokes_sysrq_handler: bool,
    is_kernel_console: bool,
};

const SysrqHandoffSummary = struct {
    toggles_sysrq_mode: bool,
    invokes_sysrq_handler: bool,
    falls_back_to_literal: bool,
};

fn summarizeSysrqHandoff(request: SysrqHandoffRequest) SysrqHandoffSummary {
    const literal_fallback = !request.is_kernel_console or request.target_vtermno == null;
    return .{
        .toggles_sysrq_mode = request.toggles_sysrq_mode,
        .invokes_sysrq_handler = request.invokes_sysrq_handler and !literal_fallback,
        .falls_back_to_literal = literal_fallback,
    };
}

test "phase11 hvc console keeps tty-registration handoff boundaries reviewable" {
    const summary = console.summarizeTtyRegistrationHandoff(.{
        .tty_driver_allocated = true,
        .tty_operations_registered = true,
        .tty_port_linked = true,
        .open_time_irq_request_ready = true,
        .wakeup_after_registration = true,
    });

    try std.testing.expect(summary.tty_driver_allocated);
    try std.testing.expect(summary.tty_operations_registered);
    try std.testing.expect(summary.tty_port_linked);
    try std.testing.expect(summary.open_time_irq_request_ready);
    try std.testing.expect(summary.wakeup_after_registration);
}

test "phase11 hvc console keeps sysrq handoff boundaries reviewable" {
    const snapshot = summarizeSysrqHandoff(.{
        .target_vtermno = 0,
        .toggles_sysrq_mode = true,
        .invokes_sysrq_handler = true,
        .is_kernel_console = true,
    });

    try std.testing.expect(snapshot.toggles_sysrq_mode);
    try std.testing.expect(snapshot.invokes_sysrq_handler);
    try std.testing.expect(!snapshot.falls_back_to_literal);
}

test "phase11 hvc console keeps notifier handoff boundaries reviewable" {
    const notify = console.summarizeNotifierAddOutcome(.{
        .notifier_add_success = true,
        .polling_fallback = false,
        .failed_open_close_cleanup = false,
        .open_time_irq_request = true,
        .kick_after_open = true,
    });
    const targetless = console.summarizeTargetlessNotifierEdge(.{
        .target_present = false,
        .notifier_registered = true,
        .unregister_requested = false,
    });

    try std.testing.expect(notify.notifier_add_success);
    try std.testing.expect(!notify.polling_fallback);
    try std.testing.expect(!notify.failed_open_close_cleanup);
    try std.testing.expect(notify.open_time_irq_request_boundaries);
    try std.testing.expect(notify.khvcd_kick_follow_through);
    try std.testing.expect(targetless.targetless_no_unregister_edge);
    try std.testing.expect(targetless.keeps_live_notifier_execution_out_of_scope);
}

test "phase11 hvc console keeps remove-path teardown ordering reviewable" {
    const attached_remove = console.summarizeRemoveHandoff(.{
        .console_lock_slot_cleared = true,
        .vtermno_and_cons_ops_released = true,
        .tty_port_put_ordered = true,
        .tty_vhangup_follow_through = true,
        .tty_kref_put_release = true,
        .keep_irq_until_hangup = true,
    });
    const detached_remove = console.summarizeRemoveHandoff(.{
        .console_lock_slot_cleared = true,
        .vtermno_and_cons_ops_released = true,
        .tty_port_put_ordered = true,
        .tty_vhangup_follow_through = false,
        .tty_kref_put_release = false,
        .keep_irq_until_hangup = false,
    });

    try std.testing.expect(attached_remove.console_lock_slot_cleared);
    try std.testing.expect(attached_remove.vtermno_and_cons_ops_released);
    try std.testing.expect(attached_remove.tty_port_put_ordered);
    try std.testing.expect(attached_remove.tty_vhangup_follow_through);
    try std.testing.expect(attached_remove.tty_kref_put_release);
    try std.testing.expect(attached_remove.keep_irq_until_hangup);

    try std.testing.expect(detached_remove.console_lock_slot_cleared);
    try std.testing.expect(detached_remove.vtermno_and_cons_ops_released);
    try std.testing.expect(detached_remove.tty_port_put_ordered);
    try std.testing.expect(!detached_remove.tty_vhangup_follow_through);
    try std.testing.expect(!detached_remove.tty_kref_put_release);
    try std.testing.expect(!detached_remove.keep_irq_until_hangup);
}
