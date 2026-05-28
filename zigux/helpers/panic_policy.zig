const std = @import("std");
const abi = @import("abi_bindings");

pub const Escalation = enum {
    immediate_abort,
    kernel_bug,
    warning_only,
};

pub const Action = enum {
    abort_now,
    bug_check,
    warn_and_return,
};

pub const EscalationError = error{
    InvalidInteropPolicy,
    UnexpectedEscalation,
};

pub const ActionError = error{
    InvalidInteropPolicy,
    UnexpectedAction,
};

pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.PanicMode {
    if (reserved != 0) return null;
    return switch (mode) {
        @intFromEnum(abi.PanicMode.abort) => .abort,
        @intFromEnum(abi.PanicMode.bug) => .bug,
        @intFromEnum(abi.PanicMode.warn) => .warn,
        else => null,
    };
}

pub fn modeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.PanicMode {
    return modeFromInteropPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn modeFromByte(mode: u8) ?abi.PanicMode {
    return modeFromInteropPolicyBytes(mode, 0);
}

pub fn modeFromInteropPolicyByte(mode: u8) ?abi.PanicMode {
    return modeFromInteropPolicyBytes(mode, 0);
}

pub fn recognizesInteropPolicyBytes(mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(mode, reserved) != null;
}

pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {
    return modeFromInteropPolicy(policy) != null;
}

pub fn recognizesByte(mode: u8) bool {
    return recognizesInteropPolicyBytes(mode, 0);
}

pub fn escalationFor(mode: abi.PanicMode) Escalation {
    return switch (mode) {
        .abort => .immediate_abort,
        .bug => .kernel_bug,
        .warn => .warning_only,
    };
}

pub fn actionFor(mode: abi.PanicMode) Action {
    return switch (mode) {
        .abort => .abort_now,
        .bug => .bug_check,
        .warn => .warn_and_return,
    };
}

pub fn requireEscalation(mode: abi.PanicMode, expected: Escalation) EscalationError!void {
    if (escalationFor(mode) != expected) {
        return error.UnexpectedEscalation;
    }
}

pub fn requireEscalationPolicyBytes(
    mode: u8,
    reserved: u8,
    expected: Escalation,
) EscalationError!void {
    const actual = escalationFromInteropPolicyBytes(mode, reserved) orelse return error.InvalidInteropPolicy;
    if (actual != expected) {
        return error.UnexpectedEscalation;
    }
}

pub fn requireEscalationInteropPolicy(
    policy: abi.InteropPolicy,
    expected: Escalation,
) EscalationError!void {
    try requireEscalationPolicyBytes(policy.panic_mode, policy.reserved, expected);
}

pub fn requireEscalationByte(mode: u8, expected: Escalation) EscalationError!void {
    try requireEscalationPolicyBytes(mode, 0, expected);
}

pub fn requireAction(mode: abi.PanicMode, expected: Action) ActionError!void {
    if (actionFor(mode) != expected) {
        return error.UnexpectedAction;
    }
}

pub fn requireActionPolicyBytes(mode: u8, reserved: u8, expected: Action) ActionError!void {
    const actual = actionForInteropPolicyBytes(mode, reserved) orelse return error.InvalidInteropPolicy;
    if (actual != expected) {
        return error.UnexpectedAction;
    }
}

pub fn requireActionInteropPolicy(policy: abi.InteropPolicy, expected: Action) ActionError!void {
    try requireActionPolicyBytes(policy.panic_mode, policy.reserved, expected);
}

pub fn requireActionByte(mode: u8, expected: Action) ActionError!void {
    try requireActionPolicyBytes(mode, 0, expected);
}

pub fn escalationFromInteropPolicyBytes(mode: u8, reserved: u8) ?Escalation {
    return escalationFor(modeFromInteropPolicyBytes(mode, reserved) orelse return null);
}

pub fn escalationFromInteropPolicy(policy: abi.InteropPolicy) ?Escalation {
    return escalationFromInteropPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn escalationFromByte(mode: u8) ?Escalation {
    return escalationFromInteropPolicyBytes(mode, 0);
}

pub fn actionForInteropPolicyBytes(mode: u8, reserved: u8) ?Action {
    return actionFor(modeFromInteropPolicyBytes(mode, reserved) orelse return null);
}

pub fn actionForInteropPolicy(policy: abi.InteropPolicy) ?Action {
    return actionForInteropPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn actionForByte(mode: u8) ?Action {
    return actionForInteropPolicyBytes(mode, 0);
}

pub fn causesImmediateHalt(mode: abi.PanicMode) bool {
    return switch (escalationFor(mode)) {
        .immediate_abort, .kernel_bug => true,
        .warning_only => false,
    };
}

pub fn emitsKernelBug(mode: abi.PanicMode) bool {
    return escalationFor(mode) == .kernel_bug;
}

pub fn permitsWarningOnlyContinuation(mode: abi.PanicMode) bool {
    return escalationFor(mode) == .warning_only;
}

pub fn canReturn(mode: abi.PanicMode) bool {
    return actionFor(mode) == .warn_and_return;
}

pub fn causesImmediateHaltPolicyBytes(mode: u8, reserved: u8) bool {
    return causesImmediateHalt(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn causesImmediateHaltInteropPolicy(policy: abi.InteropPolicy) bool {
    return causesImmediateHaltPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn causesImmediateHaltByte(mode: u8) bool {
    return causesImmediateHaltPolicyBytes(mode, 0);
}

pub fn emitsKernelBugPolicyBytes(mode: u8, reserved: u8) bool {
    return emitsKernelBug(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn emitsKernelBugInteropPolicy(policy: abi.InteropPolicy) bool {
    return emitsKernelBugPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn emitsKernelBugByte(mode: u8) bool {
    return emitsKernelBugPolicyBytes(mode, 0);
}

pub fn permitsWarningOnlyContinuationPolicyBytes(mode: u8, reserved: u8) bool {
    return permitsWarningOnlyContinuation(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn permitsWarningOnlyContinuationInteropPolicy(policy: abi.InteropPolicy) bool {
    return permitsWarningOnlyContinuationPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn permitsWarningOnlyContinuationByte(mode: u8) bool {
    return permitsWarningOnlyContinuationPolicyBytes(mode, 0);
}

pub fn canReturnInteropPolicyBytes(mode: u8, reserved: u8) bool {
    return canReturn(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn canReturnInteropPolicy(policy: abi.InteropPolicy) bool {
    return canReturnInteropPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn canReturnByte(mode: u8) bool {
    return canReturnInteropPolicyBytes(mode, 0);
}

test "phase3 panic policy keeps escalation explicit" {
    try std.testing.expectEqual(Escalation.immediate_abort, escalationFor(.abort));
    try std.testing.expectEqual(Escalation.kernel_bug, escalationFor(.bug));
    try std.testing.expectEqual(Escalation.warning_only, escalationFor(.warn));

    try std.testing.expectEqual(Action.abort_now, actionFor(.abort));
    try std.testing.expectEqual(Action.bug_check, actionFor(.bug));
    try std.testing.expectEqual(Action.warn_and_return, actionFor(.warn));

    try std.testing.expect(causesImmediateHalt(.abort));
    try std.testing.expect(causesImmediateHalt(.bug));
    try std.testing.expect(!causesImmediateHalt(.warn));

    try std.testing.expect(!emitsKernelBug(.abort));
    try std.testing.expect(emitsKernelBug(.bug));
    try std.testing.expect(!emitsKernelBug(.warn));

    try std.testing.expect(!permitsWarningOnlyContinuation(.abort));
    try std.testing.expect(!permitsWarningOnlyContinuation(.bug));
    try std.testing.expect(permitsWarningOnlyContinuation(.warn));

    try std.testing.expect(!canReturn(.abort));
    try std.testing.expect(!canReturn(.bug));
    try std.testing.expect(canReturn(.warn));
}

test "phase3 panic policy keeps require helpers explicit" {
    const abort_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const bug_policy = abi.InteropPolicy{
        .panic_mode = 1,
        .allocator_mode = 1,
        .unsafe_scope = 1,
        .reserved = 0,
    };
    const warn_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 2,
        .unsafe_scope = 2,
        .reserved = 0,
    };

    try requireEscalation(.abort, .immediate_abort);
    try requireEscalation(.bug, .kernel_bug);
    try requireEscalation(.warn, .warning_only);
    try std.testing.expectError(error.UnexpectedEscalation, requireEscalation(.warn, .kernel_bug));

    try requireEscalationByte(0, .immediate_abort);
    try requireEscalationByte(1, .kernel_bug);
    try requireEscalationByte(2, .warning_only);
    try std.testing.expectError(error.UnexpectedEscalation, requireEscalationByte(2, .kernel_bug));
    try std.testing.expectError(error.InvalidInteropPolicy, requireEscalationByte(9, .warning_only));

    try requireEscalationPolicyBytes(0, 0, .immediate_abort);
    try requireEscalationPolicyBytes(1, 0, .kernel_bug);
    try requireEscalationPolicyBytes(2, 0, .warning_only);
    try std.testing.expectError(error.UnexpectedEscalation, requireEscalationPolicyBytes(1, 0, .warning_only));
    try std.testing.expectError(error.InvalidInteropPolicy, requireEscalationPolicyBytes(2, 1, .warning_only));

    try requireEscalationInteropPolicy(abort_policy, .immediate_abort);
    try requireEscalationInteropPolicy(bug_policy, .kernel_bug);
    try requireEscalationInteropPolicy(warn_policy, .warning_only);
    try std.testing.expectError(error.UnexpectedEscalation, requireEscalationInteropPolicy(abort_policy, .warning_only));

    try requireAction(.abort, .abort_now);
    try requireAction(.bug, .bug_check);
    try requireAction(.warn, .warn_and_return);
    try std.testing.expectError(error.UnexpectedAction, requireAction(.bug, .warn_and_return));

    try requireActionByte(0, .abort_now);
    try requireActionByte(1, .bug_check);
    try requireActionByte(2, .warn_and_return);
    try std.testing.expectError(error.UnexpectedAction, requireActionByte(1, .abort_now));
    try std.testing.expectError(error.InvalidInteropPolicy, requireActionByte(9, .bug_check));

    try requireActionPolicyBytes(0, 0, .abort_now);
    try requireActionPolicyBytes(1, 0, .bug_check);
    try requireActionPolicyBytes(2, 0, .warn_and_return);
    try std.testing.expectError(error.UnexpectedAction, requireActionPolicyBytes(2, 0, .bug_check));
    try std.testing.expectError(error.InvalidInteropPolicy, requireActionPolicyBytes(2, 1, .warn_and_return));

    try requireActionInteropPolicy(abort_policy, .abort_now);
    try requireActionInteropPolicy(bug_policy, .bug_check);
    try requireActionInteropPolicy(warn_policy, .warn_and_return);
    try std.testing.expectError(error.UnexpectedAction, requireActionInteropPolicy(warn_policy, .bug_check));
}

test "phase3 panic policy stays explicit" {
    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromByte(9));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), modeFromInteropPolicyByte(2));

    try std.testing.expectEqual(@as(?Escalation, .immediate_abort), escalationFromByte(0));
    try std.testing.expectEqual(@as(?Escalation, .kernel_bug), escalationFromByte(1));
    try std.testing.expectEqual(@as(?Escalation, .warning_only), escalationFromByte(2));
    try std.testing.expectEqual(@as(?Escalation, null), escalationFromByte(9));

    try std.testing.expectEqual(@as(?Action, .abort_now), actionForByte(0));
    try std.testing.expectEqual(@as(?Action, .bug_check), actionForByte(1));
    try std.testing.expectEqual(@as(?Action, .warn_and_return), actionForByte(2));
    try std.testing.expectEqual(@as(?Action, null), actionForByte(9));

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), modeFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), modeFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), modeFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicyBytes(2, 1));

    try std.testing.expectEqual(@as(?Escalation, .immediate_abort), escalationFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?Escalation, .kernel_bug), escalationFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?Escalation, .warning_only), escalationFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?Escalation, null), escalationFromInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?Escalation, null), escalationFromInteropPolicyBytes(2, 1));

    try std.testing.expectEqual(@as(?Action, .abort_now), actionForInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?Action, .bug_check), actionForInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?Action, .warn_and_return), actionForInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicyBytes(2, 1));

    try std.testing.expect(recognizesInteropPolicyBytes(0, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(1, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(2, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(9, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(2, 1));

    try std.testing.expect(recognizesByte(0));
    try std.testing.expect(recognizesByte(1));
    try std.testing.expect(recognizesByte(2));
    try std.testing.expect(!recognizesByte(9));

    const abort_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const bug_policy = abi.InteropPolicy{
        .panic_mode = 1,
        .allocator_mode = 1,
        .unsafe_scope = 1,
        .reserved = 0,
    };
    const warn_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 2,
        .unsafe_scope = 2,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 2,
        .unsafe_scope = 2,
        .reserved = 1,
    };
    const unknown_policy = abi.InteropPolicy{
        .panic_mode = 9,
        .allocator_mode = 0,
        .unsafe_scope = 0,
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), modeFromInteropPolicy(abort_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), modeFromInteropPolicy(bug_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), modeFromInteropPolicy(warn_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicy(unknown_policy));

    try std.testing.expectEqual(@as(?Escalation, .immediate_abort), escalationFromInteropPolicy(abort_policy));
    try std.testing.expectEqual(@as(?Escalation, .kernel_bug), escalationFromInteropPolicy(bug_policy));
    try std.testing.expectEqual(@as(?Escalation, .warning_only), escalationFromInteropPolicy(warn_policy));
    try std.testing.expectEqual(@as(?Escalation, null), escalationFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?Escalation, null), escalationFromInteropPolicy(unknown_policy));

    try std.testing.expectEqual(@as(?Action, .abort_now), actionForInteropPolicy(abort_policy));
    try std.testing.expectEqual(@as(?Action, .bug_check), actionForInteropPolicy(bug_policy));
    try std.testing.expectEqual(@as(?Action, .warn_and_return), actionForInteropPolicy(warn_policy));
    try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicy(unknown_policy));

    try std.testing.expect(recognizesInteropPolicy(abort_policy));
    try std.testing.expect(recognizesInteropPolicy(bug_policy));
    try std.testing.expect(recognizesInteropPolicy(warn_policy));
    try std.testing.expect(!recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!recognizesInteropPolicy(unknown_policy));

    try std.testing.expect(causesImmediateHaltByte(0));
    try std.testing.expect(causesImmediateHaltByte(1));
    try std.testing.expect(!causesImmediateHaltByte(2));
    try std.testing.expect(!causesImmediateHaltByte(9));

    try std.testing.expect(causesImmediateHaltPolicyBytes(0, 0));
    try std.testing.expect(causesImmediateHaltPolicyBytes(1, 0));
    try std.testing.expect(!causesImmediateHaltPolicyBytes(2, 0));
    try std.testing.expect(!causesImmediateHaltPolicyBytes(2, 1));

    try std.testing.expect(causesImmediateHaltInteropPolicy(abort_policy));
    try std.testing.expect(causesImmediateHaltInteropPolicy(bug_policy));
    try std.testing.expect(!causesImmediateHaltInteropPolicy(warn_policy));
    try std.testing.expect(!causesImmediateHaltInteropPolicy(reserved_policy));
    try std.testing.expect(!causesImmediateHaltInteropPolicy(unknown_policy));

    try std.testing.expect(!emitsKernelBugByte(0));
    try std.testing.expect(emitsKernelBugByte(1));
    try std.testing.expect(!emitsKernelBugByte(2));
    try std.testing.expect(!emitsKernelBugByte(9));

    try std.testing.expect(!emitsKernelBugPolicyBytes(0, 0));
    try std.testing.expect(emitsKernelBugPolicyBytes(1, 0));
    try std.testing.expect(!emitsKernelBugPolicyBytes(2, 0));
    try std.testing.expect(!emitsKernelBugPolicyBytes(2, 1));

    try std.testing.expect(!emitsKernelBugInteropPolicy(abort_policy));
    try std.testing.expect(emitsKernelBugInteropPolicy(bug_policy));
    try std.testing.expect(!emitsKernelBugInteropPolicy(warn_policy));
    try std.testing.expect(!emitsKernelBugInteropPolicy(reserved_policy));
    try std.testing.expect(!emitsKernelBugInteropPolicy(unknown_policy));

    try std.testing.expect(!permitsWarningOnlyContinuationByte(0));
    try std.testing.expect(!permitsWarningOnlyContinuationByte(1));
    try std.testing.expect(permitsWarningOnlyContinuationByte(2));
    try std.testing.expect(!permitsWarningOnlyContinuationByte(9));

    try std.testing.expect(!permitsWarningOnlyContinuationPolicyBytes(0, 0));
    try std.testing.expect(!permitsWarningOnlyContinuationPolicyBytes(1, 0));
    try std.testing.expect(permitsWarningOnlyContinuationPolicyBytes(2, 0));
    try std.testing.expect(!permitsWarningOnlyContinuationPolicyBytes(2, 1));

    try std.testing.expect(!permitsWarningOnlyContinuationInteropPolicy(abort_policy));
    try std.testing.expect(!permitsWarningOnlyContinuationInteropPolicy(bug_policy));
    try std.testing.expect(permitsWarningOnlyContinuationInteropPolicy(warn_policy));
    try std.testing.expect(!permitsWarningOnlyContinuationInteropPolicy(reserved_policy));
    try std.testing.expect(!permitsWarningOnlyContinuationInteropPolicy(unknown_policy));

    try std.testing.expect(!canReturnByte(0));
    try std.testing.expect(!canReturnByte(1));
    try std.testing.expect(canReturnByte(2));
    try std.testing.expect(!canReturnByte(9));

    try std.testing.expect(!canReturnInteropPolicy(abort_policy));
    try std.testing.expect(!canReturnInteropPolicy(bug_policy));
    try std.testing.expect(canReturnInteropPolicy(warn_policy));
    try std.testing.expect(!canReturnInteropPolicy(reserved_policy));
    try std.testing.expect(!canReturnInteropPolicy(unknown_policy));
}
