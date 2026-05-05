const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");

test "atomic64 diff canonical wrapper keeps the shipped runtime gate wired in" {
    _ = runtime_atomic64_diff;
}
