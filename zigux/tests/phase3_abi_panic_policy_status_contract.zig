const std = @import("std");
const abi = @import("abi_bindings");
const panic_policy = @import("panic_policy_helpers");

fn policyFor(mode: abi.PanicMode) abi.InteropPolicy {
    return .{
        .panic_mode = @intFromEnum(mode),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
}

test "panic policy status routes match action and return semantics" {
    const abort_policy = policyFor(.abort);
    const bug_policy = policyFor(.bug);
    const warn_policy = policyFor(.warn);

    try std.testing.expectEqual(panic_policy.Action.abort_now, panic_policy.actionForInteropPolicy(abort_policy).?);
    try std.testing.expectEqual(panic_policy.Action.bug_check, panic_policy.actionForInteropPolicy(bug_policy).?);
    try std.testing.expectEqual(panic_policy.Action.warn_and_return, panic_policy.actionForInteropPolicy(warn_policy).?);

    try std.testing.expect(panic_policy.causesImmediateHaltInteropPolicy(abort_policy));
    try std.testing.expect(panic_policy.causesImmediateHaltInteropPolicy(bug_policy));
    try std.testing.expect(!panic_policy.causesImmediateHaltInteropPolicy(warn_policy));

    try std.testing.expect(!panic_policy.canReturnInteropPolicy(abort_policy));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(bug_policy));
    try std.testing.expect(panic_policy.canReturnInteropPolicy(warn_policy));

    const abort_status = abi.makeStatus(-1, .kernel);
    const bug_status = abi.makeStatus(-22, .kernel);
    const warn_status = abi.okStatus(.helpers);

    try std.testing.expect(!abi.statusIsOk(abort_status));
    try std.testing.expect(!abi.statusIsOk(bug_status));
    try std.testing.expect(abi.statusIsOk(warn_status));
    try std.testing.expect(abi.statusHasKnownFacility(abort_status));
    try std.testing.expect(abi.statusHasKnownFacility(bug_status));
    try std.testing.expect(abi.statusHasKnownFacility(warn_status));
}

test "panic policy reserved byte rejects every status route" {
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };

    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, null), panic_policy.escalationFromInteropPolicy(reserved_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!panic_policy.causesImmediateHaltInteropPolicy(reserved_policy));
    try std.testing.expect(!panic_policy.emitsKernelBugInteropPolicy(reserved_policy));
    try std.testing.expect(!panic_policy.permitsWarningOnlyContinuationInteropPolicy(reserved_policy));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(reserved_policy));

    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireActionInteropPolicy(reserved_policy, .warn_and_return),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireEscalationInteropPolicy(reserved_policy, .warning_only),
    );
}

test "panic policy byte helpers keep bug escalation separate from abort" {
    try panic_policy.requireActionPolicyBytes(
        @intFromEnum(abi.PanicMode.abort),
        0,
        .abort_now,
    );
    try panic_policy.requireActionPolicyBytes(
        @intFromEnum(abi.PanicMode.bug),
        0,
        .bug_check,
    );
    try panic_policy.requireActionPolicyBytes(
        @intFromEnum(abi.PanicMode.warn),
        0,
        .warn_and_return,
    );

    try panic_policy.requireEscalationPolicyBytes(
        @intFromEnum(abi.PanicMode.abort),
        0,
        .immediate_abort,
    );
    try panic_policy.requireEscalationPolicyBytes(
        @intFromEnum(abi.PanicMode.bug),
        0,
        .kernel_bug,
    );
    try panic_policy.requireEscalationPolicyBytes(
        @intFromEnum(abi.PanicMode.warn),
        0,
        .warning_only,
    );

    try std.testing.expect(panic_policy.causesImmediateHaltPolicyBytes(@intFromEnum(abi.PanicMode.abort), 0));
    try std.testing.expect(panic_policy.causesImmediateHaltPolicyBytes(@intFromEnum(abi.PanicMode.bug), 0));
    try std.testing.expect(!panic_policy.causesImmediateHaltPolicyBytes(@intFromEnum(abi.PanicMode.warn), 0));

    try std.testing.expect(!panic_policy.emitsKernelBugPolicyBytes(@intFromEnum(abi.PanicMode.abort), 0));
    try std.testing.expect(panic_policy.emitsKernelBugPolicyBytes(@intFromEnum(abi.PanicMode.bug), 0));
    try std.testing.expect(!panic_policy.emitsKernelBugPolicyBytes(@intFromEnum(abi.PanicMode.warn), 0));

    try std.testing.expectError(
        error.UnexpectedAction,
        panic_policy.requireActionPolicyBytes(@intFromEnum(abi.PanicMode.bug), 0, .abort_now),
    );
    try std.testing.expectError(
        error.UnexpectedEscalation,
        panic_policy.requireEscalationPolicyBytes(@intFromEnum(abi.PanicMode.bug), 0, .immediate_abort),
    );
}

test "panic policy unknown bytes do not synthesize ok status decisions" {
    const unknown_policy = abi.InteropPolicy{
        .panic_mode = 0xff,
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, null), panic_policy.escalationFromInteropPolicy(unknown_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(unknown_policy));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(unknown_policy));
    try std.testing.expect(!panic_policy.permitsWarningOnlyContinuationInteropPolicy(unknown_policy));

    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireActionPolicyBytes(0xff, 0, .warn_and_return),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireEscalationPolicyBytes(0xff, 0, .warning_only),
    );
}
