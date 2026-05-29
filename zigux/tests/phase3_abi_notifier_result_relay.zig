const std = @import("std");

const abi = @import("abi_bindings");
const notifier_abi = @import("notifier_abi");

fn expectResultRelay(raw: u32, expected: ?notifier_abi.NotifierResult) !void {
    try std.testing.expectEqual(expected, notifier_abi.resultFromInt(raw));
    try std.testing.expectEqual(expected, abi.notifierResultFromInt(raw));
    try std.testing.expectEqual(notifier_abi.resultIsKnown(raw), abi.notifierResultIsKnown(raw));
    try std.testing.expectEqual(notifier_abi.resultStopsChainValue(raw), abi.notifierResultStopsChainValue(raw));
}

test "phase3 abi notifier result relay preserves known values" {
    try std.testing.expectEqual(@as(u32, 0), abi.NOTIFIER_DONE);
    try std.testing.expectEqual(@as(u32, 1), abi.NOTIFIER_OK);
    try std.testing.expectEqual(@as(u32, 2), abi.NOTIFIER_STOP);

    try expectResultRelay(abi.NOTIFIER_DONE, .done);
    try expectResultRelay(abi.NOTIFIER_OK, .ok);
    try expectResultRelay(abi.NOTIFIER_STOP, .stop);
}

test "phase3 abi notifier result relay preserves stop semantics" {
    try std.testing.expect(!abi.notifierResultStopsChain(.done));
    try std.testing.expect(!abi.notifierResultStopsChain(.ok));
    try std.testing.expect(abi.notifierResultStopsChain(.stop));

    try std.testing.expectEqual(
        notifier_abi.resultStopsChain(.done),
        abi.notifierResultStopsChain(.done),
    );
    try std.testing.expectEqual(
        notifier_abi.resultStopsChain(.ok),
        abi.notifierResultStopsChain(.ok),
    );
    try std.testing.expectEqual(
        notifier_abi.resultStopsChain(.stop),
        abi.notifierResultStopsChain(.stop),
    );
}

test "phase3 abi notifier result relay rejects unknown raw values" {
    try expectResultRelay(3, null);
    try expectResultRelay(std.math.maxInt(u32), null);
}
