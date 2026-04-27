const std = @import("std");
const abi = @import("abi_bindings");

pub const InitFlow = enum {
    caller_prepared,
    helper_owned,
    helper_owned_with_reset,
};

pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {
    return switch (mode) {
        .caller_provided => .caller_prepared,
        .kernel_heap => .helper_owned,
        .arena => .helper_owned_with_reset,
    };
}

pub fn requiresExplicitCaller(mode: abi.AllocatorMode) bool {
    return initFlowFor(mode) == .caller_prepared;
}

pub fn permitsGlobalFallback(mode: abi.AllocatorMode) bool {
    return switch (initFlowFor(mode)) {
        .caller_prepared => false,
        .helper_owned, .helper_owned_with_reset => true,
    };
}

pub fn initializesOwnedState(mode: abi.AllocatorMode) bool {
    return switch (initFlowFor(mode)) {
        .caller_prepared => false,
        .helper_owned, .helper_owned_with_reset => true,
    };
}

pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {
    return initFlowFor(mode) == .helper_owned_with_reset;
}

test "phase3 allocator policy stays explicit" {
    try std.testing.expectEqual(InitFlow.caller_prepared, initFlowFor(.caller_provided));
    try std.testing.expectEqual(InitFlow.helper_owned, initFlowFor(.kernel_heap));
    try std.testing.expectEqual(InitFlow.helper_owned_with_reset, initFlowFor(.arena));

    try std.testing.expect(requiresExplicitCaller(.caller_provided));
    try std.testing.expect(!permitsGlobalFallback(.caller_provided));
    try std.testing.expect(!initializesOwnedState(.caller_provided));
    try std.testing.expect(!requiresResetOnInit(.caller_provided));

    try std.testing.expect(permitsGlobalFallback(.kernel_heap));
    try std.testing.expect(initializesOwnedState(.kernel_heap));
    try std.testing.expect(!requiresResetOnInit(.kernel_heap));

    try std.testing.expect(permitsGlobalFallback(.arena));
    try std.testing.expect(initializesOwnedState(.arena));
    try std.testing.expect(requiresResetOnInit(.arena));
}
