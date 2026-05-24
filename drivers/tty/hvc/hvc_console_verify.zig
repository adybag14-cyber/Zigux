const std = @import("std");
const hvc_console = @import("hvc_console.zig");

pub const RemoveHandoffVerifyState = enum {
    tty_already_absent,
    detached_binding_remove_handoff,
};

pub const RemoveHandoffVerifyRequest = struct {
    tty_present_at_remove: bool,
    teardown_outlives_console_binding: bool,
};

pub const RemoveHandoffVerifySummary = struct {
    state: RemoveHandoffVerifyState,
    keeps_live_remove_execution_out_of_scope: bool,
};

pub fn summarizeRemoveHandoffVerify(request: RemoveHandoffVerifyRequest) RemoveHandoffVerifySummary {
    return .{
        .state = if (request.tty_present_at_remove)
            .detached_binding_remove_handoff
        else
            .tty_already_absent,
        .keeps_live_remove_execution_out_of_scope = request.teardown_outlives_console_binding or !request.tty_present_at_remove,
    };
}

pub const CleanupTrigger = hvc_console.CleanupTrigger;
pub const CleanupPrerequisiteRequest = hvc_console.CleanupPrerequisiteRequest;
pub const CleanupPrerequisiteSummary = hvc_console.CleanupPrerequisiteSummary;

pub fn summarizeCleanupPrerequisite(
    request: CleanupPrerequisiteRequest,
) error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary {
    return hvc_console.summarizeCleanupPrerequisite(request);
}

pub const NotifierUnregisterTimingState = enum {
    targetless_no_unregister_edge,
    targetless_unregister_request_sanitized,
    targeted_unregister_request,
};

pub const NotifierUnregisterTimingRequest = struct {
    target_present: bool,
    notifier_registered: bool,
    unregister_requested: bool,
};

pub const NotifierUnregisterTimingSummary = struct {
    state: NotifierUnregisterTimingState,
    keeps_live_notifier_execution_out_of_scope: bool,
};

pub fn summarizeNotifierUnregisterTiming(
    request: NotifierUnregisterTimingRequest,
) NotifierUnregisterTimingSummary {
    const edge = hvc_console.summarizeTargetlessNotifierEdge(.{
        .target_present = request.target_present,
        .notifier_registered = request.notifier_registered,
        .unregister_requested = request.unregister_requested,
    });

    const state: NotifierUnregisterTimingState = if (edge.targetless_no_unregister_edge)
        .targetless_no_unregister_edge
    else if (edge.targetless_unregister_request_sanitized)
        .targetless_unregister_request_sanitized
    else
        .targeted_unregister_request;

    return .{
        .state = state,
        .keeps_live_notifier_execution_out_of_scope = edge.keeps_live_notifier_execution_out_of_scope,
    };
}

pub const NotifierDispatchTimingState = enum {
    targeted_dispatch_ready,
    targetless_dispatch_without_notifier,
};

pub const NotifierDispatchRequest = struct {
    tty_registered: bool,
    notifier_registered: bool,
    target_present: bool,
};

pub const NotifierDispatchSummary = struct {
    state: NotifierDispatchTimingState,
    notifier_callback_available: bool,
    keeps_live_notifier_execution_out_of_scope: bool,
};

pub fn summarizeNotifierDispatchPrerequisite(
    request: NotifierDispatchRequest,
) error{NotifierDispatchRequiresTtyRegistration}!NotifierDispatchSummary {
    if (!request.tty_registered) return error.NotifierDispatchRequiresTtyRegistration;

    const notifier_callback_available = request.notifier_registered and request.target_present;
    return .{
        .state = if (notifier_callback_available)
            .targeted_dispatch_ready
        else
            .targetless_dispatch_without_notifier,
        .notifier_callback_available = notifier_callback_available,
        .keeps_live_notifier_execution_out_of_scope = true,
    };
}

pub const SysrqLiteralFallbackRequest = struct {
    sysrq_requested: bool,
    kernel_sysrq_handler_present: bool,
    literal_fallback_available: bool,
};

pub const SysrqLiteralFallbackSummary = struct {
    uses_literal_fallback: bool,
    targetless_dispatch_without_notifier: bool,
    keeps_live_sysrq_execution_out_of_scope: bool,
};

pub fn summarizeSysrqLiteralFallback(
    request: SysrqLiteralFallbackRequest,
) SysrqLiteralFallbackSummary {
    const uses_literal_fallback = request.sysrq_requested and
        !request.kernel_sysrq_handler_present and
        request.literal_fallback_available;

    return .{
        .uses_literal_fallback = uses_literal_fallback,
        .targetless_dispatch_without_notifier = uses_literal_fallback,
        .keeps_live_sysrq_execution_out_of_scope = true,
    };
}

test "phase11 hvc verify keeps tty-already-absent remove handoff explicit" {
    const summary = summarizeRemoveHandoffVerify(.{
        .tty_present_at_remove = false,
        .teardown_outlives_console_binding = false,
    });

    try std.testing.expectEqual(RemoveHandoffVerifyState.tty_already_absent, summary.state);
    try std.testing.expect(summary.keeps_live_remove_execution_out_of_scope);
}

test "phase11 hvc verify keeps detached-binding remove handoff explicit" {
    const summary = summarizeRemoveHandoffVerify(.{
        .tty_present_at_remove = true,
        .teardown_outlives_console_binding = true,
    });

    try std.testing.expectEqual(RemoveHandoffVerifyState.detached_binding_remove_handoff, summary.state);
    try std.testing.expect(summary.keeps_live_remove_execution_out_of_scope);
}

test "phase11 hvc verify keeps cleanup prerequisite trigger splits explicit" {
    const hangup_only = try summarizeCleanupPrerequisite(.{
        .final_close_completed = false,
        .hangup_completed = true,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });
    const combined = try summarizeCleanupPrerequisite(.{
        .final_close_completed = true,
        .hangup_completed = true,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });

    try std.testing.expectEqual(CleanupTrigger.hangup_only, hangup_only.trigger);
    try std.testing.expectEqual(CleanupTrigger.final_close_and_hangup, combined.trigger);
    try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, summarizeCleanupPrerequisite(.{
        .final_close_completed = false,
        .hangup_completed = false,
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    }));
}

test "phase11 hvc verify keeps notifier unregister timing states explicit" {
    const targetless = summarizeNotifierUnregisterTiming(.{
        .target_present = false,
        .notifier_registered = true,
        .unregister_requested = false,
    });
    const sanitized = summarizeNotifierUnregisterTiming(.{
        .target_present = false,
        .notifier_registered = true,
        .unregister_requested = true,
    });
    const targeted = summarizeNotifierUnregisterTiming(.{
        .target_present = true,
        .notifier_registered = true,
        .unregister_requested = true,
    });

    try std.testing.expectEqual(NotifierUnregisterTimingState.targetless_no_unregister_edge, targetless.state);
    try std.testing.expectEqual(NotifierUnregisterTimingState.targetless_unregister_request_sanitized, sanitized.state);
    try std.testing.expectEqual(NotifierUnregisterTimingState.targeted_unregister_request, targeted.state);
    try std.testing.expect(targetless.keeps_live_notifier_execution_out_of_scope);
    try std.testing.expect(sanitized.keeps_live_notifier_execution_out_of_scope);
    try std.testing.expect(targeted.keeps_live_notifier_execution_out_of_scope);
}

test "phase11 hvc verify keeps notifier dispatch prerequisite failures explicit" {
    try std.testing.expectError(error.NotifierDispatchRequiresTtyRegistration, summarizeNotifierDispatchPrerequisite(.{
        .tty_registered = false,
        .notifier_registered = true,
        .target_present = true,
    }));
}

test "phase11 hvc verify keeps targetless dispatch without notifier explicit" {
    const summary = try summarizeNotifierDispatchPrerequisite(.{
        .tty_registered = true,
        .notifier_registered = false,
        .target_present = false,
    });

    try std.testing.expectEqual(NotifierDispatchTimingState.targetless_dispatch_without_notifier, summary.state);
    try std.testing.expect(!summary.notifier_callback_available);
    try std.testing.expect(summary.keeps_live_notifier_execution_out_of_scope);
}

test "phase11 hvc verify keeps literal-fallback helpers explicit" {
    const summary = summarizeSysrqLiteralFallback(.{
        .sysrq_requested = true,
        .kernel_sysrq_handler_present = false,
        .literal_fallback_available = true,
    });

    try std.testing.expect(summary.uses_literal_fallback);
    try std.testing.expect(summary.targetless_dispatch_without_notifier);
    try std.testing.expect(summary.keeps_live_sysrq_execution_out_of_scope);
}
