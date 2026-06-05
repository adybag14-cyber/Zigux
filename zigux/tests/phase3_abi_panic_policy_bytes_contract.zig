const std = @import("std");

const abi = @import("abi_bindings");
const panic_policy = @import("panic_policy");

test "phase3 panic policy rejects reserved interop-policy bytes before mapping modes" {
    const abort_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_ABORT,
        .allocator_mode = abi.ALLOC_CALLER_PROVIDED,
        .unsafe_scope = abi.UNSAFE_NONE,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_ABORT,
        .allocator_mode = abi.ALLOC_CALLER_PROVIDED,
        .unsafe_scope = abi.UNSAFE_NONE,
        .reserved = 1,
    };

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(abort_policy));
    try std.testing.expect(panic_policy.recognizesInteropPolicy(abort_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForInteropPolicy(reserved_policy));
}

test "phase3 panic policy keeps ABI byte aliases aligned with actions" {
    const cases = [_]struct {
        mode: u8,
        panic_mode: abi.PanicMode,
        action: panic_policy.Action,
        can_return: bool,
    }{
        .{
            .mode = abi.PANIC_ABORT,
            .panic_mode = .abort,
            .action = .abort_now,
            .can_return = false,
        },
        .{
            .mode = abi.PANIC_BUG,
            .panic_mode = .bug,
            .action = .bug_check,
            .can_return = false,
        },
        .{
            .mode = abi.PANIC_WARN,
            .panic_mode = .warn,
            .action = .warn_and_return,
            .can_return = true,
        },
    };

    for (cases) |case| {
        try std.testing.expectEqual(@as(?abi.PanicMode, case.panic_mode), panic_policy.modeFromByte(case.mode));
        try std.testing.expectEqual(@as(?panic_policy.Action, case.action), panic_policy.actionForByte(case.mode));
        try std.testing.expectEqual(case.can_return, panic_policy.canReturnByte(case.mode));
    }
}

test "phase3 panic policy rejects invalid ABI bytes without widening actions" {
    const invalid_mode: u8 = 0xff;

    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromByte(invalid_mode));
    try std.testing.expect(!panic_policy.recognizesByte(invalid_mode));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForByte(invalid_mode));
    try std.testing.expect(!panic_policy.canReturnByte(invalid_mode));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicyBytes(abi.PANIC_WARN, 9));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForInteropPolicyBytes(abi.PANIC_WARN, 9));
    try std.testing.expect(!panic_policy.canReturnInteropPolicyBytes(abi.PANIC_WARN, 9));
}
