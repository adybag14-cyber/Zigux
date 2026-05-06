const std = @import("std");
const abi = @import("abi_bindings");

pub const Action = enum {
    abort_now,
    bug_check,
    warn_and_return,
};

pub fn modeFromByte(mode: u8) ?abi.PanicMode {
    return switch (mode) {
        @intFromEnum(abi.PanicMode.abort) => .abort,
        @intFromEnum(abi.PanicMode.bug) => .bug,
        @intFromEnum(abi.PanicMode.warn) => .warn,
        else => null,
    };
}

pub fn actionFor(mode: abi.PanicMode) Action {
    return switch (mode) {
        .abort => .abort_now,
        .bug => .bug_check,
        .warn => .warn_and_return,
    };
}

pub fn actionForByte(mode: u8) ?Action {
    return actionFor(modeFromByte(mode) orelse return null);
}

pub fn canReturn(mode: abi.PanicMode) bool {
    return actionFor(mode) == .warn_and_return;
}

pub fn canReturnByte(mode: u8) bool {
    return actionForByte(mode) == .warn_and_return;
}

test "phase3 panic policy stays explicit" {
    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromByte(9));

    try std.testing.expectEqual(@as(?Action, .abort_now), actionForByte(0));
    try std.testing.expectEqual(@as(?Action, .bug_check), actionForByte(1));
    try std.testing.expectEqual(@as(?Action, .warn_and_return), actionForByte(2));
    try std.testing.expectEqual(@as(?Action, null), actionForByte(9));

    try std.testing.expect(!canReturn(.abort));
    try std.testing.expect(!canReturn(.bug));
    try std.testing.expect(canReturn(.warn));
    try std.testing.expect(!canReturnByte(0));
    try std.testing.expect(!canReturnByte(1));
    try std.testing.expect(canReturnByte(2));
    try std.testing.expect(!canReturnByte(9));
}
