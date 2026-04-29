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

pub fn modeFromInteropPolicyBytes(panic_mode: u8, reserved: u8) ?abi.PanicMode {
    if (reserved != 0) {
        return null;
    }
    return modeFromInteropPolicyByte(panic_mode);
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

pub fn recognizesInteropPolicyBytes(panic_mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(panic_mode, reserved) != null;
}

pub fn canReturn(mode: abi.PanicMode) bool {
    return actionFor(mode) == .warn_and_return;
}

pub fn canReturnPolicyBytes(panic_mode: u8, reserved: u8) bool {
    return canReturn(modeFromInteropPolicyBytes(panic_mode, reserved) orelse return false);
}

pub fn canReturnPolicyByte(panic_mode: u8) bool {
    return canReturnPolicyBytes(panic_mode, 0);
}

test "phase3 panic policy stays explicit" {
    try std.testing.expect(!canReturn(.abort));
    try std.testing.expect(!canReturn(.bug));
    try std.testing.expect(canReturn(.warn));

    try std.testing.expectEqual(abi.PanicMode.abort, modeFromInteropPolicyByte(@intFromEnum(abi.PanicMode.abort)).?);
    try std.testing.expectEqual(abi.PanicMode.bug, modeFromInteropPolicyByte(@intFromEnum(abi.PanicMode.bug)).?);
    try std.testing.expectEqual(abi.PanicMode.warn, modeFromInteropPolicyByte(@intFromEnum(abi.PanicMode.warn)).?);
    try std.testing.expect(recognizesInteropPolicyByte(@intFromEnum(abi.PanicMode.warn)));
    try std.testing.expect(!recognizesInteropPolicyByte(9));
    try std.testing.expectEqual(abi.PanicMode.warn, modeFromInteropPolicyBytes(@intFromEnum(abi.PanicMode.warn), 0).?);
    try std.testing.expect(recognizesInteropPolicyBytes(@intFromEnum(abi.PanicMode.warn), 0));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicyBytes(@intFromEnum(abi.PanicMode.warn), 1));
    try std.testing.expect(!recognizesInteropPolicyBytes(@intFromEnum(abi.PanicMode.warn), 1));
    try std.testing.expect(canReturnPolicyByte(@intFromEnum(abi.PanicMode.warn)));
    try std.testing.expect(!canReturnPolicyByte(@intFromEnum(abi.PanicMode.abort)));
    try std.testing.expect(!canReturnPolicyByte(9));
    try std.testing.expect(canReturnPolicyBytes(@intFromEnum(abi.PanicMode.warn), 0));
    try std.testing.expect(!canReturnPolicyBytes(@intFromEnum(abi.PanicMode.warn), 1));
}
