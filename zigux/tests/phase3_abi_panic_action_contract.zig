const std = @import("std");
const panic_policy = @import("panic_policy");
const abi = @import("abi_bindings");

fn policy(panic_mode: u8, allocator_mode: u8, unsafe_scope: u8, reserved: u8) abi.InteropPolicy {
    return .{
        .panic_mode = panic_mode,
        .allocator_mode = allocator_mode,
        .unsafe_scope = unsafe_scope,
        .reserved = reserved,
    };
}

test "panic policy keeps action and escalation rows aligned with ABI bytes" {
    const rows = [_]struct {
        mode: abi.PanicMode,
        byte: u8,
        escalation: panic_policy.Escalation,
        action: panic_policy.Action,
        halts: bool,
        emits_bug: bool,
        warning_only: bool,
        returns: bool,
    }{
        .{ .mode = .abort, .byte = abi.PANIC_ABORT, .escalation = .immediate_abort, .action = .abort_now, .halts = true, .emits_bug = false, .warning_only = false, .returns = false },
        .{ .mode = .bug, .byte = abi.PANIC_BUG, .escalation = .kernel_bug, .action = .bug_check, .halts = true, .emits_bug = true, .warning_only = false, .returns = false },
        .{ .mode = .warn, .byte = abi.PANIC_WARN, .escalation = .warning_only, .action = .warn_and_return, .halts = false, .emits_bug = false, .warning_only = true, .returns = true },
    };

    for (rows) |row| {
        const current = policy(row.byte, abi.ALLOC_KERNEL_HEAP, abi.UNSAFE_VOLATILE_MMIO, 0);

        try std.testing.expectEqual(row.escalation, panic_policy.escalationFor(row.mode));
        try std.testing.expectEqual(row.action, panic_policy.actionFor(row.mode));
        try std.testing.expectEqual(row.escalation, panic_policy.escalationFromByte(row.byte).?);
        try std.testing.expectEqual(row.action, panic_policy.actionForByte(row.byte).?);
        try std.testing.expectEqual(row.escalation, panic_policy.escalationFromInteropPolicy(current).?);
        try std.testing.expectEqual(row.action, panic_policy.actionForInteropPolicy(current).?);

        try std.testing.expectEqual(row.halts, panic_policy.causesImmediateHalt(row.mode));
        try std.testing.expectEqual(row.halts, panic_policy.causesImmediateHaltByte(row.byte));
        try std.testing.expectEqual(row.halts, panic_policy.causesImmediateHaltInteropPolicy(current));
        try std.testing.expectEqual(row.emits_bug, panic_policy.emitsKernelBug(row.mode));
        try std.testing.expectEqual(row.emits_bug, panic_policy.emitsKernelBugByte(row.byte));
        try std.testing.expectEqual(row.emits_bug, panic_policy.emitsKernelBugInteropPolicy(current));
        try std.testing.expectEqual(row.warning_only, panic_policy.permitsWarningOnlyContinuation(row.mode));
        try std.testing.expectEqual(row.warning_only, panic_policy.permitsWarningOnlyContinuationByte(row.byte));
        try std.testing.expectEqual(row.warning_only, panic_policy.permitsWarningOnlyContinuationInteropPolicy(current));
        try std.testing.expectEqual(row.returns, panic_policy.canReturn(row.mode));
        try std.testing.expectEqual(row.returns, panic_policy.canReturnByte(row.byte));
        try std.testing.expectEqual(row.returns, panic_policy.canReturnInteropPolicy(current));
    }
}

test "panic policy require helpers reject mismatched expected actions" {
    try panic_policy.requireEscalation(.abort, .immediate_abort);
    try panic_policy.requireEscalation(.bug, .kernel_bug);
    try panic_policy.requireEscalation(.warn, .warning_only);
    try std.testing.expectError(error.UnexpectedEscalation, panic_policy.requireEscalation(.warn, .kernel_bug));

    try panic_policy.requireAction(.abort, .abort_now);
    try panic_policy.requireAction(.bug, .bug_check);
    try panic_policy.requireAction(.warn, .warn_and_return);
    try std.testing.expectError(error.UnexpectedAction, panic_policy.requireAction(.bug, .warn_and_return));
}

test "panic policy fail-closes unknown and reserved interop policy bytes" {
    const reserved = policy(abi.PANIC_WARN, abi.ALLOC_ARENA, abi.UNSAFE_RAW_POINTER_BRIDGE, 1);
    const unknown = policy(9, abi.ALLOC_CALLER_PROVIDED, abi.UNSAFE_NONE, 0);

    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, null), panic_policy.escalationFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForInteropPolicy(reserved));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(reserved));
    try std.testing.expect(!panic_policy.causesImmediateHaltInteropPolicy(reserved));
    try std.testing.expect(!panic_policy.emitsKernelBugInteropPolicy(reserved));
    try std.testing.expect(!panic_policy.permitsWarningOnlyContinuationInteropPolicy(reserved));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(reserved));

    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(unknown));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, null), panic_policy.escalationFromInteropPolicy(unknown));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForInteropPolicy(unknown));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(unknown));
}

test "panic policy require helpers fail closed on invalid policy bytes" {
    try panic_policy.requireEscalationPolicyBytes(abi.PANIC_ABORT, 0, .immediate_abort);
    try panic_policy.requireActionPolicyBytes(abi.PANIC_WARN, 0, .warn_and_return);

    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireEscalationPolicyBytes(abi.PANIC_WARN, 1, .warning_only),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireEscalationByte(9, .warning_only),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireActionPolicyBytes(abi.PANIC_BUG, 1, .bug_check),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireActionByte(9, .bug_check),
    );
}
