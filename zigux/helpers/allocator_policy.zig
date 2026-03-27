const std = @import("std");
const abi = @import("abi_bindings");

pub fn requiresExplicitCaller(mode: abi.AllocatorMode) bool {
    return mode == .caller_provided;
}

pub fn permitsGlobalFallback(mode: abi.AllocatorMode) bool {
    return switch (mode) {
        .caller_provided => false,
        .kernel_heap, .arena => true,
    };
}

test "phase3 allocator policy stays explicit" {
    try std.testing.expect(requiresExplicitCaller(.caller_provided));
    try std.testing.expect(!permitsGlobalFallback(.caller_provided));
    try std.testing.expect(permitsGlobalFallback(.kernel_heap));
    try std.testing.expect(permitsGlobalFallback(.arena));
}
