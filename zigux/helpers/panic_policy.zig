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
    const warn_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 1,
        .unsafe_scope = 1,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 1,
        .unsafe_scope = 1,
        .reserved = 1,
    };

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), modeFromInteropPolicy(abort_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), modeFromInteropPolicy(warn_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?Action, .abort_now), actionForInteropPolicy(abort_policy));
    try std.testing.expectEqual(@as(?Action, .warn_and_return), actionForInteropPolicy(warn_policy));
    try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicy(reserved_policy));

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
    try std.testing.expect(canReturnInteropPolicy(warn_policy));
    try std.testing.expect(!canReturnInteropPolicy(reserved_policy));
}
