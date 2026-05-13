const std = @import("std");
const abi = @import("abi_bindings");

pub const Action = enum {
    abort_now,
    bug_check,
    warn_and_return,
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

pub fn recognizesInteropPolicyBytes(mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(mode, reserved) != null;
}

pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {
    return modeFromInteropPolicy(policy) != null;
}

pub fn recognizesByte(mode: u8) bool {
    return recognizesInteropPolicyBytes(mode, 0);
}

pub fn actionFor(mode: abi.PanicMode) Action {
    return switch (mode) {
        .abort => .abort_now,
        .bug => .bug_check,
        .warn => .warn_and_return,
    };
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

pub fn mustAbort(mode: abi.PanicMode) bool {
    return actionFor(mode) == .abort_now;
}

pub fn mustAbortInteropPolicyBytes(mode: u8, reserved: u8) bool {
    return actionForInteropPolicyBytes(mode, reserved) == .abort_now;
}

pub fn mustAbortInteropPolicy(policy: abi.InteropPolicy) bool {
    return mustAbortInteropPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn mustAbortByte(mode: u8) bool {
    return mustAbortInteropPolicyBytes(mode, 0);
}

pub fn mustBugCheck(mode: abi.PanicMode) bool {
    return actionFor(mode) == .bug_check;
}

pub fn mustBugCheckInteropPolicyBytes(mode: u8, reserved: u8) bool {
    return actionForInteropPolicyBytes(mode, reserved) == .bug_check;
}

pub fn mustBugCheckInteropPolicy(policy: abi.InteropPolicy) bool {
    return mustBugCheckInteropPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn mustBugCheckByte(mode: u8) bool {
    return mustBugCheckInteropPolicyBytes(mode, 0);
}

pub fn canReturn(mode: abi.PanicMode) bool {
    return actionFor(mode) == .warn_and_return;
}

pub fn canReturnInteropPolicyBytes(mode: u8, reserved: u8) bool {
    return actionForInteropPolicyBytes(mode, reserved) == .warn_and_return;
}

pub fn canReturnInteropPolicy(policy: abi.InteropPolicy) bool {
    return canReturnInteropPolicyBytes(policy.panic_mode, policy.reserved);
}

pub fn canReturnByte(mode: u8) bool {
    return canReturnInteropPolicyBytes(mode, 0);
}

test "phase3 panic policy stays explicit" {
    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromByte(9));

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), modeFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), modeFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), modeFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicyBytes(2, 1));

    try std.testing.expect(recognizesByte(0));
    try std.testing.expect(recognizesByte(1));
    try std.testing.expect(recognizesByte(2));
    try std.testing.expect(!recognizesByte(9));

    try std.testing.expect(recognizesInteropPolicyBytes(0, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(1, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(2, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(9, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(2, 1));

    try std.testing.expectEqual(@as(?Action, .abort_now), actionForByte(0));
    try std.testing.expectEqual(@as(?Action, .bug_check), actionForByte(1));
    try std.testing.expectEqual(@as(?Action, .warn_and_return), actionForByte(2));
    try std.testing.expectEqual(@as(?Action, null), actionForByte(9));

    try std.testing.expectEqual(@as(?Action, .abort_now), actionForInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?Action, .bug_check), actionForInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?Action, .warn_and_return), actionForInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicyBytes(2, 1));

    const abort_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const bug_policy = abi.InteropPolicy{
        .panic_mode = 1,
        .allocator_mode = 0,
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const warn_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 1,
        .unsafe_scope = 1,
        .reserved = 0,
    };
    const unknown_policy = abi.InteropPolicy{
        .panic_mode = 9,
        .allocator_mode = 0,
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 1,
        .unsafe_scope = 1,
        .reserved = 1,
    };

    try std.testing.expect(recognizesInteropPolicy(abort_policy));
    try std.testing.expect(recognizesInteropPolicy(bug_policy));
    try std.testing.expect(recognizesInteropPolicy(warn_policy));
    try std.testing.expect(!recognizesInteropPolicy(unknown_policy));
    try std.testing.expect(!recognizesInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), modeFromInteropPolicy(abort_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), modeFromInteropPolicy(bug_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), modeFromInteropPolicy(warn_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?Action, .abort_now), actionForInteropPolicy(abort_policy));
    try std.testing.expectEqual(@as(?Action, .bug_check), actionForInteropPolicy(bug_policy));
    try std.testing.expectEqual(@as(?Action, .warn_and_return), actionForInteropPolicy(warn_policy));
    try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicy(reserved_policy));

    try std.testing.expect(mustAbort(.abort));
    try std.testing.expect(!mustAbort(.bug));
    try std.testing.expect(!mustAbort(.warn));
    try std.testing.expect(mustAbortByte(0));
    try std.testing.expect(!mustAbortByte(1));
    try std.testing.expect(!mustAbortByte(2));
    try std.testing.expect(!mustAbortByte(9));
    try std.testing.expect(mustAbortInteropPolicyBytes(0, 0));
    try std.testing.expect(!mustAbortInteropPolicyBytes(1, 0));
    try std.testing.expect(!mustAbortInteropPolicyBytes(2, 0));
    try std.testing.expect(!mustAbortInteropPolicyBytes(9, 0));
    try std.testing.expect(!mustAbortInteropPolicyBytes(0, 1));
    try std.testing.expect(mustAbortInteropPolicy(abort_policy));
    try std.testing.expect(!mustAbortInteropPolicy(bug_policy));
    try std.testing.expect(!mustAbortInteropPolicy(warn_policy));
    try std.testing.expect(!mustAbortInteropPolicy(unknown_policy));
    try std.testing.expect(!mustAbortInteropPolicy(reserved_policy));

    try std.testing.expect(!mustBugCheck(.abort));
    try std.testing.expect(mustBugCheck(.bug));
    try std.testing.expect(!mustBugCheck(.warn));
    try std.testing.expect(!mustBugCheckByte(0));
    try std.testing.expect(mustBugCheckByte(1));
    try std.testing.expect(!mustBugCheckByte(2));
    try std.testing.expect(!mustBugCheckByte(9));
    try std.testing.expect(!mustBugCheckInteropPolicyBytes(0, 0));
    try std.testing.expect(mustBugCheckInteropPolicyBytes(1, 0));
    try std.testing.expect(!mustBugCheckInteropPolicyBytes(2, 0));
    try std.testing.expect(!mustBugCheckInteropPolicyBytes(9, 0));
    try std.testing.expect(!mustBugCheckInteropPolicyBytes(1, 1));
    try std.testing.expect(!mustBugCheckInteropPolicy(abort_policy));
    try std.testing.expect(mustBugCheckInteropPolicy(bug_policy));
    try std.testing.expect(!mustBugCheckInteropPolicy(warn_policy));
    try std.testing.expect(!mustBugCheckInteropPolicy(unknown_policy));
    try std.testing.expect(!mustBugCheckInteropPolicy(reserved_policy));

    try std.testing.expect(!canReturn(.abort));
    try std.testing.expect(!canReturn(.bug));
    try std.testing.expect(canReturn(.warn));
    try std.testing.expect(!canReturnByte(0));
    try std.testing.expect(!canReturnByte(1));
    try std.testing.expect(canReturnByte(2));
    try std.testing.expect(!canReturnByte(9));
    try std.testing.expect(!canReturnInteropPolicyBytes(0, 0));
    try std.testing.expect(!canReturnInteropPolicyBytes(1, 0));
    try std.testing.expect(canReturnInteropPolicyBytes(2, 0));
    try std.testing.expect(!canReturnInteropPolicyBytes(9, 0));
    try std.testing.expect(!canReturnInteropPolicyBytes(2, 1));
    try std.testing.expect(!canReturnInteropPolicy(abort_policy));
    try std.testing.expect(!canReturnInteropPolicy(bug_policy));
    try std.testing.expect(canReturnInteropPolicy(warn_policy));
    try std.testing.expect(!canReturnInteropPolicy(unknown_policy));
    try std.testing.expect(!canReturnInteropPolicy(reserved_policy));
}
