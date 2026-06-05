const std = @import("std");

const abi = @import("abi_bindings");
const panic_policy = @import("panic_policy");

fn policy(panic_mode: u8, allocator_mode: u8, unsafe_scope: u8, reserved: u8) abi.InteropPolicy {
    return .{
        .panic_mode = panic_mode,
        .allocator_mode = allocator_mode,
        .unsafe_scope = unsafe_scope,
        .reserved = reserved,
    };
}

test "phase3 panic policy maps ABI bytes to explicit modes" {
    try std.testing.expectEqual(@as(u8, 0), abi.PANIC_ABORT);
    try std.testing.expectEqual(@as(u8, 1), abi.PANIC_BUG);
    try std.testing.expectEqual(@as(u8, 2), abi.PANIC_WARN);

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromByte(abi.PANIC_ABORT));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromByte(abi.PANIC_BUG));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromByte(abi.PANIC_WARN));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromByte(3));

    try std.testing.expect(panic_policy.recognizesByte(abi.PANIC_ABORT));
    try std.testing.expect(panic_policy.recognizesByte(abi.PANIC_BUG));
    try std.testing.expect(panic_policy.recognizesByte(abi.PANIC_WARN));
    try std.testing.expect(!panic_policy.recognizesByte(0xff));
}

test "phase3 panic policy treats reserved interop bytes as fail closed" {
    const abort_policy = policy(abi.PANIC_ABORT, 2, 1, 0);
    const bug_policy = policy(abi.PANIC_BUG, 0, 2, 0);
    const warn_policy = policy(abi.PANIC_WARN, 1, 0, 0);
    const reserved_policy = policy(abi.PANIC_WARN, 1, 0, 1);
    const unknown_policy = policy(0x80, 0, 0, 0);

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(abort_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromInteropPolicy(bug_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromInteropPolicy(warn_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(unknown_policy));

    try std.testing.expect(panic_policy.recognizesInteropPolicy(abort_policy));
    try std.testing.expect(panic_policy.recognizesInteropPolicy(bug_policy));
    try std.testing.expect(panic_policy.recognizesInteropPolicy(warn_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(unknown_policy));
}

test "phase3 panic policy keeps escalation and action routing aligned" {
    try std.testing.expectEqual(panic_policy.Escalation.immediate_abort, panic_policy.escalationFor(.abort));
    try std.testing.expectEqual(panic_policy.Escalation.kernel_bug, panic_policy.escalationFor(.bug));
    try std.testing.expectEqual(panic_policy.Escalation.warning_only, panic_policy.escalationFor(.warn));

    try std.testing.expectEqual(panic_policy.Action.abort_now, panic_policy.actionFor(.abort));
    try std.testing.expectEqual(panic_policy.Action.bug_check, panic_policy.actionFor(.bug));
    try std.testing.expectEqual(panic_policy.Action.warn_and_return, panic_policy.actionFor(.warn));

    try std.testing.expect(panic_policy.causesImmediateHaltByte(abi.PANIC_ABORT));
    try std.testing.expect(panic_policy.causesImmediateHaltByte(abi.PANIC_BUG));
    try std.testing.expect(!panic_policy.causesImmediateHaltByte(abi.PANIC_WARN));
    try std.testing.expect(!panic_policy.causesImmediateHaltByte(0x40));

    try std.testing.expect(!panic_policy.emitsKernelBugByte(abi.PANIC_ABORT));
    try std.testing.expect(panic_policy.emitsKernelBugByte(abi.PANIC_BUG));
    try std.testing.expect(!panic_policy.emitsKernelBugByte(abi.PANIC_WARN));

    try std.testing.expect(!panic_policy.permitsWarningOnlyContinuationByte(abi.PANIC_ABORT));
    try std.testing.expect(!panic_policy.permitsWarningOnlyContinuationByte(abi.PANIC_BUG));
    try std.testing.expect(panic_policy.permitsWarningOnlyContinuationByte(abi.PANIC_WARN));

    try std.testing.expect(!panic_policy.canReturnByte(abi.PANIC_ABORT));
    try std.testing.expect(!panic_policy.canReturnByte(abi.PANIC_BUG));
    try std.testing.expect(panic_policy.canReturnByte(abi.PANIC_WARN));
}

test "phase3 panic policy reports require-helper mismatch errors explicitly" {
    const abort_policy = policy(abi.PANIC_ABORT, 0, 0, 0);
    const bug_policy = policy(abi.PANIC_BUG, 1, 1, 0);
    const warn_policy = policy(abi.PANIC_WARN, 2, 2, 0);
    const reserved_warn = policy(abi.PANIC_WARN, 2, 2, 1);

    try panic_policy.requireEscalationInteropPolicy(abort_policy, .immediate_abort);
    try panic_policy.requireEscalationInteropPolicy(bug_policy, .kernel_bug);
    try panic_policy.requireEscalationInteropPolicy(warn_policy, .warning_only);
    try std.testing.expectError(
        error.UnexpectedEscalation,
        panic_policy.requireEscalationInteropPolicy(bug_policy, .warning_only),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireEscalationInteropPolicy(reserved_warn, .warning_only),
    );

    try panic_policy.requireActionInteropPolicy(abort_policy, .abort_now);
    try panic_policy.requireActionInteropPolicy(bug_policy, .bug_check);
    try panic_policy.requireActionInteropPolicy(warn_policy, .warn_and_return);
    try std.testing.expectError(
        error.UnexpectedAction,
        panic_policy.requireActionInteropPolicy(warn_policy, .bug_check),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireActionInteropPolicy(reserved_warn, .warn_and_return),
    );
}
