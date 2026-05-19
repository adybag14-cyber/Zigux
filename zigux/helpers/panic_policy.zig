const std = @import("std");
const abi = @import("abi_bindings");

pub const Escalation = enum {
    immediate_abort,
    kernel_bug,
    warning_only,
};

pub const PanicPolicyError = error{UnexpectedEscalation};

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

pub fn escalationFromInteropPolicyBytes(mode: u8, reserved: u8) ?Escalation {
    return escalationFor(modeFromInteropPolicyBytes(mode, reserved) orelse return null);
}

pub fn escalationFromInteropPolicy(policy: abi.InteropPolicy) ?Escalation {
    return escalationFromInteropPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn escalationFromByte(mode: u8) ?Escalation {
    return escalationFromInteropPolicyBytes(mode, 0);
}

pub fn causesImmediateHalt(mode: abi.PanicMode) bool {
    return switch (escalationFor(mode)) {
        .immediate_abort, .kernel_bug => true,
        .warning_only => false,
    };
}

pub fn emitsImmediateAbort(mode: abi.PanicMode) bool {
    return escalationFor(mode) == .immediate_abort;
}

pub fn emitsKernelBug(mode: abi.PanicMode) bool {
    return escalationFor(mode) == .kernel_bug;
}

pub fn permitsWarningOnlyContinuation(mode: abi.PanicMode) bool {
    return escalationFor(mode) == .warning_only;
}

pub fn requireImmediateHalt(mode: abi.PanicMode) PanicPolicyError!void {
    if (!causesImmediateHalt(mode)) return error.UnexpectedEscalation;
}

pub fn requireImmediateAbort(mode: abi.PanicMode) PanicPolicyError!void {
    if (!emitsImmediateAbort(mode)) return error.UnexpectedEscalation;
}

pub fn requireKernelBug(mode: abi.PanicMode) PanicPolicyError!void {
    if (!emitsKernelBug(mode)) return error.UnexpectedEscalation;
}

pub fn requireWarningOnlyContinuation(mode: abi.PanicMode) PanicPolicyError!void {
    if (!permitsWarningOnlyContinuation(mode)) return error.UnexpectedEscalation;
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

pub fn requireImmediateHaltPolicyBytes(mode: u8, reserved: u8) PanicPolicyError!void {
    return requireImmediateHalt(modeFromInteropPolicyBytes(mode, reserved) orelse return error.UnexpectedEscalation);
}

pub fn requireImmediateHaltInteropPolicy(policy: abi.InteropPolicy) PanicPolicyError!void {
    return requireImmediateHaltPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn requireImmediateHaltByte(mode: u8) PanicPolicyError!void {
    return requireImmediateHaltPolicyBytes(mode, 0);
}

pub fn emitsImmediateAbortPolicyBytes(mode: u8, reserved: u8) bool {
    return emitsImmediateAbort(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn emitsImmediateAbortInteropPolicy(policy: abi.InteropPolicy) bool {
    return emitsImmediateAbortPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn emitsImmediateAbortByte(mode: u8) bool {
    return emitsImmediateAbortPolicyBytes(mode, 0);
}

pub fn requireImmediateAbortPolicyBytes(mode: u8, reserved: u8) PanicPolicyError!void {
    return requireImmediateAbort(modeFromInteropPolicyBytes(mode, reserved) orelse return error.UnexpectedEscalation);
}

pub fn requireImmediateAbortInteropPolicy(policy: abi.InteropPolicy) PanicPolicyError!void {
    return requireImmediateAbortPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn requireImmediateAbortByte(mode: u8) PanicPolicyError!void {
    return requireImmediateAbortPolicyBytes(mode, 0);
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

pub fn requireKernelBugPolicyBytes(mode: u8, reserved: u8) PanicPolicyError!void {
    return requireKernelBug(modeFromInteropPolicyBytes(mode, reserved) orelse return error.UnexpectedEscalation);
}

pub fn requireKernelBugInteropPolicy(policy: abi.InteropPolicy) PanicPolicyError!void {
    return requireKernelBugPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn requireKernelBugByte(mode: u8) PanicPolicyError!void {
    return requireKernelBugPolicyBytes(mode, 0);
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

pub fn requireWarningOnlyContinuationPolicyBytes(mode: u8, reserved: u8) PanicPolicyError!void {
    return requireWarningOnlyContinuation(modeFromInteropPolicyBytes(mode, reserved) orelse return error.UnexpectedEscalation);
}

pub fn requireWarningOnlyContinuationInteropPolicy(policy: abi.InteropPolicy) PanicPolicyError!void {
    return requireWarningOnlyContinuationPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn requireWarningOnlyContinuationByte(mode: u8) PanicPolicyError!void {
    return requireWarningOnlyContinuationPolicyBytes(mode, 0);
}

test "phase3 panic policy keeps escalation explicit" {
    try std.testing.expectEqual(Escalation.immediate_abort, escalationFor(.abort));
    try std.testing.expectEqual(Escalation.kernel_bug, escalationFor(.bug));
    try std.testing.expectEqual(Escalation.warning_only, escalationFor(.warn));

    try std.testing.expect(causesImmediateHalt(.abort));
    try std.testing.expect(causesImmediateHalt(.bug));
    try std.testing.expect(!causesImmediateHalt(.warn));

    try std.testing.expect(emitsImmediateAbort(.abort));
    try std.testing.expect(!emitsImmediateAbort(.bug));
    try std.testing.expect(!emitsImmediateAbort(.warn));

    try std.testing.expect(!emitsKernelBug(.abort));
    try std.testing.expect(emitsKernelBug(.bug));
    try std.testing.expect(!emitsKernelBug(.warn));

    try std.testing.expect(!permitsWarningOnlyContinuation(.abort));
    try std.testing.expect(!permitsWarningOnlyContinuation(.bug));
    try std.testing.expect(permitsWarningOnlyContinuation(.warn));

    try requireImmediateHalt(.abort);
    try requireImmediateHalt(.bug);
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateHalt(.warn));

    try requireImmediateAbort(.abort);
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbort(.bug));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbort(.warn));

    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBug(.abort));
    try requireKernelBug(.bug);
    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBug(.warn));

    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuation(.abort));
    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuation(.bug));
    try requireWarningOnlyContinuation(.warn);
}

test "phase3 panic policy stays explicit" {
    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromByte(9));

    try std.testing.expectEqual(@as(?Escalation, .immediate_abort), escalationFromByte(0));
    try std.testing.expectEqual(@as(?Escalation, .kernel_bug), escalationFromByte(1));
    try std.testing.expectEqual(@as(?Escalation, .warning_only), escalationFromByte(2));
    try std.testing.expectEqual(@as(?Escalation, null), escalationFromByte(9));

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

    try std.testing.expect(recognizesInteropPolicy(abort_policy));
    try std.testing.expect(recognizesInteropPolicy(bug_policy));
    try std.testing.expect(recognizesInteropPolicy(warn_policy));
    try std.testing.expect(!recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!recognizesInteropPolicy(unknown_policy));

    try std.testing.expect(causesImmediateHaltByte(0));
    try std.testing.expect(causesImmediateHaltByte(1));
    try std.testing.expect(!causesImmediateHaltByte(2));
    try std.testing.expect(!causesImmediateHaltByte(9));
    try requireImmediateHaltByte(0);
    try requireImmediateHaltByte(1);
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateHaltByte(2));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateHaltByte(9));

    try std.testing.expect(emitsImmediateAbortByte(0));
    try std.testing.expect(!emitsImmediateAbortByte(1));
    try std.testing.expect(!emitsImmediateAbortByte(2));
    try std.testing.expect(!emitsImmediateAbortByte(9));
    try requireImmediateAbortByte(0);
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbortByte(1));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbortByte(2));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbortByte(9));

    try std.testing.expect(causesImmediateHaltPolicyBytes(0, 0));
    try std.testing.expect(causesImmediateHaltPolicyBytes(1, 0));
    try std.testing.expect(!causesImmediateHaltPolicyBytes(2, 0));
    try std.testing.expect(!causesImmediateHaltPolicyBytes(2, 1));
    try requireImmediateHaltPolicyBytes(0, 0);
    try requireImmediateHaltPolicyBytes(1, 0);
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateHaltPolicyBytes(2, 0));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateHaltPolicyBytes(2, 1));

    try std.testing.expect(emitsImmediateAbortPolicyBytes(0, 0));
    try std.testing.expect(!emitsImmediateAbortPolicyBytes(1, 0));
    try std.testing.expect(!emitsImmediateAbortPolicyBytes(2, 0));
    try std.testing.expect(!emitsImmediateAbortPolicyBytes(2, 1));
    try requireImmediateAbortPolicyBytes(0, 0);
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbortPolicyBytes(1, 0));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbortPolicyBytes(2, 0));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbortPolicyBytes(2, 1));

    try std.testing.expect(causesImmediateHaltInteropPolicy(abort_policy));
    try std.testing.expect(causesImmediateHaltInteropPolicy(bug_policy));
    try std.testing.expect(!causesImmediateHaltInteropPolicy(warn_policy));
    try std.testing.expect(!causesImmediateHaltInteropPolicy(reserved_policy));
    try std.testing.expect(!causesImmediateHaltInteropPolicy(unknown_policy));
    try requireImmediateHaltInteropPolicy(abort_policy);
    try requireImmediateHaltInteropPolicy(bug_policy);
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateHaltInteropPolicy(warn_policy));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateHaltInteropPolicy(reserved_policy));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateHaltInteropPolicy(unknown_policy));

    try std.testing.expect(emitsImmediateAbortInteropPolicy(abort_policy));
    try std.testing.expect(!emitsImmediateAbortInteropPolicy(bug_policy));
    try std.testing.expect(!emitsImmediateAbortInteropPolicy(warn_policy));
    try std.testing.expect(!emitsImmediateAbortInteropPolicy(reserved_policy));
    try std.testing.expect(!emitsImmediateAbortInteropPolicy(unknown_policy));
    try requireImmediateAbortInteropPolicy(abort_policy);
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbortInteropPolicy(bug_policy));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbortInteropPolicy(warn_policy));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbortInteropPolicy(reserved_policy));
    try std.testing.expectError(error.UnexpectedEscalation, requireImmediateAbortInteropPolicy(unknown_policy));

    try std.testing.expect(!emitsKernelBugByte(0));
    try std.testing.expect(emitsKernelBugByte(1));
    try std.testing.expect(!emitsKernelBugByte(2));
    try std.testing.expect(!emitsKernelBugByte(9));
    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBugByte(0));
    try requireKernelBugByte(1);
    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBugByte(2));
    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBugByte(9));

    try std.testing.expect(!emitsKernelBugPolicyBytes(0, 0));
    try std.testing.expect(emitsKernelBugPolicyBytes(1, 0));
    try std.testing.expect(!emitsKernelBugPolicyBytes(2, 0));
    try std.testing.expect(!emitsKernelBugPolicyBytes(2, 1));
    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBugPolicyBytes(0, 0));
    try requireKernelBugPolicyBytes(1, 0);
    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBugPolicyBytes(2, 0));
    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBugPolicyBytes(2, 1));

    try std.testing.expect(!emitsKernelBugInteropPolicy(abort_policy));
    try std.testing.expect(emitsKernelBugInteropPolicy(bug_policy));
    try std.testing.expect(!emitsKernelBugInteropPolicy(warn_policy));
    try std.testing.expect(!emitsKernelBugInteropPolicy(reserved_policy));
    try std.testing.expect(!emitsKernelBugInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBugInteropPolicy(abort_policy));
    try requireKernelBugInteropPolicy(bug_policy);
    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBugInteropPolicy(warn_policy));
    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBugInteropPolicy(reserved_policy));
    try std.testing.expectError(error.UnexpectedEscalation, requireKernelBugInteropPolicy(unknown_policy));

    try std.testing.expect(!permitsWarningOnlyContinuationByte(0));
    try std.testing.expect(!permitsWarningOnlyContinuationByte(1));
    try std.testing.expect(permitsWarningOnlyContinuationByte(2));
    try std.testing.expect(!permitsWarningOnlyContinuationByte(9));
    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuationByte(0));
    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuationByte(1));
    try requireWarningOnlyContinuationByte(2);
    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuationByte(9));

    try std.testing.expect(!permitsWarningOnlyContinuationPolicyBytes(0, 0));
    try std.testing.expect(!permitsWarningOnlyContinuationPolicyBytes(1, 0));
    try std.testing.expect(permitsWarningOnlyContinuationPolicyBytes(2, 0));
    try std.testing.expect(!permitsWarningOnlyContinuationPolicyBytes(2, 1));
    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuationPolicyBytes(0, 0));
    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuationPolicyBytes(1, 0));
    try requireWarningOnlyContinuationPolicyBytes(2, 0);
    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuationPolicyBytes(2, 1));

    try std.testing.expect(!permitsWarningOnlyContinuationInteropPolicy(abort_policy));
    try std.testing.expect(!permitsWarningOnlyContinuationInteropPolicy(bug_policy));
    try std.testing.expect(permitsWarningOnlyContinuationInteropPolicy(warn_policy));
    try std.testing.expect(!permitsWarningOnlyContinuationInteropPolicy(reserved_policy));
    try std.testing.expect(!permitsWarningOnlyContinuationInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuationInteropPolicy(abort_policy));
    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuationInteropPolicy(bug_policy));
    try requireWarningOnlyContinuationInteropPolicy(warn_policy);
    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuationInteropPolicy(reserved_policy));
    try std.testing.expectError(error.UnexpectedEscalation, requireWarningOnlyContinuationInteropPolicy(unknown_policy));
}
