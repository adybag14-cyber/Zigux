const std = @import("std");
const hvc_console = @import("hvc_console.zig");

pub const RemoveHandoffWithoutBindingRequest = struct {
    tty_already_absent: bool,
    console_binding_present: bool,
    keep_irq_until_hangup: bool,
};

pub const RemoveHandoffWithoutBindingSummary = struct {
    tty_already_absent: bool,
    detached_binding_remove_handoff: bool,
    hangup_driven_teardown_retained: bool,
    remove_handoff_reviewable: bool,
};

pub fn summarizeRemoveHandoffWithoutBinding(
    request: RemoveHandoffWithoutBindingRequest,
) RemoveHandoffWithoutBindingSummary {
    const detached_binding_remove_handoff =
        request.tty_already_absent and !request.console_binding_present;
    return .{
        .tty_already_absent = request.tty_already_absent,
        .detached_binding_remove_handoff = detached_binding_remove_handoff,
        .hangup_driven_teardown_retained = request.keep_irq_until_hangup,
        .remove_handoff_reviewable = request.tty_already_absent or
            detached_binding_remove_handoff,
    };
}

pub const NotifierUnregisterTimingState = struct {
    targetless_no_unregister_edge: bool,
    targetless_unregister_request_sanitized: bool,
    targeted_unregister_request: bool,
    keeps_live_notifier_execution_out_of_scope: bool,
};

pub fn summarizeNotifierUnregisterTiming(
    notifier_registered: bool,
    target_present: bool,
    unregister_requested: bool,
) NotifierUnregisterTimingState {
    const edge = hvc_console.summarizeTargetlessNotifierEdge(.{
        .target_present = target_present,
        .notifier_registered = notifier_registered,
        .unregister_requested = unregister_requested,
    });
    return .{
        .targetless_no_unregister_edge = edge.targetless_no_unregister_edge,
        .targetless_unregister_request_sanitized = edge.targetless_unregister_request_sanitized,
        .targeted_unregister_request = edge.unregister_requested,
        .keeps_live_notifier_execution_out_of_scope = edge.keeps_live_notifier_execution_out_of_scope,
    };
}

pub const SysrqLiteralFallbackRequest = struct {
    tty_registered: bool,
    notifier_registered: bool,
    target_present: bool,
    sysrq_requested: bool,
    kernel_sysrq_byte: bool = true,
};

pub const SysrqLiteralFallbackSummary = struct {
    tty_registered: bool,
    notifier_registered: bool,
    target_present: bool,
    kernel_sysrq_byte: bool,
    dispatch_allowed: bool,
    targetless_dispatch_without_notifier: bool,
    targetless_dispatch_with_notifier_sanitized: bool,
    literal_fallback_required: bool,
    literal_byte_retained: bool,
    keeps_live_sysrq_execution_out_of_scope: bool,
};

pub fn summarizeNotifierDispatch(
    request: SysrqLiteralFallbackRequest,
) error{NotifierDispatchRequiresTtyRegistration}!SysrqLiteralFallbackSummary {
    if (!request.tty_registered) return error.NotifierDispatchRequiresTtyRegistration;

    const dispatch_allowed =
        request.kernel_sysrq_byte and request.sysrq_requested and request.notifier_registered and request.target_present;
    const targetless_dispatch_without_notifier =
        request.kernel_sysrq_byte and request.sysrq_requested and !request.notifier_registered and !request.target_present;
    const targetless_dispatch_with_notifier_sanitized =
        request.kernel_sysrq_byte and request.sysrq_requested and request.notifier_registered and !request.target_present;

    return .{
        .tty_registered = request.tty_registered,
        .notifier_registered = request.notifier_registered,
        .target_present = request.target_present,
        .kernel_sysrq_byte = request.kernel_sysrq_byte,
        .dispatch_allowed = dispatch_allowed,
        .targetless_dispatch_without_notifier = targetless_dispatch_without_notifier,
        .targetless_dispatch_with_notifier_sanitized = targetless_dispatch_with_notifier_sanitized,
        .literal_fallback_required = request.kernel_sysrq_byte and request.sysrq_requested and !dispatch_allowed,
        .literal_byte_retained = !request.kernel_sysrq_byte and request.sysrq_requested,
        .keeps_live_sysrq_execution_out_of_scope = true,
    };
}

pub fn summarizeCleanupTrigger(
    final_close_completed: bool,
    hangup_completed: bool,
) error{CleanupRequiresFinalCloseOrHangup}!hvc_console.CleanupPrerequisiteSummary {
    return hvc_console.summarizeCleanupPrerequisite(.{
        .final_close_completed = final_close_completed,
        .hangup_completed = hangup_completed,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });
}

test "phase11 hvc verify helper keeps tty-already-absent remove handoff explicit" {
    const summary = summarizeRemoveHandoffWithoutBinding(.{
        .tty_already_absent = true,
        .console_binding_present = true,
        .keep_irq_until_hangup = true,
    });

    try std.testing.expect(summary.tty_already_absent);
    try std.testing.expect(!summary.detached_binding_remove_handoff);
    try std.testing.expect(summary.hangup_driven_teardown_retained);
    try std.testing.expect(summary.remove_handoff_reviewable);
}

test "phase11 hvc verify helper keeps detached binding remove handoff reviewable" {
    const summary = summarizeRemoveHandoffWithoutBinding(.{
        .tty_already_absent = true,
        .console_binding_present = false,
        .keep_irq_until_hangup = true,
    });

    try std.testing.expect(summary.detached_binding_remove_handoff);
    try std.testing.expect(summary.hangup_driven_teardown_retained);
    try std.testing.expect(summary.remove_handoff_reviewable);
}

test "phase11 hvc verify helper keeps cleanup trigger prerequisites explicit" {
    try std.testing.expectError(
        error.CleanupRequiresFinalCloseOrHangup,
        summarizeCleanupTrigger(false, false),
    );

    const hangup_only = try summarizeCleanupTrigger(false, true);
    try std.testing.expectEqual(hvc_console.CleanupTrigger.hangup_only, hangup_only.trigger);

    const combined = try summarizeCleanupTrigger(true, true);
    try std.testing.expectEqual(
        hvc_console.CleanupTrigger.final_close_and_hangup,
        combined.trigger,
    );
}

test "phase11 hvc verify helper keeps notifier prerequisite failures explicit" {
    try std.testing.expectError(
        error.NotifierDispatchRequiresTtyRegistration,
        summarizeNotifierDispatch(.{
            .tty_registered = false,
            .notifier_registered = true,
            .target_present = true,
            .sysrq_requested = true,
        }),
    );
}

test "phase11 hvc verify helper keeps targetless unregister requests visible as sanitized edges" {
    const sanitized = summarizeNotifierUnregisterTiming(true, false, true);
    try std.testing.expect(!sanitized.targetless_no_unregister_edge);
    try std.testing.expect(sanitized.targetless_unregister_request_sanitized);
    try std.testing.expect(!sanitized.targeted_unregister_request);
    try std.testing.expect(sanitized.keeps_live_notifier_execution_out_of_scope);

    const targeted = summarizeNotifierUnregisterTiming(true, true, true);
    try std.testing.expect(!targeted.targetless_no_unregister_edge);
    try std.testing.expect(!targeted.targetless_unregister_request_sanitized);
    try std.testing.expect(targeted.targeted_unregister_request);
}

test "phase11 hvc verify helper keeps targetless sysrq fallback reviewable" {
    const summary = try summarizeNotifierDispatch(.{
        .tty_registered = true,
        .notifier_registered = false,
        .target_present = false,
        .sysrq_requested = true,
    });

    try std.testing.expect(!summary.dispatch_allowed);
    try std.testing.expect(summary.targetless_dispatch_without_notifier);
    try std.testing.expect(!summary.targetless_dispatch_with_notifier_sanitized);
    try std.testing.expect(summary.literal_fallback_required);
    try std.testing.expect(!summary.literal_byte_retained);
    try std.testing.expect(summary.keeps_live_sysrq_execution_out_of_scope);
}

test "phase11 hvc verify helper keeps registered targetless sysrq fallback sanitized" {
    const summary = try summarizeNotifierDispatch(.{
        .tty_registered = true,
        .notifier_registered = true,
        .target_present = false,
        .sysrq_requested = true,
    });

    try std.testing.expect(!summary.dispatch_allowed);
    try std.testing.expect(!summary.targetless_dispatch_without_notifier);
    try std.testing.expect(summary.targetless_dispatch_with_notifier_sanitized);
    try std.testing.expect(summary.literal_fallback_required);
    try std.testing.expect(!summary.literal_byte_retained);
    try std.testing.expect(summary.keeps_live_sysrq_execution_out_of_scope);
}

test "phase11 hvc verify helper keeps non-kernel sysrq literal fallback explicit" {
    const summary = try summarizeNotifierDispatch(.{
        .tty_registered = true,
        .notifier_registered = true,
        .target_present = true,
        .sysrq_requested = true,
        .kernel_sysrq_byte = false,
    });

    try std.testing.expect(!summary.dispatch_allowed);
    try std.testing.expect(!summary.targetless_dispatch_without_notifier);
    try std.testing.expect(!summary.targetless_dispatch_with_notifier_sanitized);
    try std.testing.expect(!summary.literal_fallback_required);
    try std.testing.expect(summary.literal_byte_retained);
    try std.testing.expect(summary.keeps_live_sysrq_execution_out_of_scope);
}
