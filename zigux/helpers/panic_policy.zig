const std = @import("std");
const abi = @import("abi_bindings");

pub const Action = enum {
    abort_now,
    bug_check,
    warn_and_return,
};

pub fn actionFor(mode: abi.PanicMode) Action {
    return switch (mode) {
        .abort => .abort_now,
        .bug => .bug_check,
        .warn => .warn_and_return,
    };
}

pub fn modeFromInteropPolicyByte(panic_mode: u8) ?abi.PanicMode {
    return switch (panic_mode) {
        @intFromEnum(abi.PanicMode.abort) => .abort,
        @intFromEnum(abi.PanicMode.bug) => .bug,
        @intFromEnum(abi.PanicMode.warn) => .warn,
        else => null,
    };
}

pub fn recognizesInteropPolicyByte(panic_mode: u8) bool {
    return modeFromInteropPolicyByte(panic_mode) != null;
}

pub fn canReturn(mode: abi.PanicMode) bool {
    return actionFor(mode) == .warn_and_return;
}

pub fn canReturnPolicyByte(panic_mode: u8) bool {
    return canReturn(modeFromInteropPolicyByte(panic_mode) orelse return false);
}

test "phase3 panic policy stays explicit" {
    try std.testing.expectEqual(Action.abort_now, actionFor(.abort));
    try std.testing.expectEqual(Action.bug_check, actionFor(.bug));
    try std.testing.expectEqual(Action.warn_and_return, actionFor(.warn));
    try std.testing.expect(!canReturn(.abort));
    try std.testing.expect(!canReturn(.bug));
    try std.testing.expect(canReturn(.warn));

    try std.testing.expectEqual(abi.PanicMode.abort, modeFromInteropPolicyByte(@intFromEnum(abi.PanicMode.abort)).?);
    try std.testing.expectEqual(abi.PanicMode.bug, modeFromInteropPolicyByte(@intFromEnum(abi.PanicMode.bug)).?);
    try std.testing.expectEqual(abi.PanicMode.warn, modeFromInteropPolicyByte(@intFromEnum(abi.PanicMode.warn)).?);
    try std.testing.expect(recognizesInteropPolicyByte(@intFromEnum(abi.PanicMode.warn)));
    try std.testing.expect(!recognizesInteropPolicyByte(9));
    try std.testing.expect(canReturnPolicyByte(@intFromEnum(abi.PanicMode.warn)));
    try std.testing.expect(!canReturnPolicyByte(@intFromEnum(abi.PanicMode.abort)));
    try std.testing.expect(!canReturnPolicyByte(9));
}
