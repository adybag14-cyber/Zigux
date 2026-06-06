const std = @import("std");
const abi = @import("abi_bindings");
const panic_policy = @import("panic_policy_helpers");

fn policy(
    panic_mode: u8,
    allocator_mode: u8,
    unsafe_scope: u8,
    reserved: u8,
) abi.InteropPolicy {
    return .{
        .panic_mode = panic_mode,
        .allocator_mode = allocator_mode,
        .unsafe_scope = unsafe_scope,
        .reserved = reserved,
    };
}

test "phase3 panic-policy byte contract keeps action and escalation domains aligned" {
    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromByte(9));

    try std.testing.expectEqual(panic_policy.Escalation.immediate_abort, panic_policy.escalationFor(.abort));
    try std.testing.expectEqual(panic_policy.Escalation.kernel_bug, panic_policy.escalationFor(.bug));
    try std.testing.expectEqual(panic_policy.Escalation.warning_only, panic_policy.escalationFor(.warn));

    try std.testing.expectEqual(panic_policy.Action.abort_now, panic_policy.actionFor(.abort));
    try std.testing.expectEqual(panic_policy.Action.bug_check, panic_policy.actionFor(.bug));
    try std.testing.expectEqual(panic_policy.Action.warn_and_return, panic_policy.actionFor(.warn));

    try std.testing.expectEqual(@as(?panic_policy.Escalation, .immediate_abort), panic_policy.escalationFromByte(0));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .kernel_bug), panic_policy.escalationFromByte(1));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .warning_only), panic_policy.escalationFromByte(2));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, null), panic_policy.escalationFromByte(9));

    try std.testing.expectEqual(@as(?panic_policy.Action, .abort_now), panic_policy.actionForByte(0));
    try std.testing.expectEqual(@as(?panic_policy.Action, .bug_check), panic_policy.actionForByte(1));
    try std.testing.expectEqual(@as(?panic_policy.Action, .warn_and_return), panic_policy.actionForByte(2));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForByte(9));
}

test "phase3 panic-policy byte contract rejects reserved interop bytes before policy action" {
    const abort_policy = policy(0, 2, 1, 0);
    const bug_policy = policy(1, 0, 2, 0);
    const warn_policy = policy(2, 1, 0, 0);
    const unknown_policy = policy(9, 1, 0, 0);
    const reserved_policy = policy(2, 1, 0, 1);

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(abort_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromInteropPolicy(bug_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromInteropPolicy(warn_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_policy));

    try std.testing.expectEqual(@as(?panic_policy.Action, .abort_now), panic_policy.actionForInteropPolicy(abort_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, .bug_check), panic_policy.actionForInteropPolicy(bug_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, .warn_and_return), panic_policy.actionForInteropPolicy(warn_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForInteropPolicy(reserved_policy));

    try std.testing.expectEqual(
        @as(?panic_policy.Escalation, .warning_only),
        panic_policy.escalationFromInteropPolicy(warn_policy),
    );
    try std.testing.expectEqual(@as(?panic_policy.Escalation, null), panic_policy.escalationFromInteropPolicy(reserved_policy));
    try std.testing.expect(panic_policy.recognizesInteropPolicy(abort_policy));
    try std.testing.expect(panic_policy.recognizesInteropPolicy(bug_policy));
    try std.testing.expect(panic_policy.recognizesInteropPolicy(warn_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(unknown_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(reserved_policy));
}

test "phase3 panic-policy byte contract keeps require-helper failures explicit" {
    const abort_policy = policy(0, 0, 0, 0);
    const bug_policy = policy(1, 0, 0, 0);
    const warn_policy = policy(2, 0, 0, 0);
    const reserved_policy = policy(2, 0, 0, 1);

    try panic_policy.requireEscalationByte(0, .immediate_abort);
    try panic_policy.requireEscalationByte(1, .kernel_bug);
    try panic_policy.requireEscalationByte(2, .warning_only);
    try std.testing.expectError(error.UnexpectedEscalation, panic_policy.requireEscalationByte(2, .kernel_bug));
    try std.testing.expectError(error.InvalidInteropPolicy, panic_policy.requireEscalationByte(9, .warning_only));
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireEscalationPolicyBytes(2, 1, .warning_only),
    );

    try panic_policy.requireActionInteropPolicy(abort_policy, .abort_now);
    try panic_policy.requireActionInteropPolicy(bug_policy, .bug_check);
    try panic_policy.requireActionInteropPolicy(warn_policy, .warn_and_return);
    try std.testing.expectError(error.UnexpectedAction, panic_policy.requireActionInteropPolicy(warn_policy, .bug_check));
    try std.testing.expectError(error.InvalidInteropPolicy, panic_policy.requireActionInteropPolicy(reserved_policy, .warn_and_return));

    try panic_policy.requireActionByte(0, .abort_now);
    try panic_policy.requireActionByte(1, .bug_check);
    try panic_policy.requireActionByte(2, .warn_and_return);
    try std.testing.expectError(error.UnexpectedAction, panic_policy.requireActionByte(1, .abort_now));
    try std.testing.expectError(error.InvalidInteropPolicy, panic_policy.requireActionByte(9, .bug_check));
}

test "phase3 panic-policy byte contract keeps halt bug and return predicates aligned" {
    const abort_policy = policy(0, 2, 1, 0);
    const bug_policy = policy(1, 0, 2, 0);
    const warn_policy = policy(2, 1, 0, 0);
    const reserved_policy = policy(2, 1, 0, 1);

    try std.testing.expect(panic_policy.causesImmediateHaltByte(0));
    try std.testing.expect(panic_policy.causesImmediateHaltByte(1));
    try std.testing.expect(!panic_policy.causesImmediateHaltByte(2));
    try std.testing.expect(!panic_policy.causesImmediateHaltByte(9));
    try std.testing.expect(!panic_policy.causesImmediateHaltPolicyBytes(2, 1));

    try std.testing.expect(!panic_policy.emitsKernelBugInteropPolicy(abort_policy));
    try std.testing.expect(panic_policy.emitsKernelBugInteropPolicy(bug_policy));
    try std.testing.expect(!panic_policy.emitsKernelBugInteropPolicy(warn_policy));
    try std.testing.expect(!panic_policy.emitsKernelBugInteropPolicy(reserved_policy));

    try std.testing.expect(!panic_policy.permitsWarningOnlyContinuationInteropPolicy(abort_policy));
    try std.testing.expect(!panic_policy.permitsWarningOnlyContinuationInteropPolicy(bug_policy));
    try std.testing.expect(panic_policy.permitsWarningOnlyContinuationInteropPolicy(warn_policy));
    try std.testing.expect(!panic_policy.permitsWarningOnlyContinuationInteropPolicy(reserved_policy));

    try std.testing.expect(!panic_policy.canReturnInteropPolicy(abort_policy));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(bug_policy));
    try std.testing.expect(panic_policy.canReturnInteropPolicy(warn_policy));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(reserved_policy));
}
