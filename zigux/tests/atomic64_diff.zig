const std = @import("std");
const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");
const runtime_atomic64_diff_source = @embedFile("runtime_atomic64_diff.zig");

comptime {
    _ = runtime_atomic64_diff;
}

fn expectRuntimeMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, runtime_atomic64_diff_source, marker) != null);
}

test "atomic64 diff wrapper keeps the bounded runtime replay body reachable" {
    try expectRuntimeMarker("runtime atomic64 diff gate replays bounded atomic64_test.c");
    try expectRuntimeMarker("runtime atomic64 diff gate keeps selftest family coverage explicit");
    try expectRuntimeMarker("runtime atomic64 diff gate keeps post-selftest replay explicit");
}

test "atomic64 diff wrapper records the exact bounded runtime atomic64 checks" {
    try expectRuntimeMarker("add grows the starter counter by the onestwos constant from atomic64_test.c");
    try expectRuntimeMarker("add accepts the negative one decrement path from atomic64_test.c");
    try expectRuntimeMarker("sub matches the wide onestwos decrement from atomic64_test.c");
    try expectRuntimeMarker("sub accepts the negative one increment path from atomic64_test.c");

    try expectRuntimeMarker("or matches the v0|v1 family from atomic64_test.c");
    try expectRuntimeMarker("and matches the v0&v1 family from atomic64_test.c");
    try expectRuntimeMarker("xor matches the v0^v1 family from atomic64_test.c");
    try expectRuntimeMarker("andnot matches the v0&~v1 family from atomic64_test.c");

    try expectRuntimeMarker("v0 to v1 keeps the original counter visible as the exchange return value");
    try expectRuntimeMarker("v1 to v2 keeps wide negative and positive 64-bit values distinct");
    try expectRuntimeMarker("high-bit starter from atomic64_test.c still round-trips through exchange");
    try expectRuntimeMarker("cmpxchg success path stores the desired value when the expected value matches");
    try expectRuntimeMarker("cmpxchg mismatch keeps the original value visible");

    try expectRuntimeMarker("add_unless leaves the counter untouched when it already matches the blocked value");
    try expectRuntimeMarker("add_unless applies the addend when the current value differs from the blocked value");
    try expectRuntimeMarker("inc_not_zero increments a positive non-zero counter");
    try expectRuntimeMarker("inc_not_zero leaves zero unchanged");
    try expectRuntimeMarker("inc_not_zero still increments -1 back to zero");
    try expectRuntimeMarker("inc_not_zero keeps the high-bit atomic64_test.c sentinel nonzero while incrementing it");
    try expectRuntimeMarker("dec_if_positive decrements a positive counter and returns the decremented value");
    try expectRuntimeMarker("dec_if_positive returns -1 for zero without changing storage");
    try expectRuntimeMarker("dec_if_positive returns seed minus one for negative inputs without storing it");

    try expectRuntimeMarker("checked_returning_paths");
    try expectRuntimeMarker("checked_guard_paths");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.incNotZeroCounter()");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.decIfPositiveCounter()");
}
