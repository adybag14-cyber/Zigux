const std = @import("std");
const atomic = @import("atomic");

pub const RmwOperation = atomic.RmwOperation;
pub const RmwOperationFamily = atomic.RmwOperationFamily;

pub const RmwOperationProfile = struct {
    operation: RmwOperation,
    family: RmwOperationFamily,
    is_exchange: bool,
};

pub fn profile(operation: RmwOperation) RmwOperationProfile {
    const family = atomic.rmwOperationFamily(operation);
    return .{
        .operation = operation,
        .family = family,
        .is_exchange = family == .exchange,
    };
}

pub fn rmwOperationIsExchange(operation: RmwOperation) bool {
    return profile(operation).is_exchange;
}

pub fn rmwOperationFamily(operation: RmwOperation) RmwOperationFamily {
    return profile(operation).family;
}

test "phase3 atomic RMW family helper exposes exchange classification" {
    const exchange_profile = profile(.exchange);

    try std.testing.expectEqual(RmwOperation.exchange, exchange_profile.operation);
    try std.testing.expectEqual(RmwOperationFamily.exchange, exchange_profile.family);
    try std.testing.expect(exchange_profile.is_exchange);
    try std.testing.expect(rmwOperationIsExchange(.exchange));

    try std.testing.expect(!rmwOperationIsExchange(.add));
    try std.testing.expect(!rmwOperationIsExchange(.xor));
    try std.testing.expect(!rmwOperationIsExchange(.max));
}

test "phase3 atomic RMW family helper mirrors the canonical atomic classifier" {
    const operations = [_]RmwOperation{
        .exchange,
        .add,
        .sub,
        .nand,
        .@"or",
        .@"and",
        .xor,
        .min,
        .max,
    };

    for (operations) |operation| {
        const classification = profile(operation);
        try std.testing.expectEqual(operation, classification.operation);
        try std.testing.expectEqual(atomic.rmwOperationFamily(operation), classification.family);
        try std.testing.expectEqual(classification.family == .exchange, classification.is_exchange);
        try std.testing.expectEqual(atomic.rmwOperationFamily(operation), rmwOperationFamily(operation));
    }
}

test "phase3 atomic RMW family helper keeps non-exchange family predicates separate" {
    try std.testing.expect(atomic.rmwOperationIsArithmetic(.add));
    try std.testing.expect(atomic.rmwOperationIsArithmetic(.sub));
    try std.testing.expect(!rmwOperationIsExchange(.add));
    try std.testing.expect(!rmwOperationIsExchange(.sub));

    try std.testing.expect(atomic.rmwOperationIsBitwise(.nand));
    try std.testing.expect(atomic.rmwOperationIsBitwise(.xor));
    try std.testing.expect(!rmwOperationIsExchange(.nand));
    try std.testing.expect(!rmwOperationIsExchange(.xor));

    try std.testing.expect(atomic.rmwOperationIsExtrema(.min));
    try std.testing.expect(atomic.rmwOperationIsExtrema(.max));
    try std.testing.expect(!rmwOperationIsExchange(.min));
    try std.testing.expect(!rmwOperationIsExchange(.max));
}
