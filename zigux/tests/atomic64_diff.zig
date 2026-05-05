const std = @import("std");
const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");
const runtime_atomic64_diff_source = @embedFile("runtime_atomic64_diff.zig");

fn expectRuntimeMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, runtime_atomic64_diff_source, marker) != null);
}

test "atomic64 diff canonical wrapper keeps the shipped runtime gate wired in" {
    _ = runtime_atomic64_diff;
}

test "atomic64 diff wrapper records the current bounded runtime checks" {
    try expectRuntimeMarker(
        "runtime atomic64 diff gate replays bounded atomic64_test.c exchange, cmpxchg, and add_unless expectations",
    );
    try expectRuntimeMarker(
        "v0 to v1 keeps the original counter visible as the exchange return value",
    );
    try expectRuntimeMarker(
        "v1 to v2 keeps wide negative and positive 64-bit values distinct",
    );
    try expectRuntimeMarker(
        "high-bit starter from atomic64_test.c still round-trips through exchange",
    );
    try expectRuntimeMarker(
        "cmpxchg success path stores the desired value when the expected value matches",
    );
    try expectRuntimeMarker("cmpxchg mismatch keeps the original value visible");
    try expectRuntimeMarker(
        "add_unless leaves the counter untouched when it already matches the blocked value",
    );
    try expectRuntimeMarker(
        "add_unless applies the addend when the current value differs from the blocked value",
    );
    try expectRuntimeMarker("runtime atomic64 diff gate keeps selftest family coverage explicit");
}
