const std = @import("std");

const abi = @import("abi_bindings");

fn expectKnownResult(raw: u32, expected: abi.NotifierResult) !void {
    try std.testing.expectEqual(@as(?abi.NotifierResult, expected), abi.notifierResultFromInt(raw));
    try std.testing.expect(abi.notifierResultIsKnown(raw));
    try std.testing.expectEqual(@intFromEnum(expected), raw);
}

test "phase3 notifier result ABI constants stay byte stable" {
    try std.testing.expectEqual(@as(u32, 0), abi.NOTIFIER_DONE);
    try std.testing.expectEqual(@as(u32, 1), abi.NOTIFIER_OK);
    try std.testing.expectEqual(@as(u32, 2), abi.NOTIFIER_STOP);
    try std.testing.expectEqual(abi.NOTIFIER_DONE, @intFromEnum(abi.NotifierResult.done));
    try std.testing.expectEqual(abi.NOTIFIER_OK, @intFromEnum(abi.NotifierResult.ok));
    try std.testing.expectEqual(abi.NOTIFIER_STOP, @intFromEnum(abi.NotifierResult.stop));
}

test "phase3 notifier result decoding is closed over published values" {
    try expectKnownResult(abi.NOTIFIER_DONE, .done);
    try expectKnownResult(abi.NOTIFIER_OK, .ok);
    try expectKnownResult(abi.NOTIFIER_STOP, .stop);

    try std.testing.expectEqual(@as(?abi.NotifierResult, null), abi.notifierResultFromInt(3));
    try std.testing.expectEqual(@as(?abi.NotifierResult, null), abi.notifierResultFromInt(std.math.maxInt(u32)));
    try std.testing.expect(!abi.notifierResultIsKnown(3));
    try std.testing.expect(!abi.notifierResultIsKnown(std.math.maxInt(u32)));
}

test "phase3 notifier result stop semantics fail closed for unknown values" {
    try std.testing.expect(!abi.notifierResultStopsChain(.done));
    try std.testing.expect(!abi.notifierResultStopsChain(.ok));
    try std.testing.expect(abi.notifierResultStopsChain(.stop));
    try std.testing.expect(!abi.notifierResultStopsChainValue(abi.NOTIFIER_DONE));
    try std.testing.expect(!abi.notifierResultStopsChainValue(abi.NOTIFIER_OK));
    try std.testing.expect(abi.notifierResultStopsChainValue(abi.NOTIFIER_STOP));
    try std.testing.expect(!abi.notifierResultStopsChainValue(3));
    try std.testing.expect(!abi.notifierResultStopsChainValue(std.math.maxInt(u32)));
}
