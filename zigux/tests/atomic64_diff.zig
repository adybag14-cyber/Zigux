const std = @import("std");
const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");
const runtime_atomic64_diff_source = @embedFile("runtime_atomic64_diff.zig");

comptime {
    _ = runtime_atomic64_diff;
}

test "atomic64 diff wrapper keeps the bounded runtime replay body reachable" {
    try std.testing.expect(std.mem.indexOf(
        u8,
        runtime_atomic64_diff_source,
        "runtime atomic64 diff gate replays bounded atomic64_test.c",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        runtime_atomic64_diff_source,
        "runtime atomic64 diff gate keeps post-selftest replay explicit",
    ) != null);
}
